# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This file has implementation of a siigeo client to download station information.

from colorama import Fore
from pathlib import Path
from datetime import datetime
from src.config import settings
import requests

logger = settings.get_logger(__name__)

class SiigeoFetcher:
    filename = "siigeo_stations.xlsx"
    filepath = Path(settings.data_dir, filename)

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

    @classmethod
    def update_info(cls, action:bool = False):
        try:
            timestamp_mod = SiigeoFetcher.filepath.stat().st_mtime
            mod_time = datetime.fromtimestamp(timestamp_mod)
            dt = (datetime.now() - mod_time).total_seconds()

            if dt > settings.siigeo.CACHE_EXPIRATION_SECONDS or action:
                logger.info(Fore.GREEN + "Updating station information!!!" + Fore.RESET)
                SiigeoFetcher.download_info()
            
        except FileNotFoundError:
            SiigeoFetcher.download_info()             

if __name__ == '__main__':
    SiigeoFetcher.update_info(action=True)
