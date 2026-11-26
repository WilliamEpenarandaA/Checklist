# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This file has implementation of a HTTP client module for downloading SIIGEO station information from SGC.

import requests
from colorama import Fore
from pathlib import Path
from src.config import settings

logger = settings.get_logger(__name__)

class SiigeoFetcher:
    """
    Client for fetching and saving the SIIGEO stations Excel file locally.

    Attributes
    ----------
    filepath : pathlib.Path
        Local destination path where the downloaded SIIGEO stations file is
        saved (``data/siigeo_stations.xlsx``).
    """
    filepath = Path(settings.data_dir, settings.files.SIIGEO_STATIONS_FILE)

    @classmethod
    def download_info(cls):
        """
        Download station metadata from ``settings.siigeo.URL`` to disk.

        Sends an HTTP GET request to ``settings.siigeo.URL`` with
        ``verify=None``, validates the HTTP response status via
        ``raise_for_status()``, and writes the binary content to
        ``SiigeoFetcher.filepath``. Any ``requests.exceptions.HTTPError`` or
        general ``Exception`` is logged internally without being re-raised.
        """
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
