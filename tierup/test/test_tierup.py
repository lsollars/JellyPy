
"""
Tests for jellypy tierup package.

Usage from /JellyPy/tierup:
    pytest --pconfig=test/config.ini
"""
import pytest
import jellypy.pyCIPAPI.auth as auth
import jellypy.tierup.irtools as irt

@pytest.fixture
def cipapi_session(jellypy_config):
    auth_credentials = {
        'username': jellypy_config['pyCIPAPI']['username'],
        'password': jellypy_config['pyCIPAPI']['password']
    }
    return auth.AuthenticatedCIPAPISession(auth_credentials=auth_credentials)

class TestIRTools():
    def test_get_irjson(self, cipapi_session):
        """Interpretation request jsons can be downloaded from the CIPAPI"""
        data = irt.get_ir_json(2202, 2, session=cipapi_session)
        assert isinstance(data, dict)
    
    @pytest.fixture
    def test_irj(cipapi_session):
        return irt.get_irjson(2202, 2, session=cipapi_session)

    def test_save_irjson(self, test_irj, tmpdir):
        # Create directory
        outdir = tmpdir.mkdir('tierup_test')
        # Check a file is created with the interpretation request and ID by default
        irt.save_irjson(test_irj, outdir)
        assert tmpdir.join('2202-2.json').check(file=True)
        # Assert a file is created with the interpretation request and ID with given args
        irt.save_irjson(test_irj, outdir, '2202-2_data.json')
        assert tmpdir.join('2202-2_data.json').check(file=True)

    
    # def test_v6_validator(self, cipapi_session):
    #     """Returned json is GeL v6 model.
    #     Although we use the reports_v6=True request parameter, earlier interpretation request jsons
    #     are returned without v6 data structure. Here we test two examples with the gelmodels validation."""
    #     is_v6 = irs.get_interpretation_request_json(54715,1,session=cipapi_session)
    #     not_v6 = irs.get_interpretation_request_json(45,2,session=cipapi_session)

    #     v6_validator = irs.get_v6_interpreted_genome_validator()

    #     # Test the first interpreted genome against the interpreted genome v6 model
    #     is_v6_ig = is_v6['interpreted_genome'][0]['interpreted_genome_data']
    #     not_v6_ig = not_v6['interpreted_genome'][0]['interpreted_genome_data']
        
    #     assert v6_validator.validate(is_v6_ig) == True
    #     assert v6_validator.validate(not_v6_ig) == False