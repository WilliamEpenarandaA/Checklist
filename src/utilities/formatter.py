# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# .

import pandas as pd
from src.config import settings
from abc import ABC, abstractmethod
from colorama import Fore

logger = settings.get_logger(__name__)

class FormatterStrategy(ABC):
    @classmethod
    @abstractmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        pass
    
    @classmethod
    @abstractmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        pass

    @classmethod
    @abstractmethod
    def filter_data(cls, station_data:pd.DataFrame):
        pass

class SiigeoFormatter:
    @classmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        station_data = station_data.rename(columns={'IDENTIFICADOR':'id', 'ESTADO ESTACIÓN':'station_status',\
            'CÓDIGO LOCALIZACION':'channel_code', 'ESTADO COD LOC.':'channel_status',\
            'TIPO DE TRANSMISIÓN':'type_transmission', 'TIPO DE ESTACIÓN':'type_station',\
            'TIPO DE ADQUISICIÓN':'type_adquissition'})
        
        return station_data
    
    @classmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        station_data ['channel_code'] = station_data['channel_code'].fillna('').astype(str)
        station_data['station_status'] = station_data['station_status'].astype(str).str.lower()
        station_data['type_transmission'] = station_data['type_transmission'].astype(str).str.lower()
        station_data['type_station'] = station_data['type_station'].astype(str).str.lower()
        station_data['type_adquissition'] = station_data['type_adquissition'].astype(str).str.lower()
        
        return station_data
    
    @classmethod
    def filter_data(cls, station_data:pd.DataFrame):
        station_data= station_data.loc[(station_data['station_status'] == 'activa')] 
        station_data = station_data.loc[(station_data['type_adquissition'] != 'descarga')]
        cols = ['network_code', 'id', 'channel_code', 'type_transmission']
        station_data = station_data[cols] 
        logger.info(Fore.GREEN + "Dataframe formatted sucessfully." + Fore.RESET + f" n={len(station_data)}")

        return station_data

class OtherStationsFormatter:
    @classmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        station_data = station_data.rename(columns={'IDENTIFICADOR':'id', 'NOMBRE':'name', 'ESTADO ESTACIÓN':'station_status',\
            'CODIGO RED': 'network_code', 'CODIGO SENSOR': 'channel', 'CODIGO CANAL':'channel_code',
            'ESTADO ESTACION':'station_status', 'TIPO DE TRANSMISION':'type_transmission', 
            'TIPO DE ADQUISICION':'type_adquissition'})
        
        return station_data
    
    @classmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        station_data['channel'] = station_data['channel'].fillna('').astype(str)
        station_data['channel_code'] = station_data['channel_code'].fillna('').astype(str)
        station_data['network_code'] = station_data['network_code'].fillna('').astype(str)
        station_data['station_status'] = station_data['station_status'].astype(str).str.lower()
        station_data['type_transmission'] = station_data['type_transmission'].astype(str).str.lower()
        station_data['type_adquissition'] = station_data['type_adquissition'].astype(str).str.lower()

        return station_data
    
    @classmethod
    def filter_data(cls, station_data:pd.DataFrame):
        cols = ['network_code', 'id', 'channel_code', 'type_transmission']
        station_data = station_data[cols] 
        logger.info(Fore.GREEN + "Dataframe formatted sucessfully." + Fore.RESET + f" n={len(station_data)}")
        return station_data

if __name__ == "__main__":
    from src.data_access.load_data import StationRepository
    siigeo_data = StationRepository.get_siigeo_stations()
    shared_data = StationRepository.get_shared_stations()
    inter_data = StationRepository.get_inter_stations()

    data = {'siigeo': siigeo_data, 'shared': shared_data, 'inter': inter_data}
    format_data = {}
    for key, df in data.items():
        strategy = SiigeoFormatter() if key == 'siigeo' else OtherStationsFormatter()
        df = strategy.rename_cols(df)
        df = strategy.assign_data_types(df)
        df = strategy.filter_data(df)
        format_data[key] = df     

    siigeo_data = format_data['siigeo']
    shared_data = format_data['shared']
    inter_data = format_data['inter']