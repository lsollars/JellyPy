
def generate_events(irjo):
    variant_events = (
        (variant, ReportEvent(event)) for variant in irjo.tiering['interpreted_genome_data']['variants']
        for event in variant['reportEvents']
        if event['tier'] == 'TIER3')
    return variant_events

class ReportEvent():
    def __init__(self, event):
        self.data = event
        self.gene = self.get_gene()
        self.panel = self.data['genePanel']['panelName']

    def get_gene(self):
        all_genes = [ entity['geneSymbol'] 
            for entity in self.data['genomicEntities']
            if entity['type'] == 'gene'
        ]
        assert len(all_genes) == 1, 'More than one report event entity of type gene'
        return all_genes.pop()

class EventManager():

    def __init__(self, event: ReportEvent, irjo):
        self.event = event
        self.irjo = irjo
        self.check_panels()

    def check_panels(self):
        if self.event.panel not in self.irjo.panels:
            raise ValueError(f"{self.event.panel} not in {self.irjo.panels.keys()}")
    
    def query_panel_app(self):
        panel = self.irjo.panels[self.event.panel]
        try:
            gene_map = panel.get_gene_map()
            hgnc, confidence = gene_map[self.event.gene]
            return self.event.gene, hgnc, confidence, panel
        except KeyError:
            return self.event.gene, None, None, panel
