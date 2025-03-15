import logging
import logging.config
import colorlog
import yaml
from pathlib import Path
from .config_service import GeneralConfigService
from .database_service import DatabaseService
from .clip_embedding_service import ClipEmbeddingService


config_path = Path.joinpath(Path(__file__).parent.parent, "configs/logger_config.yaml")

# read logger_config.yaml (seperated from general config service)
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config=config)

