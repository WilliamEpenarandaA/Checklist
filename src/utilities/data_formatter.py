# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to give an specific format SGC stations data.

import pandas as pd
from abc import ABC, abstractmethod
from colorama import Fore
from src.config import settings
from src.data_access.load_data import StationRepository

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
    def infer_channel(cls, station_data:pd.DataFrame):
        pass

    @classmethod
    @abstractmethod
    def filter_data(cls, station_data:pd.DataFrame):
        pass

    @classmethod
    @abstractmethod
    def default_connection(cls, station_data:pd.DataFrame):
        pass


class SiigeoFormatter:
    @classmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        station_data = station_data.rename(columns={'IDENTIFICADOR':'stid', 'ESTADO ESTACIÓN':'station_status',\
            'CÓDIGO LOCALIZACION':'loc', 'ESTADO COD LOC.':'channel_status',\
            'TIPO DE TRANSMISIÓN':'type_transmission', 'TIPO DE ESTACIÓN':'type_station',\
            'TIPO DE ADQUISICIÓN':'type_acquisition'})
        
        return station_data
    
    @classmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        station_data ['loc'] = station_data['loc'].where(station_data['loc'].notnull(), None)
        station_data['station_status'] = station_data['station_status'].str.lower()
        station_data['type_transmission'] = station_data['type_transmission'].str.lower()
        station_data['type_station'] = station_data['type_station'].str.lower()
        station_data['type_acquisition'] = station_data['type_acquisition'].str.lower()

        return station_data
    
    @classmethod
    def infer_channel(cls, station_data:pd.DataFrame):
        def infer(row):
            if row['stid'] == 'ROSC' and pd.isna(row['loc']):
                return 'BHZ'
            else:
                return settings.stations.CHANNEL_MAP.get(row['loc'])
            
        station_data['channel'] = station_data.apply(infer, axis=1)
        station_data['channel'] = station_data['channel'].astype("string[pyarrow]")

        return station_data

    @classmethod
    def filter_data(cls, station_data:pd.DataFrame):
        station_data= station_data.loc[(station_data['station_status'] == 'activa')] 
        station_data = station_data.loc[(station_data['type_acquisition'] != 'descarga')]
        cols = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        station_data = station_data[cols] 
        logger.info(Fore.GREEN + "Dataframe formatted sucessfully." + Fore.RESET + f" n={len(station_data)}")

        return station_data
    
    @classmethod
    def default_connection(cls, station_data:pd.DataFrame):
        station_data['last_connection'] = None
        return station_data

class OtherStationsFormatter:
    @classmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        station_data = station_data.rename(columns={'IDENTIFICADOR':'stid', 'NOMBRE':'name', 'ESTADO ESTACIÓN':'station_status',\
            'CODIGO RED': 'network', 'CODIGO SENSOR': 'channel', 'CODIGO CANAL':'loc',
            'ESTADO ESTACION':'station_status', 'TIPO DE TRANSMISION':'type_transmission', 
            'TIPO DE ADQUISICION':'type_acquisition'})
        
        return station_data
    
    @classmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        station_data['channel'] = station_data['channel'].where(station_data['channel'].notnull(), None)
        station_data['loc'] = station_data['loc'].where(station_data['loc'].notnull(), None)
        station_data['network'] = station_data['network'].where(station_data['network'].notnull(), None)
        station_data['station_status'] = station_data['station_status'].str.lower()
        station_data['type_transmission'] = station_data['type_transmission'].str.lower()
        station_data['type_acquisition'] = station_data['type_acquisition'].str.lower()

        return station_data
    
    @classmethod
    def infer_channel(cls, station_data:pd.DataFrame):
        return station_data

    @classmethod
    def filter_data(cls, station_data:pd.DataFrame):
        cols = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        station_data = station_data[cols] 
        logger.info(Fore.GREEN + "Dataframe formatted sucessfully." + Fore.RESET + f" n={len(station_data)}")
        return station_data
    
    @classmethod
    def default_connection(cls, station_data:pd.DataFrame):
        station_data['last_connection'] = None
        return station_data
    
if __name__ == "__main__":
    siigeo_data = StationRepository.get_siigeo_stations()
    shared_data = StationRepository.get_shared_stations()
    inter_data = StationRepository.get_inter_stations()

    data = {'siigeo': siigeo_data, 'shared': shared_data, 'inter': inter_data}
    format_data = {}
    for key, df in data.items():
        strategy = SiigeoFormatter() if key == 'siigeo' else OtherStationsFormatter()
        df = strategy.rename_cols(df)
        df = strategy.assign_data_types(df)
        df = strategy.infer_channel(df)
        df = strategy.filter_data(df)
        df = strategy.default_connection(df)
        format_data[key] = df     

    siigeo_data = format_data['siigeo']
    shared_data = format_data['shared']
    inter_data = format_data['inter']
    print(f'{siigeo_data.loc[siigeo_data['stid'] == 'BLMC']}')
    print(f'{siigeo_data.loc[siigeo_data['stid'] == 'ROSC']}')
    print(f'{siigeo_data.loc[siigeo_data['stid'] == 'DRL04']}')

    print(siigeo_data.dtypes)
    print(shared_data.dtypes)
