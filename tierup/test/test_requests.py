"""
Tests 

Usage:
    pytest tierup/test/test_requests.py --jpconfig=tierup/test/config.ini
"""

import json
import pytest
import jellypy.pyCIPAPI.interpretation_requests as irs
import jellypy.pyCIPAPI.auth as auth

class TestIRtools():
    def test_get_irjson(self, jpconfig):
        irid = jpconfig.get('pyCIPAPI', 'test_irid')
        irversion = jpconfig.get('pyCIPAPI', 'test_irversion')
        session = auth.AuthenticatedCIPAPISession(
                auth_credentials={
                'username': jpconfig.get('pyCIPAPI', 'username'),
                'password': jpconfig.get('pyCIPAPI', 'password')
            }
        )
        # Attempt to get a known interpretation request. This can be changed in the test config.
        data = irs.get_interpretation_request_json(irid, irversion, reports_v6=True, session=session)
        assert isinstance(data, dict)
