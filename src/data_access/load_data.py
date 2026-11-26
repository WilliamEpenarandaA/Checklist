# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation of a data access module for loading SGC and international station datasets.

import json
from colorama import Fore
from datetime import datetime
import pandas as pd
from pathlib import Path
from src.config import settings
from src.data_access.siigeo_client import SiigeoFetcher

logger = settings.get_logger(__name__)

class StationRepository:
    """
    Repository for loading SIIGEO, shared, and international SGC station data.

    Attributes
    ----------
    siigeo_data_path : pathlib.Path
        Path to the local Excel file containing SIIGEO station metadata
        (``data/siigeo_stations.xlsx``).
    shared_data_path : pathlib.Path
        Path to the local JSON file containing shared station metadata
        (``data/shared_stations.json``).
    inter_data_path : pathlib.Path
        Path to the local JSON file containing international station metadata
        (``data/inter_stations.json``).
    """
    # Build station data filepaths
    siigeo_data_path = Path(settings.data_dir, settings.files.SIIGEO_STATIONS_FILE)
    shared_data_path = Path(settings.data_dir, settings.files.SHARED_STATIONS_FILE)
    inter_data_path = Path(settings.data_dir, settings.files.INTER_STATIONS_FILE)

    @classmethod
    def get_siigeo_stations(cls, mode:bool = False):
        """
        Load SIIGEO station metadata into a PyArrow-backed DataFrame.

        Evaluates the last modification timestamp of ``SiigeoFetcher.filepath``
        against ``settings.siigeo.CACHE_EXPIRATION_SECONDS``. Invokes
        ``SiigeoFetcher.download_info()`` when the cache has expired, when
        ``mode`` is ``True``, or when ``SiigeoFetcher.filepath`` is missing.
        Reads seven station metadata columns from ``siigeo_data_path`` and
        appends a ``'network'`` column set to ``'CM'``.

        Parameters
        ----------
        mode : bool, default False
            If ``True``, forces downloading updated station data from SIIGEO
            regardless of cache expiration time.

        Returns
        -------
        pandas.DataFrame
            Station dataset backed by ``string[pyarrow]`` columns:
            ``'IDENTIFICADOR'``, ``'ESTADO ESTACIÓN'``,
            ``'CÓDIGO LOCALIZACION'``, ``'ESTADO COD LOC.'``,
            ``'TIPO DE TRANSMISIÓN'``, ``'TIPO DE ESTACIÓN'``,
            ``'TIPO DE ADQUISICIÓN'``, and ``'network'``.

        Raises
        ------
        FileNotFoundError
            If ``siigeo_data_path`` does not exist on disk when reading the
            Excel file (for example, if the file was absent and
            ``SiigeoFetcher.download_info()`` failed to download it).
        """
        try:
            timestamp_mod = SiigeoFetcher.filepath.stat().st_mtime
            mod_time = datetime.fromtimestamp(timestamp_mod)
            dt = (datetime.now() - mod_time).total_seconds()

            if dt > settings.siigeo.CACHE_EXPIRATION_SECONDS or mode:
                logger.info(Fore.GREEN + "Updating station information!!!" + Fore.RESET)
                SiigeoFetcher.download_info()
            
        except FileNotFoundError:
            SiigeoFetcher.download_info()

        cols = ['IDENTIFICADOR', 'ESTADO ESTACIÓN', 'CÓDIGO LOCALIZACION', 'ESTADO COD LOC.',\
            'TIPO DE TRANSMISIÓN', 'TIPO DE ESTACIÓN', 'TIPO DE ADQUISICIÓN']
        siigeo_data = pd.read_excel(cls.siigeo_data_path, usecols=cols, dtype_backend="pyarrow", dtype={'CÓDIGO LOCALIZACION':"string[pyarrow]"})
        siigeo_data['network'] = 'CM'
        siigeo_data['network'] = siigeo_data['network'].astype("string[pyarrow]")
        logger.info(Fore.GREEN + "Stations from Siigeo file succesfully load." + Fore.RESET)

        return siigeo_data
    
    @classmethod
    def get_shared_stations(cls):
        """
        Load shared station metadata from JSON into a PyArrow-backed DataFrame.

        Reads and parses ``shared_data_path``, verifies that the parsed JSON
        list is non-empty, converts it into a PyArrow-backed DataFrame, and
        explicitly casts ``'CODIGO CANAL'`` to ``string[pyarrow]``.

        Returns
        -------
        pandas.DataFrame
            Shared station dataset backed by ``string[pyarrow]`` columns:
            ``'IDENTIFICADOR'``, ``'nombre'``, ``'CODIGO RED'``,
            ``'CODIGO SENSOR'``, ``'CODIGO CANAL'``, ``'ESTADO ESTACION'``,
            ``'TIPO DE TRANSMISION'``, and ``'TIPO DE ADQUISICION'``.

        Raises
        ------
        FileNotFoundError
            If ``shared_data_path`` does not exist.
        ValueError
            If the parsed JSON content is empty, or if the file cannot be
            decoded as valid JSON (``json.JSONDecodeError``).
        KeyError
            If ``'CODIGO CANAL'`` is missing from the loaded records.
        """
        try:
            with open(cls.shared_data_path, 'r') as file:
                shared_data = json.load(file)

            if not shared_data:
                raise ValueError("Shared station file is empty.")
            shared_data = pd.DataFrame.from_dict(shared_data).convert_dtypes(dtype_backend="pyarrow")
            shared_data = shared_data.astype(dtype={"CODIGO CANAL":"string[pyarrow]"})
            logger.info(Fore.GREEN + "Shared stations succesfully load." + Fore.RESET)

        except FileNotFoundError:
            logger.critical(Fore.RED + f"Shared stations file doesn't exists at {cls.shared_data_path}!!" + Fore.RESET)
            raise

        except ValueError as err:
            logger.critical(Fore.RED + str(err) + Fore.RESET)
            raise

        return shared_data

    @classmethod
    def get_inter_stations(cls):
        """
        Load international station metadata from JSON into a PyArrow-backed DataFrame.

        Reads and parses ``inter_data_path``, verifies that the parsed JSON
        list is non-empty, and converts it into a PyArrow-backed DataFrame.

        Returns
        -------
        pandas.DataFrame
            International station dataset backed by ``string[pyarrow]`` columns:
            ``'IDENTIFICADOR'``, ``'nombre'``, ``'pais'``, ``'CODIGO RED'``,
            ``'CODIGO SENSOR'``, ``'CODIGO CANAL'``, ``'ESTADO ESTACION'``,
            ``'TIPO DE TRANSMISION'``, and ``'TIPO DE ADQUISICION'``.

        Raises
        ------
        FileNotFoundError
            If ``inter_data_path`` does not exist.
        ValueError
            If the parsed JSON content is empty, or if the file cannot be
            decoded as valid JSON (``json.JSONDecodeError``).
        """
        try:
            with open(cls.inter_data_path, 'r') as file:
                inter_data = json.load(file)

            if not inter_data:
                raise ValueError("International station file is empty.")
            inter_data = pd.DataFrame.from_dict(inter_data).convert_dtypes(dtype_backend="pyarrow")
            logger.info(Fore.GREEN + "International stations succesfully load." + Fore.RESET)
            
        except FileNotFoundError:
            logger.critical(Fore.RED + f"International stations file doesn't exists at {cls.inter_data_path}!!" + Fore.RESET)
            raise

        except ValueError as err:
            logger.critical(Fore.RED + str(err) + Fore.RESET)
            raise

        return inter_data
    
if __name__ == "__main__":
    StationRepository.get_siigeo_stations()
    StationRepository.get_shared_stations()
    StationRepository.get_inter_stations()
    #print(StationRepository.get_inter_stations().dtypes)