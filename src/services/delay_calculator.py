# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to compute delays of SGC stations.

import numpy as np
import pandas as pd
from colorama import Fore
from src.config import settings
from datetime import datetime, timezone

logger = settings.get_logger(__name__)

class DelayCalculator:
    
    @classmethod
    def add_stations_untracked(cls, station_data:pd.DataFrame, slinktool_data:pd.DataFrame):
        for _, row in station_data.iterrows():
            if row['stid'] not in slinktool_data['stid'].values:
                row = row.to_frame().T
                final_data = pd.concat([slinktool_data, row], ignore_index=True)
        
        cols2convert = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        final_data[cols2convert] = final_data[cols2convert].astype("string[pyarrow]")
        logger.info(Fore.GREEN + "Adding stations not tracked by slinktool sucessfully!!" + Fore.RESET)

        return final_data

    @classmethod
    def compute_delays(cls, stations_data:pd.DataFrame, datetime_column:str, delay_column:str = 'delay'):
        now_utc = np.datetime64(datetime.now(timezone.utc).replace(tzinfo=None))
        datetimes = stations_data[datetime_column].to_numpy()
        diff = pd.to_timedelta(now_utc - datetimes) 
        #diff = (now_utc - datetimes) / np.timedelta64(1, 's')
        stations_data[delay_column] = diff
        logger.info(Fore.GREEN + "Delays sucessfully computed!!" + Fore.RESET)

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
        comp = stations_data[delay_column].dt.components
        stations_data[delay_formatted_col] = (
            comp['days'].astype("string[pyarrow]") + 'd ' +
            comp['hours'].astype("string[pyarrow]") + 'h ' +
            comp['minutes'].astype("string[pyarrow]") + 'm ' +
            comp['seconds'].astype("string[pyarrow]") + 's'
        )
        logger.info(Fore.GREEN + "Delays sucessfully formatted!!" + Fore.RESET)

        return stations_data
    

if __name__ == "__main__":
    from src.data_access.slinktool_executor import SlinktoolExecutor
    from src.data_access.load_data import StationRepository
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
    #print(final_data)
    #print(final_data.dtypes)
    #print("Memory usaged:", final_data.memory_usage(deep=True).sum()/(1024**2), "MB")
    #import time
    #init_time = time.perf_counter()
    final_data = DelayCalculator.compute_delays(final_data, 'last_connection')
    #end_time = time.perf_counter()
    #print(f"Method execution time: {end_time - init_time:.5f} seconds")

    print(DelayCalculator.format_delays(final_data, delay_column='delay'))
    #init_time = time.perf_counter()
    #print(DelayCalculator.compute_delays2(final_data, 'last_connection'))
    #end_time = time.perf_counter()
    #print(f"Method execution time: {end_time - init_time:.5f} seconds")