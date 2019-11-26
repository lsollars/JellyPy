
"""
Tests for jellypy tierup package.

Usage from /JellyPy/tierup:
    pytest --jpconfig=test/config.ini
"""
import json
import pytest
import jellypy.pyCIPAPI.auth as auth
import jellypy.tierup.irtools as irt
import jellypy.tierup.panelapp as pa
import jellypy.tierup.lib as lib

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

class TestTierUpLib():

    @pytest.fixture
    def irjo(self, irjson):
        return irt.IRJson(irjson)

    def test_get_gene_map(self):
        """Test that the panel app gene map returns the structure: Dict[str, tuple]"""
        panel = pa.GeLPanel(213)
        mapping = panel.get_gene_map()
        key, value = list(mapping.items())[0]
        assert isinstance(key, str)
        assert isinstance(value, tuple)
    
    def test_irj_object(self, irjo):
        assert irjo.tiering['interpretationService'] == 'genomics_england_tiering'
        assert isinstance(irjo.panels, dict)
        irjo.update_panel('NEWPANEL', 123)
        assert 'NEWPANEL' in irjo.panels


    #TODO
    # EventPanelMatcher does the bulk of the work for gathering data for TierUp status.
    # Test it here with the following API
    # handler = ReportEventHandler(irjo)
    # for event in handler.generate_events(): # Produces a generator of report_event objects
    #    response = handler.query_panel_app(event)
    #    tierup_report = handler.build_report(event, response)
    #    print_as_csv(tierup_report)  
    def test_event_generator(self, irjo_local):
        """Test that the event handler generates report event objects"""
        reporter = lib.TierUpReporter(irjo_local)
        event = next(reporter.generate_events())
        assert isinstance(event, lib.ReportEvent)

    def test_query_pa(self, irjo_local):
        reporter = lib.TierUpReporter(irjo_local)
        test_panel = pa.GeLPanel(123)
        gene_false = 'ABCD'
        gene_true = 'ACVRL1'
        assert reporter.query_panel_app(gene_false, test_panel) == (gene_false, None, None, test_panel)
        assert all([reporter.query_panel_app(gene_true, test_panel)])

    def test_reporter(self, irjo_local):
        """Test that the event handler builds TierUp reports"""
        reporter = lib.TierUpReporter(irjo_local)
        event = next(reporter.generate_events())
        panel = irjo_local.panels[event.panel]
        _, hgnc, confidence, _ = reporter.query_panel_app(event.gene, panel)
        record = reporter.tierup_record(event, hgnc, confidence, panel)
        assert isinstance(record, dict)

    def test_panel_updater(self):
        # 11109-1.json is the test for this. Pull from API.
        with open('/home/nana/Documents/work/JellyPy/scripts/11109-1.json') as f:
            irjo = irt.IRJson(json.load(f))
        pu = lib.PanelUpdater()
        current = list(irjo.panels.keys())
        pu.add_event_panels(irjo)
        new = irjo.panels.keys()
        assert new != current
