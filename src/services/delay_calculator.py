# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains a service module for merging untracked stations and computing transmission delays.

from colorama import Fore
from datetime import datetime, UTC
import numpy as np
import pandas as pd
from src.config import settings

logger = settings.get_logger(__name__)

class DelayCalculator:
    """
    Calculator for merging untracked stations and computing/formatting delays.
    """

    @classmethod 
    def add_stations_untracked(cls, station_data:pd.DataFrame, slinktool_data:pd.DataFrame):
        """
        Append stations missing from ``slinktool`` output to the tracked dataset.

        Filters ``station_data`` for rows whose ``('stid', 'channel')`` index
        pair does not appear in ``slinktool_data``, concatenates
        ``slinktool_data`` with those untracked rows, and casts ``'network'``,
        ``'stid'``, ``'loc'``, ``'channel'``, and ``'type_transmission'`` to
        ``string[pyarrow]``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            Reference station metadata DataFrame formatted by
            ``SiigeoFormatter`` and ``OtherStationsFormatter`` with columns
            ``'network'``, ``'stid'``, ``'loc'``, ``'channel'``,
            ``'type_transmission'``, and ``'last_connection'``.
        slinktool_data : pandas.DataFrame
            DataFrame of ``slinktool`` streams formatted by
            ``SlinktoolFormatter`` with columns ``'network'``, ``'stid'``,
            ``'loc'``, ``'channel'``, ``'type_transmission'``, and
            ``'last_connection'``.

        Returns
        -------
        pandas.DataFrame
            Concatenated DataFrame with a reset integer index and the columns
            ``'network'``, ``'stid'``, ``'loc'``, ``'channel'``, and
            ``'type_transmission'`` cast to ``string[pyarrow]``.

        Raises
        ------
        KeyError
            If ``'stid'`` or ``'channel'`` is missing from either input
            DataFrame, or if any of ``'network'``, ``'loc'``, or
            ``'type_transmission'`` is missing from the concatenated DataFrame.
        """
        cols = ['stid', 'channel']
        data = station_data[~station_data.set_index(cols).index.isin(slinktool_data.set_index(cols).index)]
        final_data = pd.concat([slinktool_data, data], ignore_index=True)
        cols2convert = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        final_data[cols2convert] = final_data[cols2convert].astype("string[pyarrow]")
        logger.info(Fore.GREEN + "Adding stations not tracked by slinktool succesfully!!" + Fore.RESET)            

        return final_data

    @classmethod
    def compute_delays(cls, stations_data:pd.DataFrame,  datetime: datetime, datetime_column:str, delay_column:str = 'delay'):
        """
        Compute elapsed time delays between a reference timestamp and station data.

        Converts ``datetime`` to ``numpy.datetime64`` and
        ``stations_data[datetime_column]`` to a NumPy datetime array, computes
        ``datetime - stations_data[datetime_column]`` as a ``pandas.Timedelta``
        series, and assigns it in-place to ``stations_data[delay_column]``.

        Parameters
        ----------
        stations_data : pandas.DataFrame
            Station DataFrame containing ``datetime_column``. Modified in-place
            by adding or updating ``delay_column``.
        datetime : datetime.datetime
            Naive reference timestamp (typically UTC with ``tzinfo=None``) from
            which station timestamps are subtracted.
        datetime_column : str
            Column name in ``stations_data`` storing the station timestamps
            (e.g., ``'last_connection'``).
        delay_column : str, default 'delay'
            Column name in ``stations_data`` where the computed timedelta
            values are stored.

        Returns
        -------
        pandas.DataFrame
            The ``stations_data`` DataFrame updated with ``delay_column``.

        Raises
        ------
        KeyError
            If ``datetime_column`` does not exist in ``stations_data``.
        ValueError
            If values in ``datetime_column`` cannot be converted by
            ``pandas.to_datetime``.
        """
        now_utc = np.datetime64(datetime)
        datetimes = pd.to_datetime(stations_data[datetime_column]).to_numpy()
        diff = pd.to_timedelta(now_utc - datetimes) 
        #diff = (now_utc - datetimes) / np.timedelta64(1, 's')
        stations_data[delay_column] = diff
        logger.info(Fore.GREEN + "Delays succesfully computed!!" + Fore.RESET)

        return stations_data
    
    #@classmethod
    #def compute_delays2(cls, stations_data:pd.DataFrame, datetime_column:str, delay_column:str = 'delay'):
    #    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    #    diff = now_utc - stations_data[datetime_column]
    #    stations_data[delay_column] = diff.dt.total_seconds()
    #
    #    return stations_data

    @classmethod
    def format_delays(cls, stations_data:pd.DataFrame, delay_column:str, delay_formatted_col:str = 'delay_'):
        """
        Format a timedelta column into ``'<days>d <hours>h <minutes>m <seconds>s'`` strings.

        Extracts timedelta components via
        ``stations_data[delay_column].dt.components`` and writes the formatted
        ``string[pyarrow]`` representation in-place to
        ``stations_data[delay_formatted_col]``.

        Parameters
        ----------
        stations_data : pandas.DataFrame
            Station DataFrame containing the timedelta column ``delay_column``.
            Modified in-place by adding or updating ``delay_formatted_col``.
        delay_column : str
            Name of the timedelta column in ``stations_data`` to format.
        delay_formatted_col : str, default 'delay_'
            Name of the output column storing formatted delay strings.

        Returns
        -------
        pandas.DataFrame
            The ``stations_data`` DataFrame updated with
            ``delay_formatted_col`` typed as ``string[pyarrow]``.

        Raises
        ------
        KeyError
            If ``delay_column`` does not exist in ``stations_data``.
        AttributeError
            If ``stations_data[delay_column]`` does not hold timedelta values
            compatible with the ``.dt.components`` accessor.
        """
        comp = stations_data[delay_column].dt.components
        stations_data[delay_formatted_col] = (
            comp['days'].astype("string[pyarrow]") + 'd ' +
            comp['hours'].astype("string[pyarrow]") + 'h ' +
            comp['minutes'].astype("string[pyarrow]") + 'm ' +
            comp['seconds'].astype("string[pyarrow]") + 's'
        )
        logger.info(Fore.GREEN + "Delays succesfully formatted!!" + Fore.RESET)

        return stations_data
    
