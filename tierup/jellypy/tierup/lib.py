import datetime
import pkg_resources
import json
import logging
import csv

from typing import Iterable

from jellypy.tierup.irtools import IRJson, IRJIO
from jellypy.tierup.panelapp import PanelApp

logger = logging.getLogger(__name__)


class ReportEvent():
    """Represents a tiering report event.
    Args:
        event: A report event from the irjson tiering section
        variant: The variant under which the report event is nested in the irjson
    Attributes:
        data: Report event passed to class constructor
        variant: Variant passed to class constructor
        gene: The gene symbol for the tiered report event variant
        panelname: The panel name relevant to the report event variant
    """
    def __init__(self, event, variant):
        self.data = event
        self.variant = variant
        self.gene = self._get_gene()
        self.panelname = self.data['genePanel']['panelName']

    def _get_gene(self):
        all_genes = [ entity['geneSymbol'] 
            for entity in self.data['genomicEntities']
            if entity['type'] == 'gene'
        ]
        assert len(all_genes) == 1, 'More than one report event entity of type gene'
        return all_genes.pop()

class PanelUpdater():
    """Update panel IDs in IRJson object panels.
    
    Panels applied when tier 3 variants were reported may have different PanelApp IDs today.
    This class searches PanelApp to update panel identifiers where necessary.
    """
    def __init__(self):
        pass

    def add_event_panels(self, irjo: IRJson) -> None:
        """Add new panel identifiers to IRJson objects where panels have been merged.
        This updates the ID of renamed or merged panels, ensuring the accurate current panel is returned
        from any downstream PanelApp API calls.

        Args:
            irjo: An interpretation request json object
        """
        missing_panels = self._find_missing_event_panels(irjo)
        panels_to_add = self._search_panelapp(missing_panels)
        for name, identifier in panels_to_add:
            irjo.update_panel(name, identifier)

    def _search_panelapp(self, missing_panels) -> list:
        """Search the relevant disorders section of panelapp for given panel names.
    
        Args:
            missing_panels: Panel names to find in panelapp.
        Returns:
            List[Tuple]: A list of tuples containing the panel name and relevant ID.
        """
        oldname_id = []
        # for panel in panel app;
        pa = PanelApp()
        for gel_panel in pa:
           for panel_name in missing_panels:
               if panel_name in gel_panel['relevant_disorders']:
                   # Note assumption: All panel names have one ID matching in panel app
                   oldname_id.append((panel_name, gel_panel['id']))
        return oldname_id

    def _find_missing_event_panels(self, irjo) -> set:
        """Panel names reported with tiered variants and remove those 
        missing from the top-level of the interpretation request today.

        Args:
            irjo: An interpretation request json object
        Returns:
            A set of panel names missing from the top-level of the interpretation request. These names
                have likely been updated and filed uner a new panel ID.
        """
        event_panels = {
            event['genePanel']['panelName']
            for variant_data in irjo.tiering['interpreted_genome_data']['variants']
            for event in variant_data['reportEvents']
        }
        ir_panels = set(irjo.panels.keys())
        return event_panels - ir_panels

