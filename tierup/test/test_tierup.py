
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
        data = irt.get_irjson(2202, 2, session=cipapi_session)
        assert isinstance(data, dict)
    
    def test_save_irjson(self, tmpdir):
        irjson = irt.get_irjson(2202, 2, session=cipapi_session)
        outdir = tmpdir.mkdir('tierup_test')
        # Check a file is created with the interpretation request and ID by default
        irt.save_irjson(irjson, outdir)
        assert outdir.join('OPA-2202-2.json').check(file=True)
        # Assert a file is created with the interpretation request and ID with given args
        irt.save_irjson(irjson, outdir, '2202-2_data.json')
        assert outdir.join('2202-2_data.json').check(file=True)

@pytest.fixture
def irjson(cipapi_session):
    return irt.get_irjson(455, 1, session=cipapi_session)

class TestIRValidator():
    def test_v6_validator(self, cipapi_session):
        """Test json is GeL v6 model.
        Although we use the reports_v6=True request parameter, earlier interpretation request jsons
        are returned without v6 data structure. Here we test two examples with the gelmodels validation."""
        validator = irt.IRJValidator()

        is_v6 = irt.get_irjson(456,2,session=cipapi_session)
        not_v6 = irt.get_irjson(45,2,session=cipapi_session)

        assert validator.is_v6(is_v6) == True
        assert validator.is_v6(not_v6) == False

    def test_sent_to_gmcs(self, irjson, cipapi_session):
        """Test json has been reported by GeL"""
        validator = irt.IRJValidator()
        assert validator.is_sent(irjson) == True

    def test_unsolved(self, irjson, cipapi_session):
        """Test json has not been reported solved"""
        validator = irt.IRJValidator()
        assert validator.is_unsolved(irjson) == True