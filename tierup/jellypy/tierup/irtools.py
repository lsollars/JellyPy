"""Utilities for handling interpretation request data."""

import pathlib
import jellypy.pyCIPAPI.interpretation_requests as irs
from jellypy.pyCIPAPI.auth import AuthenticatedCIPAPISession

def get_irjson(irid: int, irversion: int, session: AuthenticatedCIPAPISession) -> dict:
    """Get an interpretation request json from the CPIAPI using jellpy.pyCIPAPI library
    Args:
        irid: Interpretation request id
        irv: Interpretation request version
        session: An authenticated CIPAPI session (pyCIPAPI)
    Returns:
        json_response: A dictionary containing the interpretation request response
    """
    json_response = irs.get_interpretation_request_json(irid, irversion, session=session)
    return json_response

def save_irjson(ir_json: dict, outdir: str = None, file_name: str = None):
    """Save interpretation request json to an output directory"""
    pass