if __name__ == "__main__":
    from src.data_access.load_data import StationRepository
    from src.data_access.slinktool_executor import SlinktoolExecutor
    from src.utilities.data_formatter import SiigeoFormatter, OtherStationsFormatter
    from src.utilities.slinktool_formatter import SlinktoolFormatter

    # Load stations data
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
    all_data = pd.concat([siigeo_data, shared_data, inter_data], ignore_index=True)

    # Load slinktool data 
    port = SlinktoolExecutor.get_port('91')
    comm = SlinktoolExecutor.build_command('91', port)
    output = SlinktoolExecutor.request_info(comm)
    solution = SlinktoolFormatter.extract_info(output)
    slink_data = SlinktoolFormatter.build_dataframe(solution)
    slink_data = SlinktoolFormatter.select_interest_channels(slink_data)
    slink_data = SlinktoolFormatter.assign_transmission(slink_data, all_data)
    slink_data = SlinktoolFormatter.order_cols(slink_data)

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        final_data = DelayCalculator.add_stations_untracked(all_data, slink_data)

    #print(len(final_data), final_data.columns)    
    print(final_data.loc[final_data['stid'] == 'YAVI3'])
    #print(final_data.dtypes)
    #print("Memory usaged:", final_data.memory_usage(deep=True).sum()/(1024**2), "MB")
    import time
    init_time = time.perf_counter()
    actual_time = datetime.now(UTC).replace(tzinfo=None)
    final_data = DelayCalculator.compute_delays(final_data, actual_time, 'last_connection')
    end_time = time.perf_counter()
    print(f"Method execution time: {end_time - init_time:.5f} seconds")
    print(final_data.loc[final_data['stid'] == 'YAVI3'])
    #print(DelayCalculator.format_delays(final_data, delay_column='delay'))
    #init_time = time.perf_counter()
    #print(DelayCalculator.compute_delays2(final_data, 'last_connection'))
    #end_time = time.perf_counter()
    #print(f"Method execution time: {end_time - init_time:.5f} seconds")