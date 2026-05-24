## Configuration Projects Environments
import os
from pathlib import Path
from dataclasses import dataclass, field

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
# CLASS CONFIGURATION
# ====================================================
@dataclass
class ProjectSettings:
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    siigeo: SiigeoConfig = field(default_factory=SiigeoConfig)

settings = ProjectSettings()