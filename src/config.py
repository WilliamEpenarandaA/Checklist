# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# Project-wide configuration, constants, and logging setup.
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path

# ====================================================
# SETUP LOGS
# ====================================================
class LoggerManager:
    """
    Manager for creating and configuring console loggers.

    Attributes
    ----------
    default_level : int
        Default logging level applied when no explicit level is provided.
    formatter : logging.Formatter
        Log message formatter using the pattern ``'{asctime} [{levelname}] {message}'``
        and time format ``'%H:%M:%S'``.
    """
    def __init__(self, default_level=logging.DEBUG):
        """
        Initialize the logger manager with a default logging level.

        Parameters
        ----------
        default_level : int, default logging.DEBUG
            Logging level used as fallback when configuring loggers.
        """
        self.default_level = default_level
        self.formatter = logging.Formatter("{asctime} [{levelname}] {message}", 
            style="{", datefmt="%H:%M:%S"
        )

    def get_logger(self, name:str = "checklist", level=None):
        """
        Retrieve and configure a named logger with a console stream handler.

        Sets the logger level to ``level`` (or ``self.default_level`` if
        ``level`` is ``None``). If the logger does not yet have handlers,
        attaches a ``logging.StreamHandler`` formatted with ``self.formatter``
        and disables log propagation.

        Parameters
        ----------
        name : str, default 'checklist'
            Name of the logger to retrieve from ``logging.getLogger``.
        level : int or None, default None
            Logging level to apply. If ``None``, ``self.default_level`` is used.

        Returns
        -------
        logging.Logger
            Configured logger instance.
        """
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
    """
    Configuration constants for the SIIGEO intranet data source and local cache.

    Attributes
    ----------
    URL : str
        Endpoint URL to download the SIIGEO stations Excel file, read from the
        ``'SIIGEO_URL'`` environment variable with fallback to
        ``'https://siigeo.sgc.gov.co/stations/stationExcelCodLocation/'``.
    CACHE_EXPIRATION_DAYS : int
        Number of days before the local SIIGEO file cache expires (``30``).
    SECONDS_PER_DAY : int
        Number of seconds in one day (``86400``).
    CACHE_EXPIRATION_SECONDS : int
        Cache expiration threshold in seconds (``2592000``).
    """
    URL = os.getenv("SIIGEO_URL", "https://siigeo.sgc.gov.co/stations/stationExcelCodLocation/")
    CACHE_EXPIRATION_DAYS = 30
    SECONDS_PER_DAY = 86400
    CACHE_EXPIRATION_SECONDS = CACHE_EXPIRATION_DAYS * SECONDS_PER_DAY

# ====================================================
# SERVER CONFIGURATIONS
# ====================================================
class ServerConfig:
    """
    Network configuration for data acquisition servers.

    Attributes
    ----------
    PORTS : dict of {str: str or None}
        Mapping of server identifiers (``'232'``, ``'13'``, ``'97'``, ``'2'``,
        ``'91'``, ``'95'``) to their configured port strings or ``None``.
    SERVERS_WITH_FILE_OUTPUT : list of str
        List of server identifiers that generate output files
        (``['232', '13', '91', '95']``).
    """
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
        """
        Build the IP address (and optional port) string for a given server ID.

        Uses the ``10.100.101.<server_id>:<port>`` subnet when ``port`` is
        provided and ``server_id`` is ``'2'``, ``10.100.100.<server_id>:<port>``
        for any other ``server_id`` when ``port`` is provided, and
        ``10.100.100.<server_id>`` when ``port`` is ``None``.

        Parameters
        ----------
        server_id : str, default '91'
            Final octet identifier of the target server.
        port : str or None, default None
            Port number to append to the IP address. If ``None``, no port is
            appended.

        Returns
        -------
        str
            Formatted server IP address, including ``:<port>`` when ``port`` is
            not ``None``.
        """
        if port is not None:
            if server_id == '2':
                return f"10.100.101.{server_id}:{port}"
            else:
                return f"10.100.100.{server_id}:{port}"
        else: 
            return f"10.100.100.{server_id}"

