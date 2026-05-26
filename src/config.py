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
# SERVER CONFIGURATIONS
# ====================================================
class ServerConfig:
    PORTS = {
        "232": "16501",
        "13" : "16501",
        "97" : "18000",
        "2"  : "18000",
        "91" : None,
        "95" : None
    }
    SERVERS_WITH_FILE_OUTPUT = ["232", "13", "91", "95"]

    @classmethod
    def get_server_ip(cls, server_id:str = '91', port:str = None):
        if port is not None:
            if server_id == '2':
                return f"10.100.101.{server_id}:{port}"
            else:
                return f"10.100.100.{server_id}:{port}"
        else: 
            return f"10.100.100.{server_id}"

# ====================================================
# FILE CONFIGURATIONS
# ====================================================
class FileConfig:
    # input files
    SIIGEO_STATIONS_FILE = "siigeo_stations.xlsx"
    SHARED_STATIONS_FILE = "shared_stations.json"
    INTER_STATIONS_FILE = "inter_stations.json"

    #output files
    SEISMO_OUT_FILE = "seismo_checklist.csv"
    ACCEL_OUT_FILE = "accel_checklist.csv"
    INTER_OUT_FILE = "inter_checklist.csv" 

# ====================================================
# CHANNEL AND STATION CONFIGURATION
# ====================================================
class StationConfig:
    CHANNEL_MAP = {
        '00': 'HHZ',
        '01': 'HHZ',
        '10': 'HNZ',
        '11': 'HNZ',
        '20': 'EHZ',
        '30': 'HHZ',
        '40': 'HLZ'
    }
    UNALIGN_CHANNELS = ['BH1', 'BH2'] 
    EAST_SLINKTOOL_CHANNELS = ['BHE', 'HHE', 'HNE', 'EHE', 'HLE']
    NORTH_SLINKTOOL_CHANNELS = ['BHN', 'HHN', 'HNN', 'EHN', 'HLN']
    VERTICAL_SLINKTOOL_CHANNELS = ['BHZ', 'HHZ', 'HNZ', 'EHZ', 'HLZ']
    AVALAIBLE_SLINKTOOL_CHANNELS = [*EAST_SLINKTOOL_CHANNELS, 
                                    *NORTH_SLINKTOOL_CHANNELS, 
                                    *VERTICAL_SLINKTOOL_CHANNELS, 
                                    *UNALIGN_CHANNELS]

    SPECIAL_INTER_STATIONS = ['JTS', 'SDV']
    OVS_MAN = ['AGAM', 'ANIM', 'ELAM', 'NIDM', 'PIRM', 'SJUM', 'TAPM']
    OVS_POP = ['BELO', 'CONO', 'SOTO', 'PALO']
    OVS_PA = ['BODP', 'GCUF', 'GUAP']
    UQ = ['PBLA', 'RIBER']
    SHARED_NAT_ORDER = [*UQ, *OVS_MAN, *OVS_POP, *OVS_PA]

# ====================================================
# ENTRY POINT CONFIG CLASS
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

    files: FileConfig = field(default_factory=FileConfig)
    servers: ServerConfig = field(default_factory=ServerConfig)
    stations: StationConfig = field(default_factory=StationConfig)

settings = ProjectSettings()