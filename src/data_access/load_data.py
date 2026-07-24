# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to load SGC stations data.

import json
from colorama import Fore
from datetime import datetime
import pandas as pd
from pathlib import Path
from src.config import settings
from src.data_access.siigeo_client import SiigeoFetcher

logger = settings.get_logger(__name__)

class StationRepository:
    # Build station data filepaths
    siigeo_data_path = Path(settings.data_dir, settings.files.SIIGEO_STATIONS_FILE)
    shared_data_path = Path(settings.data_dir, settings.files.SHARED_STATIONS_FILE)
    inter_data_path = Path(settings.data_dir, settings.files.INTER_STATIONS_FILE)

    @classmethod
    def get_siigeo_stations(cls, mode:bool = False):
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
        try:
            with open(cls.shared_data_path, 'r') as file:
                shared_data = json.load(file)
            shared_data = pd.DataFrame.from_dict(shared_data).convert_dtypes(dtype_backend="pyarrow")
            shared_data = shared_data.astype(dtype={"CODIGO CANAL":"string[pyarrow]"})
            logger.info(Fore.GREEN + "Shared stations succesfully load." + Fore.RESET)

        except FileNotFoundError:
            logger.critical(Fore.RED + "Shared stations file doesn't exists!!" + Fore.RESET)
        
        return shared_data

    @classmethod
    def get_inter_stations(cls):
        try:
            with open(cls.inter_data_path, 'r') as file:
                inter_data = json.load(file)
            inter_data = pd.DataFrame.from_dict(inter_data).convert_dtypes(dtype_backend="pyarrow")
            logger.info(Fore.GREEN + "International stations succesfully load." + Fore.RESET)
            
        except FileNotFoundError:
            logger.critical(Fore.RED + "International stations file doesn't exists!!" + Fore.RESET)

        return inter_data
    
if __name__ == "__main__":
    StationRepository.get_siigeo_stations()
    StationRepository.get_shared_stations()
    StationRepository.get_inter_stations()
    #print(StationRepository.get_inter_stations().dtypes)