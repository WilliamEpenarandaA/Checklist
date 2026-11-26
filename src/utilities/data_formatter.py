# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains Formatter strategies for normalizing SIIGEO, shared, and international station DataFrames.

from abc import ABC, abstractmethod
from colorama import Fore
import pandas as pd
from src.config import settings
from src.data_access.load_data import StationRepository

logger = settings.get_logger(__name__)

class FormatterStrategy(ABC):
    """
    Abstract base class defining station DataFrame formatting steps.
    """

    @classmethod
    @abstractmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        """
        Rename raw source columns into standardized field names.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Raw station DataFrame to transform.
        """
        pass
    
    @classmethod
    @abstractmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        """
        Normalize column data types and text casing on station data.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Station DataFrame with renamed columns.
        """
        pass

    @classmethod
    @abstractmethod
    def infer_channel(cls, station_data:pd.DataFrame):
        """
        Infer or resolve sensor channel codes for station rows.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Station DataFrame with normalized types.
        """
        pass

    @classmethod
    @abstractmethod
    def filter_data(cls, station_data:pd.DataFrame):
        """
        Filter station records and select the target output columns.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Station DataFrame after channel inference.
        """
        pass

    @classmethod
    @abstractmethod
    def default_connection(cls, station_data:pd.DataFrame):
        """
        Initialize default connection metadata on station data.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Filtered station DataFrame.
        """
        pass


class SiigeoFormatter:
    """
    Formatter for SIIGEO station DataFrames with PyArrow-backed channel inference.
    """
    @classmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        """
        Rename SIIGEO Excel columns to standardized internal names.

        Maps ``'IDENTIFICADOR'`` -> ``'stid'``, ``'ESTADO ESTACIÓN'`` ->
        ``'station_status'``, ``'CÓDIGO LOCALIZACION'`` -> ``'loc'``,
        ``'ESTADO COD LOC.'`` -> ``'channel_status'``,
        ``'TIPO DE TRANSMISIÓN'`` -> ``'type_transmission'``,
        ``'TIPO DE ESTACIÓN'`` -> ``'type_station'``, and
        ``'TIPO DE ADQUISICIÓN'`` -> ``'type_acquisition'``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            SIIGEO station DataFrame loaded by ``StationRepository.get_siigeo_stations``.

        Returns
        -------
        pandas.DataFrame
            DataFrame with renamed columns.
        """
        station_data = station_data.rename(columns={'IDENTIFICADOR':'stid', 'ESTADO ESTACIÓN':'station_status',\
            'CÓDIGO LOCALIZACION':'loc', 'ESTADO COD LOC.':'channel_status',\
            'TIPO DE TRANSMISIÓN':'type_transmission', 'TIPO DE ESTACIÓN':'type_station',\
            'TIPO DE ADQUISICIÓN':'type_acquisition'})
        
        return station_data
    
    @classmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        """
        Replace null location values with ``None`` and lowercase status/type columns.

        Parameters
        ----------
        station_data : pandas.DataFrame
            SIIGEO DataFrame containing ``'loc'``, ``'station_status'``,
            ``'type_transmission'``, ``'type_station'``, and
            ``'type_acquisition'``.

        Returns
        -------
        pandas.DataFrame
            DataFrame with normalized ``'loc'`` nulls and lowercased text
            columns.
        """
        station_data ['loc'] = station_data['loc'].where(station_data['loc'].notnull(), None)
        station_data['station_status'] = station_data['station_status'].str.lower()
        station_data['type_transmission'] = station_data['type_transmission'].str.lower()
        station_data['type_station'] = station_data['type_station'].str.lower()
        station_data['type_acquisition'] = station_data['type_acquisition'].str.lower()

        return station_data
    
    @classmethod
    def infer_channel(cls, station_data:pd.DataFrame):
        """
        Infer channel codes from station ID and location code, cast to ``string[pyarrow]``.

        Assigns ``'BHZ'`` when ``stid == 'ROSC'`` and ``loc`` is null;
        otherwise looks up ``loc`` in ``settings.stations.CHANNEL_MAP``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            SIIGEO DataFrame containing ``'stid'`` and ``'loc'`` columns.

        Returns
        -------
        pandas.DataFrame
            DataFrame with an added ``'channel'`` column of dtype
            ``string[pyarrow]``.
        """
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
        """
        Keep active non-download stations and project standard columns.

        Filters rows where ``station_status == 'activa'`` and
        ``type_acquisition != 'descarga'``, then retains
        ``['network', 'stid', 'loc', 'channel', 'type_transmission']``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Formatted SIIGEO DataFrame containing ``'station_status'``,
            ``'type_acquisition'``, ``'network'``, ``'stid'``, ``'loc'``,
            ``'channel'``, and ``'type_transmission'``.

        Returns
        -------
        pandas.DataFrame
            Filtered DataFrame with columns ``['network', 'stid', 'loc',
            'channel', 'type_transmission']``.
        """
        station_data= station_data.loc[(station_data['station_status'] == 'activa')] 
        station_data = station_data.loc[(station_data['type_acquisition'] != 'descarga')]
        cols = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        station_data = station_data[cols] 
        logger.info(Fore.GREEN + "Dataframe formatted succesfully." + Fore.RESET + f" n={len(station_data)}")

        return station_data
    
    @classmethod
    def default_connection(cls, station_data:pd.DataFrame):
        """
        Add a ``'last_connection'`` column initialized to ``None``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Filtered SIIGEO station DataFrame.

        Returns
        -------
        pandas.DataFrame
            DataFrame including ``'last_connection'`` set to ``None``.
        """
        station_data['last_connection'] = None
        return station_data

