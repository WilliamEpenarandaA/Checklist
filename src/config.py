import os
import logging
from pathlib import Path
from dataclasses import dataclass, field

# ====================================================
# SETUP LOGS
# ====================================================
class LoggerManager:
    def __init__(self, default_level=logging.DEBUG):
        self.default_level = default_level
        self.formatter = logging.Formatter("{asctime} [{levelname}] {message}", 
            style="{", datefmt="%H:%M:%S"
        )

    def get_logger(self, name:str = "checklist", level=None):
        logger_level = level if level is not None else self.default_level
        logger = logging.getLogger(name)
        logger.setLevel(logger_level)

        if not logger.hasHandlers():
            console = logging.StreamHandler()
            console.setFormatter(self.formatter)
            console.setLevel(logger_level)
            logger.addHandler(console)
            logger.propagate = False
        
        return logger

# ====================================================
# BASE PATHS
# ====================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(BASE_DIR, "data")

# ====================================================
# SIIGEO INTRANET CONFIGURATION
# ====================================================
## Intranet URL
class SiigeoConfig:
    URL = os.getenv("SIIGEO_URL", "https://siigeo.sgc.gov.co/stations/stationExcelCodLocation/")
    CACHE_EXPIRATION_DAYS = 30
    SECONDS_PER_DAY = 86400
    CACHE_EXPIRATION_SECONDS = CACHE_EXPIRATION_DAYS * SECONDS_PER_DAY

# ====================================================
# ENTRY POINT CONFIGURATION CLASS
# ====================================================
@dataclass
class ProjectSettings:
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    siigeo: SiigeoConfig = field(default_factory=SiigeoConfig)
    logger_manager: LoggerManager = field(default_factory=LoggerManager)
    ## Trick to call logger in a shorter way
    def get_logger(self, name:str, level=None):
        return self.logger_manager.get_logger(name, level)

settings = ProjectSettings()