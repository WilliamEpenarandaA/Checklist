# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to analyze status and performance metrics of SGC stations.

from colorama import Fore
from datetime import datetime, UTC
import numpy as np
import pandas as pd
from src.config import settings

logger = settings.get_logger(__name__)

class StationAnalysis:
    
    @classmethod
    def get_station_status(cls, delay1: np.array, delay2: np.array, dt:float):
        conditions = [(np.isnan(delay1)) & (np.isnan(delay2)),
                        (delay1 < 0) & (delay2 < 0),
                        (delay1 <= settings.thresholds.ONLINE_MAX_DELAY) & (delay2 - delay1 <= dt),
                        (delay1 <= settings.thresholds.ONLINE_MAX_DELAY) & (delay2 - delay1 > dt),
                        (delay1 > settings.thresholds.ONLINE_MAX_DELAY) & (delay2 - delay1 <= dt),
                        (delay1 > settings.thresholds.ONLINE_MAX_DELAY) & (delay2 - delay1 > dt)
        ]
        outputs = ["N/A", "Future", "Online", "Intermittent", "Intermittent", "Offline"]
        status = np.select(conditions, outputs, default='Error')
        logger.info(Fore.GREEN + "Station status determined succesfully!!" + Fore.RESET)
        has_error = 'Error' in status
        count = np.sum(status == 'Error')
        if has_error:
            logger.error(Fore.RED + f"There are {count} stations with Error status!!" + Fore.RESET)

        return status

    @classmethod
    def sensor_metrics(cls, stations_data:pd.DataFrame, status_column:str = 'status'):
        
        ## Sensors connectivity metrics
        num_online = len(stations_data.loc[stations_data[status_column] == 'Online']['stid'].unique())
        num_onseismo = len(stations_data.loc[
            (stations_data['channel'].isin(settings.stations.SEISMOMETER_CHANNELS)) & 
            (stations_data[status_column] == 'Online')
            ]['stid'].unique())
        num_onaccel = len(stations_data.loc[
            (stations_data['channel'].isin(settings.stations.ACCELEROMETER_CHANNELS)) & 
            (stations_data[status_column] == 'Online')
            ]['stid'].unique())
        num_onstrong = len(stations_data.loc[
            (stations_data['channel'].isin(settings.stations.STRONG_MOTION_CHANNELS)) & 
            (stations_data[status_column] == 'Online')
            ]['stid'].unique())
        num_onsatellital = len(stations_data.loc[
            (stations_data['type_transmission'] == 'satelital') | 
            (stations_data['type_transmission'] == 'satelital leo') &
            (stations_data[status_column] == 'Online')
            ]['stid'].unique())
        num_oncellphone = len(stations_data.loc[
            (stations_data['type_transmission'] == 'celular') &
            (stations_data[status_column] == 'Online')
            ]['stid'].unique())
        num_oninternet = len(stations_data.loc[
            (stations_data['type_transmission'] == 'internet') &
            (stations_data[status_column] == 'Online')
            ]['stid'].unique())
        num_onradio = len(stations_data.loc[
            (stations_data['type_transmission'] == 'radio') &
            (stations_data[status_column] == 'Online')
            ]['stid'].unique())
        
        ## Sensors type metrics
        num_total = len(stations_data['stid'].unique())
        num_seismo = len(stations_data.loc[stations_data['channel'].isin(settings.stations.SEISMOMETER_CHANNELS)]['stid'].unique())
        num_accel = len(stations_data.loc[stations_data['channel'].isin(settings.stations.ACCELEROMETER_CHANNELS)]['stid'].unique())
        num_strong = len(stations_data.loc[stations_data['channel'].isin(settings.stations.STRONG_MOTION_CHANNELS)]['stid'].unique())

        ## Transmission type metrics
        num_satellital = len(stations_data.loc[
            (stations_data['type_transmission'] == 'satelital') | 
            (stations_data['type_transmission'] == 'satelital leo')
            ]['stid'].unique())
        num_cellphone = len(stations_data.loc[stations_data['type_transmission'] == 'celular']['stid'].unique())
        num_internet = len(stations_data.loc[stations_data['type_transmission'] == 'internet']['stid'].unique())
        num_radio = len(stations_data.loc[stations_data['type_transmission'] == 'radio']['stid'].unique())
        
        results = {"online_stations": int(num_online), 
                   "total_stations": int(num_total),
                   "online_seismo": int(num_onseismo),
                   "total_seismo": int(num_seismo),
                   "online_accel": int(num_onaccel),
                   "total_accel": int(num_accel),
                   "online_strong": int(num_onstrong),
                   "total_strong": int(num_strong),
                   "online_satellital": int(num_onsatellital),
                   "total_satellital": int(num_satellital),
                   "online_cellphone": int(num_oncellphone),
                   "total_cellphone": int(num_cellphone),
                   "online_internet": int(num_oninternet),
                   "total_internet": int(num_internet),
                   "online_radio": int(num_onradio),
                   "total_radio": int(num_radio)
            }
        logger.info(Fore.GREEN + "Sensor metrics computed succesfully!!" + Fore.RESET)

        return results

if __name__ == '__main__':
    from src.data_access.slinktool_executor import SlinktoolExecutor
    from src.data_access.load_data import StationRepository
    from src.services.delay_calculator import DelayCalculator
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

    #Compute Delay Time
    actual_time = datetime.now(UTC).replace(tzinfo=None)
    final_data = DelayCalculator.compute_delays(final_data, actual_time, 'last_connection')
    final_data = DelayCalculator.format_delays(final_data, delay_column='delay')

    # Second validation of Delay Time
    import time
    dt = 30
    time.sleep(dt)
    output = SlinktoolExecutor.request_info(comm)
    solution = SlinktoolFormatter.extract_info(output)
    slink_data = SlinktoolFormatter.build_dataframe(solution)
    slink_data = SlinktoolFormatter.select_interest_channels(slink_data)
    slink_data = SlinktoolFormatter.assign_transmission(slink_data, all_data)
    slink_data = SlinktoolFormatter.order_cols(slink_data)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        final_data2 = DelayCalculator.add_stations_untracked(all_data, slink_data)
    actual_time = datetime.now(UTC).replace(tzinfo=None)
    final_data2 = DelayCalculator.compute_delays(final_data2, actual_time, 'last_connection')
    final_data2 = DelayCalculator.format_delays(final_data2, delay_column='delay')

    ## Extract delay columns
    delay1 = final_data['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
    delay2 = final_data2['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
    status = StationAnalysis.get_station_status(delay1, delay2, dt)
    final_data2['delay1_seconds'] = delay1
    final_data2['delay2_seconds'] = delay2
    final_data2['status'] = status
    print(final_data2)
    
    res = StationAnalysis.sensor_metrics(final_data2)
    print(res)