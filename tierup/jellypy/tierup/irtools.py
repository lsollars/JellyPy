"""Utilities for handling interpretation request data."""

import pathlib
import json
import jellypy.pyCIPAPI.interpretation_requests as irs

from jellypy.pyCIPAPI.auth import AuthenticatedCIPAPISession

from protocols.util.dependency_manager import VERSION_500
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.reports_6_0_1 import InterpretedGenome

def get_irjson(irid: int, irversion: int, session: AuthenticatedCIPAPISession) -> dict:
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

def save_irjson(ir_json: dict, outdir: str = None, file_name: str = None):
    """Save interpretation request json"""
    default_output = ir_json['interpretation_request_data']['json_request']['InterpretationRequestID'] + '.json'
    output_file = file_name if file_name else default_output
    output_path = pathlib.Path(outdir, output_file) if outdir else output_file
    with open(output_path, 'w') as f:
        json.dump(ir_json, f)

def read_irjson(filepath: str):
    """Read json file"""
    with open(filepath, 'r') as f:
        return json.load(f)


class IRJValidator():
    """Interpretation request Json V6. Utility methods for interacting with data structure."""
    
    def __init__(self):
        pass
    
    def validate(self, irjson):
        return self.is_v6(irjson) and self.is_sent(irjson) and self.is_unsolved(irjson)

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
        """Returns True if no reports have been issued that indicate the case has been solved."""
        if irjson['clinical_report'] == []:
            return True

        most_recent_report = max(irjson['clinical_report'], key = lambda x: x['clinical_report_version'])
        if most_recent_report['exit_questionnaire'] == None:
            return True

        is_unsolved = (most_recent_report['exit_questionnaire']['exit_questionnaire_data'][
            'familyLevelQuestions']['caseSolvedFamily'] != "yes")
        return is_unsolved