# ====================================================
# STATUS THRESHOLDS
# ====================================================
class ThresholdsStatus:
    """
    Threshold constants for station status classification.

    Attributes
    ----------
    ONLINE_MAX_DELAY : int
        Maximum delay threshold in seconds (``180``) for online status.
    """
    ONLINE_MAX_DELAY = 180  # in seconds

# ====================================================
# FILE CONFIGURATIONS
# ====================================================
class FileConfig:
    """
    Input/output filenames and status symbol mappings for checklist files.

    Attributes
    ----------
    SIIGEO_STATIONS_FILE : str
        Filename for the SIIGEO stations Excel dataset (``'siigeo_stations.xlsx'``).
    SHARED_STATIONS_FILE : str
        Filename for the shared stations JSON dataset (``'shared_stations.json'``).
    INTER_STATIONS_FILE : str
        Filename for the international stations JSON dataset (``'inter_stations.json'``).
    SEISMO_OUT_FILE : str
        Output CSV filename for the seismometer checklist (``'seismo_checklist.csv'``).
    ACCEL_OUT_FILE : str
        Output CSV filename for the accelerometer checklist (``'accel_checklist.csv'``).
    INTER_OUT_FILE : str
        Output CSV filename for the international stations checklist (``'inter_checklist.csv'``).
    SYMBOL_STATUS_CHECKLIST : dict of {str: str}
        Mapping from station status labels (``'Online'``, ``'Intermittent'``,
        ``'Offline'``, ``'Future'``, ``'N/A'``, ``'Error'``) to checklist
        symbol strings.
    """
    # Input files
    SIIGEO_STATIONS_FILE = "siigeo_stations.xlsx"
    SHARED_STATIONS_FILE = "shared_stations.json"
    INTER_STATIONS_FILE = "inter_stations.json"

    # Output files
    SEISMO_OUT_FILE = "seismo_checklist.csv"
    ACCEL_OUT_FILE = "accel_checklist.csv"
    INTER_OUT_FILE = "inter_checklist.csv"

    SYMBOL_STATUS_CHECKLIST = {'Online': '', 'Intermittent': '--', 'Offline': 'x', 'Future': '?', 'N/A': 'x', 'Error': 'xx'} 

