import logging
import yaml
from pathlib import Path
from box import Box

logger = logging.getLogger(__name__)
base_root_path = Path(__file__).parent.parent.parent.parent
ai_root_path = Path(__file__).parent.parent
config_path = Path.joinpath(ai_root_path, "configs/config.yaml")

class ConfigService:
    def __init__(self):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            self._config = Box(config)

    # database
    @property
    def database_url(self):
        return self._config.database.url

    # database_init
    @property
    def source_dataset(self):
        file_name = self._config.database_init.source_file
        path = Path.joinpath(base_root_path, "datasets/")
        path = Path.joinpath(path, file_name)
        return path
    
    @property
    def base_collection_name(self):
        return self._config.database_init.base_collection_name
    
    @property
    def target_categories(self):
        return self._config.database_init.categories




GeneralConfigService = ConfigService()