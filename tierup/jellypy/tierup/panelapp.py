"""Utilities for working with PanelApp"""

import requests

class GeLPanel():
    """A GeL PanelApp Panel.
    
    """
    host = "https://panelapp.genomicsengland.co.uk/api/v1/panels"
    
    def __init__(self, panel, version=None):
        self.url = f'{self.host}/{panel}'
        self.version = float(version) if version else None
        self._json = self._get_panel_json()

        # Initialise attributes
        self.name, self.id, self.hash = self._json['name'], self._json['id'], self._json['hash_id']
        self.created = self._json['version_created']
        self.version = float(self._json['version'])
        
    def get_gene_map(self):
        mapping = { gene['gene_data']['hgnc_symbol']: (gene['gene_data']['hgnc_id'], gene['confidence_level'])
            for gene in self._json['genes']
        }
        return mapping

    def _get_panel_json(self):
        """Returns json response object for API request."""
        data = requests.get(self.url, params={"version" : self.version})
        data.raise_for_status() # Raise error if invalid response code
        return data.json()

    def __str__(self):
        return f"{self.name}, {self.id}"