# ====================================================
# CHANNEL AND STATION CONFIGURATION
# ====================================================
class StationConfig:
    """
    Channel mappings, sensor channel groups, and station identifier lists.

    Attributes
    ----------
    CHANNEL_MAP : dict of {str: str}
        Mapping from two-digit location codes to vertical sensor channel codes.
    UNALIGN_CHANNELS : list of str
        Unaligned horizontal borehole/broadband channel codes (``['BH1', 'BH2']``).
    EAST_SLINKTOOL_CHANNELS : list of str
        East-component channel codes queried from ``slinktool``.
    NORTH_SLINKTOOL_CHANNELS : list of str
        North-component channel codes queried from ``slinktool``.
    VERTICAL_SLINKTOOL_CHANNELS : list of str
        Vertical-component channel codes queried from ``slinktool``.
    AVALAIBLE_SLINKTOOL_CHANNELS : list of str
        Combined list of east, north, vertical, and unaligned ``slinktool``
        channel codes.
    OVS_MAN : list of str
        Station codes associated with ``OVS_MAN``.
    OVS_POP : list of str
        Station codes associated with ``OVS_POP``.
    OVS_PA : list of str
        Station codes associated with ``OVS_PA``.
    UQ : list of str
        Station codes associated with ``UQ``.
    SHARED_NAT_ORDER : list of str
        Ordered concatenation of ``UQ``, ``OVS_MAN``, ``OVS_POP``, and
        ``OVS_PA`` station codes.
    SEISMOMETER_CHANNELS : list of str
        Channel codes classified under seismometers.
    ACCELEROMETER_CHANNELS : list of str
        Channel codes classified under accelerometers.
    STRONG_MOTION_CHANNELS : list of str
        Channel codes classified under strong-motion sensors.
    SHORT_PERIOD_CHANNELS : list of str
        Channel codes classified under short-period sensors.
    INTER_PATTERN_CHANNELS : dict of {str: str}
        Mapping from vertical channel codes to two-character channel prefixes
        for international stations.
    SPECIAL_INTER_STATIONS : list of str
        Identifiers of international stations with special handling
        (``['JTS', 'NNA', 'SDV', 'SJG', 'TEIG']``).
    """
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
    EAST_SLINKTOOL_CHANNELS = ['BHE', 'HHE', 'HNE', 'EHE', 'HLE', 'ELE']
    NORTH_SLINKTOOL_CHANNELS = ['BHN', 'HHN', 'HNN', 'EHN', 'HLN', 'ELN']
    VERTICAL_SLINKTOOL_CHANNELS = ['BHZ', 'HHZ', 'HNZ', 'EHZ', 'HLZ', 'SHZ', 'ELZ']
    AVALAIBLE_SLINKTOOL_CHANNELS = [*EAST_SLINKTOOL_CHANNELS, 
                                    *NORTH_SLINKTOOL_CHANNELS, 
                                    *VERTICAL_SLINKTOOL_CHANNELS, 
                                    *UNALIGN_CHANNELS]

    OVS_MAN = ['AGAM', 'ANIM', 'ELAM', 'NIDM', 'PIRM', 'SJUM', 'TAPM']
    OVS_POP = ['BELO', 'CALO', 'CONO', 'SOTO', 'PALO']
    OVS_PA = ['BODP', 'DANP', 'GCUF', 'GUAP']
    UQ = ['PBLA', 'RIBER']
    SHARED_NAT_ORDER = [*UQ, *OVS_MAN, *OVS_POP, *OVS_PA]
    SEISMOMETER_CHANNELS = ['BH1', 'BH2', 'BHE', 'BHN', 'BHZ', 'HHE', 'HHN', 'HHZ']
    ACCELEROMETER_CHANNELS = ['HNE', 'HNN', 'HNZ']
    STRONG_MOTION_CHANNELS = ['HLE', 'HLN', 'HLZ']
    SHORT_PERIOD_CHANNELS = ['EHE', 'EHN', 'EHZ', 'ELZ']
    INTER_PATTERN_CHANNELS = {'BHZ': 'BH', 'HHZ': 'HH', 'HNZ': 'HN', 'EHZ': 'EH', 'HLZ': 'HL', 'SHZ': 'SH', '': ''}
    SPECIAL_INTER_STATIONS = ['JTS', 'NNA', 'SDV', 'SJG', 'TEIG']

# ====================================================
# ENTRY POINT CONFIG ENVIRONMENT VARIABLES
# ====================================================
@dataclass
class ProjectSettings:
    """
    Aggregated project configuration container.

    Attributes
    ----------
    base_dir : pathlib.Path
        Root directory of the project.
    data_dir : pathlib.Path
        Directory containing local station input/output data files.
    siigeo : SiigeoConfig
        SIIGEO intranet URL and cache expiration settings.
    logger_manager : LoggerManager
        Centralized logger factory instance.
    files : FileConfig
        Input/output filenames and checklist status symbols.
    servers : ServerConfig
        Acquisition server ports and IP resolution settings.
    stations : StationConfig
        Channel mappings and station group definitions.
    thresholds : ThresholdsStatus
        Delay thresholds for station status evaluation.
    """
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    siigeo: SiigeoConfig = field(default_factory=SiigeoConfig)
    logger_manager: LoggerManager = field(default_factory=LoggerManager)

    ## Trick to call logger in a shorter way
    def get_logger(self, name:str, level=None):
        """
        Retrieve a configured logger via ``self.logger_manager``.

        Parameters
        ----------
        name : str
            Name of the logger to retrieve.
        level : int or None, default None
            Logging level to apply. If ``None``, the manager's default level is
            used.

        Returns
        -------
        logging.Logger
            Configured logger instance.
        """
        return self.logger_manager.get_logger(name, level)

    files: FileConfig = field(default_factory=FileConfig)
    servers: ServerConfig = field(default_factory=ServerConfig)
    stations: StationConfig = field(default_factory=StationConfig)
    thresholds: ThresholdsStatus = field(default_factory=ThresholdsStatus)

settings = ProjectSettings()