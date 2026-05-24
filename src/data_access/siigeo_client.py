# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This file has implementation of a siigeo client to download station information from SGC.

from colorama import Fore
from pathlib import Path
from src.config import settings
import requests

logger = settings.get_logger(__name__)

class SiigeoFetcher:
    filepath = Path(settings.data_dir, settings.files.SIIGEO_STATIONS_FILE)

    @classmethod
    def download_info(cls):
        try:
            logger.info(Fore.GREEN + "Downloading stations information from siigeo!!!" + Fore.RESET)
            response = requests.get(settings.siigeo.URL, verify=None)
            response.raise_for_status()
            logger.info(Fore.GREEN + "Success." + Fore.RESET)
            with open(SiigeoFetcher.filepath, 'wb') as file:
                file.write(response.content)
        except requests.exceptions.HTTPError as err:
            logger.error(Fore.RED + f"HTTP error: {err}" + Fore.RESET)
        except Exception as err:
            logger.error(Fore.RED + f"Error: {err}" + Fore.RESET)                 

if __name__ == '__main__':
    SiigeoFetcher.download_info()