class OtherStationsFormatter:
    """
    Formatter for shared and international station DataFrames.
    """
    @classmethod
    def rename_cols(cls, station_data:pd.DataFrame):
        """
        Rename shared/international JSON columns to standardized internal names.

        Maps ``'IDENTIFICADOR'`` -> ``'stid'``, ``'NOMBRE'`` -> ``'name'``,
        ``'ESTADO ESTACIÓN'`` / ``'ESTADO ESTACION'`` -> ``'station_status'``,
        ``'CODIGO RED'`` -> ``'network'``, ``'CODIGO SENSOR'`` ->
        ``'channel'``, ``'CODIGO CANAL'`` -> ``'loc'``,
        ``'TIPO DE TRANSMISION'`` -> ``'type_transmission'``, and
        ``'TIPO DE ADQUISICION'`` -> ``'type_acquisition'``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Station DataFrame from ``StationRepository.get_shared_stations`` or
            ``StationRepository.get_inter_stations``.

        Returns
        -------
        pandas.DataFrame
            DataFrame with renamed columns.
        """
        station_data = station_data.rename(columns={'IDENTIFICADOR':'stid', 'NOMBRE':'name', 'ESTADO ESTACIÓN':'station_status',\
            'CODIGO RED': 'network', 'CODIGO SENSOR': 'channel', 'CODIGO CANAL':'loc',
            'ESTADO ESTACION':'station_status', 'TIPO DE TRANSMISION':'type_transmission', 
            'TIPO DE ADQUISICION':'type_acquisition'})
        
        return station_data
    
    @classmethod
    def assign_data_types(cls, station_data:pd.DataFrame):
        """
        Normalize null values in ``'channel'``, ``'loc'``, and ``'network'`` and lowercase text fields.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Renamed shared or international station DataFrame.

        Returns
        -------
        pandas.DataFrame
            DataFrame with null placeholders set to ``None`` and lowercased
            status/transmission/acquisition columns.
        """
        station_data['channel'] = station_data['channel'].where(station_data['channel'].notnull(), None)
        station_data['loc'] = station_data['loc'].where(station_data['loc'].notnull(), None)
        station_data['network'] = station_data['network'].where(station_data['network'].notnull(), None)
        station_data['station_status'] = station_data['station_status'].str.lower()
        station_data['type_transmission'] = station_data['type_transmission'].str.lower()
        station_data['type_acquisition'] = station_data['type_acquisition'].str.lower()

        return station_data
    
    @classmethod
    def infer_channel(cls, station_data:pd.DataFrame):
        """
        Return ``station_data`` unchanged as channels are already present.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Station DataFrame with ``'channel'`` column.

        Returns
        -------
        pandas.DataFrame
            Unmodified ``station_data`` DataFrame.
        """
        return station_data

    @classmethod
    def filter_data(cls, station_data:pd.DataFrame):
        """
        Select standardized station columns without row filtering.

        Retains ``['network', 'stid', 'loc', 'channel', 'type_transmission']``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Formatted shared or international station DataFrame.

        Returns
        -------
        pandas.DataFrame
            DataFrame projected to ``['network', 'stid', 'loc', 'channel',
            'type_transmission']``.
        """
        cols = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        station_data = station_data[cols] 
        logger.info(Fore.GREEN + "Dataframe formatted succesfully." + Fore.RESET + f" n={len(station_data)}")
        return station_data
    
    @classmethod
    def default_connection(cls, station_data:pd.DataFrame):
        """
        Add a ``'last_connection'`` column initialized to ``None``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Projected station DataFrame.

        Returns
        -------
        pandas.DataFrame
            DataFrame including ``'last_connection'`` set to ``None``.
        """
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
