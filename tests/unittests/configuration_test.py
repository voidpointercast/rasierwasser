from unittest import TestCase
from pathlib import Path
from rasierwasser.configuration.main import load_config_from_file, RasierwasserConfig

class ConfigurationTest(TestCase):

    def setUp(self) -> None:
        self.data_dir = Path(__file__).parent.joinpath('data', 'configuration_test')

    def test_json_parsing(self):
        config: RasierwasserConfig = load_config_from_file(self.data_dir.joinpath('rasierwasser.json'))
        print(config)