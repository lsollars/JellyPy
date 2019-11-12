import datetime
import pkg_resources

def generate_events(irjo):
    variant_events = (
        ReportEvent(event, variant) for variant in irjo.tiering['interpreted_genome_data']['variants']
        for event in variant['reportEvents']
        if event['tier'] == 'TIER3')
    return variant_events

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

class EventPanelMatcher():

    def __init__(self, event: ReportEvent, irjo):
        self.event = event
        self.irjo = irjo
        self.check_panels()

    def check_panels(self):
        """Raise an error if the report event panel is not in the panels known for the interpretation request"""
        if self.event.panel not in self.irjo.panels:
            raise ValueError(f"{self.event.panel} not in {self.irjo.panels.keys()}")
    
    def query_panel_app(self):
        """Get the current hgnc id and confidence level for the report event gene from the panelapp API.
        Returns:
            event_hgnc_confidence_panel (Tuple): A tuple containing four elements:
                [0] the gene in the report event
                [1] the hgnc id from panel app. None if not found
                [2] the confidence level from panel app. None if not found
                [3] A jellypy.tierup.panelapp.GeLPanel object for the report event panel
        """
        # Get the panel app object for the event panel. We need this to query panel app for the latest
        # panel/gene information.
        panel = self.irjo.panels[self.event.panel]
        try:
            # Query panelapp. Dictionary returned maps panelapp_gene:(panelapp_hgnc, panelapp_confidence).
            gene_map = panel.get_gene_map()
            hgnc, confidence = gene_map[self.event.gene]
            return self.event.gene, hgnc, confidence, panel
        except KeyError:
            # The event.gene does not map to panelapp_gene because either:
            # - gene symbol has changed over time
            # - the gene has been dropped from the panel 
            return self.event.gene, None, None, panel

def build_tierup_report(irjo, extra_panels = None):
    for event in generate_events(irjo):
        em = EventPanelMatcher(event, irjo)
        event_gene, hgnc, confidence, panel = em.query_panel_app()
        tierup_report = {
            'justification': event.data['eventJustification'],
            'consequences': str([ cons['name'] for cons in event.data['variantConsequences'] ]),
            'penetrance': event.data['penetrance'],
            'denovo_score': event.data['deNovoQualityScore'],
            'score': event.data['score'],
            'event_id': event.data['reportEventId'],
            'interpretation_request_id': irjo.tiering['interpreted_genome_data']['interpretationRequestId'],
            'gel_tiering_version' : None, #TODO: Extract tiering version from softwareVersions key
            'created_at': irjo.tiering['created_at'],
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
            're_gene': event_gene,
            'tu_version': pkg_resources.require("jellypy-tierup")[0].version,
            'tu_panel_hash': panel.hash,
            'tu_panel_name': panel.name,
            'tu_panel_version': panel.version,
            'tu_panel_number': panel.id,
            'tu_panel_created': panel.created,
            'tu_hgnc_id': "No TU HGNC Search",
            'pa_hgnc_id': hgnc,
            'pa_gene': event_gene,
            'pa_confidence': confidence,
            'tu_comment': "No comment implemented",
            'software_versions': str(irjo.tiering['interpreted_genome_data']['softwareVersions']),
            'reference_db_versions': str(irjo.tiering['interpreted_genome_data']['referenceDatabasesVersions']),
            'extra_panels': extra_panels,
            'tu_run_time': datetime.datetime.now().strftime('%c')
        }
        tierup_report.update(irjo.tier_counts)
        yield tierup_report
