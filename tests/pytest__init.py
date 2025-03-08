class TestInit:
    def test__version(self):
        from fixtures_generator import __version__
        assert __version__ == '1.0.3'
