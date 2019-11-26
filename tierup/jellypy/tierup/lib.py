import datetime
import pkg_resources

from jellypy.tierup.irtools import IRJson
from jellypy.tierup.panelapp import PanelApp

class ReportEvent():
    def __init__(self, event, variant):
        self.data = event
        self.variant = variant
        self.gene = self.get_gene()
        self.panel = self.data['genePanel']['panelName']

    def get_gene(self):
        all_genes = [ entity['geneSymbol'] 
            for entity in self.data['genomicEntities']
            if entity['type'] == 'gene'
        ]
        assert len(all_genes) == 1, 'More than one report event entity of type gene'
        return all_genes.pop()

class PanelUpdater():
    # Report events describe their panels by "Name" and "version".
    # The interpretation_request_data describes the panels applied to the interpretation request by hash id.
    #    Panel names can change over time, therefore pulling panel data by hash may return a panel with a name
    #    that does not match the names in the report event. This class takes an irjson object, which has its
    #    interpretation_request_data panel names. It pulls panel names from all report events. Any names that 
    #    are missing are searched for in the gel API and the IRJ object is updated.
    ## Scenario: IRJson hash is outdated?
    def __init__(self):
        pass

    def add_event_panels(self, irjo):
        missing_panels = self._find_missing_event_panels(irjo)
        panels_to_add = self._search_panelapp(missing_panels)
        for name, identifier in panels_to_add:
            irjo.update_panel(name, identifier)

    def _search_panelapp(self, missing_panels):
        oldname_id = []
        # for panel in panel app;
        pa = PanelApp()
        for gel_panel in pa:
           for panel_name in missing_panels:
               if panel_name in gel_panel['relevant_disorders']:
                   # Note assumption: All panel names have one ID matching in panel app
                   oldname_id.append((panel_name, gel_panel['id']))
        return oldname_id

    def _find_missing_event_panels(self, irjo):
        # Get all panel names from report events and filter those that are not
        # the name of any of the interpretation request panels today.
        event_panels = {
            event['genePanel']['panelName']
            for variant_data in irjo.tiering['interpreted_genome_data']['variants']
            for event in variant_data['reportEvents']
        }
        ir_panels = set(irjo.panels.keys())
        return event_panels - ir_panels

class TierUpReporter():

    def __init__(self, irjo):
        self.irjo = irjo

    def generate_events(self):
        for variant in self.irjo.tiering['interpreted_genome_data']['variants']:
            for event in variant['reportEvents']:
                if event['tier'] == 'TIER3':
                    yield ReportEvent(event, variant)

    def query_panel_app(self, gene, panel):
        """Get the hgnc id and confidence level for a gene from the panelapp API.
        Args:
            gene: A gene symbol
            panel: A GeLPanel object
        Returns:
            event_hgnc_confidence_panel (Tuple): A tuple containing four elements:
                [0] `gene` from args
                [1] the hgnc id from panel app. None if not found
                [2] the confidence level from panel app. None if not found
                [3] `panel` from args
        """
        try:
            all_genes = panel.get_gene_map()
            hgnc, confidence = all_genes[gene]
            return gene, hgnc, confidence, panel
        except KeyError:
            # The gene does not map to a panelapp_symbol because either:
            # - gene symbol has changed over time
            # - the gene has been dropped from the panel 
            return gene, None, None, panel

    def tierup_record(self, event, hgnc, confidence, panel):
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
