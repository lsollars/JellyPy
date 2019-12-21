"""Utilities for handling interpretation request data."""
from collections import Counter
import json
import pathlib
import re

import jellypy.pyCIPAPI.interpretation_requests as irs
import jellypy.tierup.panelapp as pa
from jellypy.pyCIPAPI.auth import AuthenticatedCIPAPISession

from protocols.util.dependency_manager import VERSION_500
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.reports_6_0_1 import InterpretedGenome

class IRJIO():
    def __init__(self):
        pass


    def get(self, irid: int, irversion: int, session: AuthenticatedCIPAPISession) -> dict:
        """Get an interpretation request json from the CPIAPI using jellpy.pyCIPAPI library
        Args:
            irid: Interpretation request id
            irv: Interpretation request version
            session: An authenticated CIPAPI session (pyCIPAPI)
        Returns:
            json_response: A dictionary containing the interpretation request response
        """
        json_response = irs.get_interpretation_request_json(irid, irversion, reports_v6=True, session=session)
        return json_response

    def read(self, filepath: str):
        """Read IRJ json from disk"""
        with open(filepath, 'r') as f:
            return IRJson(json.load(f))

    def save(self, irjson: IRJson, filepath: str = None):
        """Save IRJson to disk"""
        _fp = filepath or irjson.irid + '.json'
        with open(_fp, 'w') as f:
            json.dump(irjson.json, f)

class IRJValidator():
    """Interpretation request Json V6. Utility methods for interacting with data structure."""
    
    def __init__(self):
        pass
    
    def validate(self, irjson):
        is_v6 = self.is_v6(irjson)
        is_sent = self.is_sent(irjson)
        is_unsolved = self.is_unsolved(irjson)

        if is_v6 and is_sent and is_unsolved:
            pass
        else:
            raise IOError(f'Invalid interpretation request JSON: '
            f'is_v6:{is_v6}, is_sent:{is_sent}, is_unsolved:{is_unsolved}')

    def is_v6(self, irjson):
        """Returns true if the interpreted genome of an irjson is GeL v6 model.
        Despite using the report_v6 argument, older interpretation requests are not returned with this schema."""
        try:
            irj_genome = irjson['interpreted_genome'][0]['interpreted_genome_data']
        except KeyError:
            return False
        ir_factory = GenericFactoryAvro.get_factory_avro(InterpretedGenome, version=VERSION_500)
        ir_factory_instance = ir_factory()
        return ir_factory_instance.validate(irj_genome)

    def is_sent(self, irjson):
        """Returns true if the irjson has been submitted to the interpretation portal by GeL.
        Requests are given this status once all QC checks are passed and decision support service
        has processed data.
        """
        is_sent = 'sent_to_gmcs' in [item['status'] for item in irjson['status']]
        return is_sent
    
    def is_unsolved(self, irjson):
        """Returns True if no reports have been issued where the case has been solved."""
        # If a report has not been issued, the clinical_report field will be an empty list. Return True.
        if irjson['clinical_report'] == []:
            return True

        reports = irjson['clinical_report']
        reports_with_questionnaire = [ report for report in reports if report['exit_questionnaire'] is not None ]
        reports_solved = [ report for report in reports_with_questionnaire if report[
            'exit_questionnaire']['exit_questionnaire_data']['familyLevelQuestions']['caseSolvedFamily'
            ] == "yes"
        ]
        if any(reports_solved):
            return False
        else:
            return True

class IRJson():
    """Utilities for parsing IRJson data"""

    def __init__(self, irjson, validator=IRJValidator):
        validator().validate(irjson)
        self.json = irjson
        self.tiering = self._get_tiering()
        self.tier_counts = self._get_tiering_counts()
        self.panels = self._get_panels()
        self.updated_panels = []

    def _get_tiering(self):
        tiering_list = list(
            filter(
                lambda x: x['interpreted_genome_data']['interpretationService'] == 'genomics_england_tiering',
                self.json['interpreted_genome']
            )
        )
        # TODO: Although the interpreted genome is in an array, we are yet to encounter a request with more than one
        # run of the genomics england tiering pipeline. Regardless, this is a temporary failsafe and we would rather
        # select the latest one.
        assert len(tiering_list) == 1, "0 or >1 gel tiering interpretation found"
        return tiering_list.pop()
    
    def _get_panels(self):
        _panels = {}
        data = self.json['interpretation_request_data']['json_request']['pedigree']['analysisPanels']
        for item in data:
            try:
                panel = pa.GeLPanel(item['panelName'])
                _panels[panel.name] = panel
            except requests.HTTPError:
                print(f'Warning. No PanelApp API reponse for {item["panelName"]}')
        return _panels

    def _get_tiering_counts(self):
        """Count variants in each tiering band for a gel tiering interpreted genome"""
        tier_counts = dict.fromkeys(['TIER1','TIER2','TIER3'], 0)
        tiers = [ event['tier']
            for data in self.tiering['interpreted_genome_data']['variants']
            for event in data['reportEvents']
        ]
        tier_counts.update(Counter(tiers))
        return tier_counts

    def update_panel(self, panel_name, panel_id):
        """Add or update a panel name using an ID from the PanelApp API"""
        new_panel = pa.GeLPanel(panel_id)
        self.panels[panel_name] = new_panel
        self.updated_panels.append(f"{panel_name}, {panel_id}")

    @property
    def irid(self):
        irid_full = self.tiering['interpreted_genome_data']['interpretationRequestId']
        irid_digits = re.search('\d+-\d+', irid_full).group(0)
        return irid_digits