class TierUpRunner():
    """Run TierUp on an interpretation request json object

    Args:
        irjo: Interpretation request json object
    """

    def __init__(self, irjo:IRJson):
        self.irjo = irjo

    def run(self):
        """Run tierup algorithm

        Returns:
            Generator containing tierup CSV results for each tier 3 variant
        """
        tier_three_events = self._generate_events()
        for event in tier_three_events:
            panel = self.irjo.panels[event.panelname]
            hgnc, conf = self.query_panel_app(event.gene, panel)
            record = self._tierup_record(event, hgnc, conf, panel)
            yield record

    def _generate_events(self):
        for variant in self.irjo.tiering['interpreted_genome_data']['variants']:
            for event in variant['reportEvents']:
                if event['tier'] == 'TIER3':
                    yield ReportEvent(event, variant)

    def query_panel_app(self, gene: str, panel):
        """Get the hgnc id and confidence level for a gene from the panelapp API.
        
        Args:
            gene: A gene symbol
            panel: A GeLPanel object
        Returns:
            A tuple containing four elements:
                - [0] `gene` from args
                - [1] the hgnc id from panel app. None if not found
                - [2] the confidence level from panel app. None if not found
                - [3] `panel` from args
        """
        try:
            all_genes = panel.get_gene_map()
            hgnc, confidence = all_genes[gene]
            return hgnc, confidence
        except KeyError:
            # The gene does not map to a panelapp_symbol because either:
            # - gene symbol has changed over time
            # - the gene has been dropped from the panel 
            return None, None

    def _tierup_record(self, event, hgnc, confidence, panel):
        record = {
            'justification': event.data['eventJustification'],
            'consequences': str([ cons['name'] for cons in event.data['variantConsequences'] ]),
            'penetrance': event.data['penetrance'],
            'denovo_score': event.data['deNovoQualityScore'],
            'score': event.data['score'],
            'event_id': event.data['reportEventId'],
            'interpretation_request_id': self.irjo.tiering['interpreted_genome_data']['interpretationRequestId'],
            'gel_tiering_version' : None, #TODO: Extract tiering version from softwareVersions key
            'created_at': self.irjo.tiering['created_at'],
            'tier': event.data['tier'],
            'segregation': event.data['segregationPattern'],
            'inheritance': event.data['modeOfInheritance'],
            'group': event.data['groupOfVariants'],
            'zygosity': event.variant['variantCalls'][0]['zygosity'], #TODO: GET THE PARTICIPANT'S CALL
            'participant_id': 10000, #TODO: Get from IRJ
            'position': event.variant['variantCoordinates']['position'],
            'chromosome': event.variant['variantCoordinates']['chromosome'],
            'assembly': event.variant['variantCoordinates']['assembly'],
            'reference': event.variant['variantCoordinates']['reference'],
            'alternate': event.variant['variantCoordinates']['alternate'],
            're_panel_id': event.data['genePanel']['panelIdentifier'],
            're_panel_version': event.data['genePanel']['panelVersion'],
            're_panel_source': event.data['genePanel']['source'],
            're_panel_name': event.data['genePanel']['panelName'],
            're_gene': event.gene,
            'tu_version': pkg_resources.require("jellypy-tierup")[0].version,
            'tu_panel_hash': panel.hash,
            'tu_panel_name': panel.name,
            'tu_panel_version': panel.version,
            'tu_panel_number': panel.id,
            'tu_panel_created': panel.created,
            'tu_hgnc_id': "No TU HGNC Search",
            'pa_hgnc_id': hgnc,
            'pa_gene': event.gene,
            'pa_confidence': confidence,
            'tu_comment': "No comment implemented",
            'software_versions': str(self.irjo.tiering['interpreted_genome_data']['softwareVersions']),
            'reference_db_versions': str(self.irjo.tiering['interpreted_genome_data']['referenceDatabasesVersions']),
            'extra_panels': self.irjo.updated_panels,
            'tu_run_time': datetime.datetime.now().strftime('%c'),
            'tier1_count': self.irjo.tier_counts['TIER1'],
            'tier2_count': self.irjo.tier_counts['TIER2'],
            'tier3_count': self.irjo.tier_counts['TIER3']
        }
        return record

class TierUpWriter():
    def __init__(self, outfile, schema, writer=csv.DictWriter):
        self.outstream = open(outfile, 'w')
        self.header = json.loads(schema)['required']
        self.writer = writer(self.outstream, fieldnames=self.header, delimiter="\t")   

    def write(self, data):
        """Write data to csv output file"""
        self.writer.writerow(data)
    
    def close_file(self):
        """Close csv output file"""
        self.outstream.close()

class TierUpCSVWriter(TierUpWriter):

    schema = pkg_resources.resource_string('jellypy.tierup', 'data/report.schema')

    def __init__(self, *args, **kwargs):
        super(TierUpCSVWriter, self).__init__(*args, schema=self.schema, **kwargs)
        self.writer.writeheader()

class TierUpSummaryWriter(TierUpWriter):

    schema = pkg_resources.resource_string('jellypy.tierup', 'data/summary_report.schema')

    def __init__(self, *args, **kwargs):
        super(TierUpSummaryWriter, self).__init__(*args, schema=self.schema, **kwargs)

    def write(self, data):
        if data['pa_confidence'] and data['pa_confidence'] in ['3','4']:
            filtered = { k:v for k,v in data.items() if k in self.header }
            self.writer.writerow(filtered)
