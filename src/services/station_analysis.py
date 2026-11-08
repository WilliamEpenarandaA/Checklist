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
    def count_stations_status(cls, stations_data:pd.DataFrame, status:str):
        return (stations_data['status'] == status).groupby(stations_data['stid']).any().sum()

    @classmethod
    def sensor_metrics(cls, stations_data:pd.DataFrame):

        ## Filter by instrument types
        seismo = stations_data.loc[stations_data['channel'].isin(settings.stations.SEISMOMETER_CHANNELS)]
        accel = stations_data.loc[stations_data['channel'].isin(settings.stations.ACCELEROMETER_CHANNELS)]
        strong = stations_data.loc[stations_data['channel'].isin(settings.stations.STRONG_MOTION_CHANNELS)]

        ## Filter by transmission types
        satellital = stations_data.loc[
            (stations_data['type_transmission'] == 'satelital') | 
            (stations_data['type_transmission'] == 'satelital leo')
            ]

        cellphone = stations_data.loc[stations_data['type_transmission'] == 'celular']
        radio = stations_data.loc[stations_data['type_transmission'] == 'radio']
        internet = stations_data.loc[stations_data['type_transmission'] == 'internet']
        
        ## Obtain connectivity metrics
        num_online = cls.count_stations_status(stations_data, status='Online')
        num_onseismo = cls.count_stations_status(seismo, status='Online')
        num_onaccel = cls.count_stations_status(accel, status='Online')
        num_onstrong = cls.count_stations_status(strong, status='Online')

        num_offline = (cls.count_stations_status(stations_data, status='Offline')) + (cls.count_stations_status(stations_data, status='N/A'))
        num_offseismo = (cls.count_stations_status(seismo, status='Offline')) + (cls.count_stations_status(seismo, status='N/A'))
        num_offaccel = (cls.count_stations_status(accel, status='Offline')) + (cls.count_stations_status(accel, status='N/A'))
        num_offstrong = (cls.count_stations_status(strong, status='Offline')) + (cls.count_stations_status(strong, status='N/A'))

        num_onsatellital = cls.count_stations_status(satellital, status='Online')
        num_oncellphone = cls.count_stations_status(cellphone, status='Online')
        num_oninternet = cls.count_stations_status(internet, status='Online')
        num_onradio = cls.count_stations_status(radio, status='Online')

        num_offsatellital = (cls.count_stations_status(satellital, status='Offline')) + (cls.count_stations_status(satellital, status='N/A'))
        num_offcellphone = (cls.count_stations_status(cellphone, status='Offline')) + (cls.count_stations_status(cellphone, status='N/A'))
        num_offinternet = (cls.count_stations_status(internet, status='Offline')) + (cls.count_stations_status(internet, status='N/A'))
        num_offradio = (cls.count_stations_status(radio, status='Offline')) + (cls.count_stations_status(radio, status='N/A'))
        
        ## Sensors type metrics
        num_total = len(stations_data['stid'].unique())
        num_seismo = len(stations_data.loc[stations_data['channel'].isin(settings.stations.SEISMOMETER_CHANNELS)]['stid'].unique())
        num_accel = len(stations_data.loc[stations_data['channel'].isin(settings.stations.ACCELEROMETER_CHANNELS)]['stid'].unique())
        num_strong = len(stations_data.loc[stations_data['channel'].isin(settings.stations.STRONG_MOTION_CHANNELS)]['stid'].unique())

        ## Total sensor and transmission types
        num_satellital = len(stations_data.loc[
            (stations_data['type_transmission'] == 'satelital') | 
            (stations_data['type_transmission'] == 'satelital leo')
            ]['stid'].unique())
        num_cellphone = len(stations_data.loc[stations_data['type_transmission'] == 'celular']['stid'].unique())
        num_internet = len(stations_data.loc[stations_data['type_transmission'] == 'internet']['stid'].unique())
        num_radio = len(stations_data.loc[stations_data['type_transmission'] == 'radio']['stid'].unique())
        
        results = {"online_stations": int(num_online),
                   "offline_stations": int(num_offline), 
                   "total_stations": int(num_total),
                   "online_seismometers": int(num_onseismo),
                   "offline_seismometers": int(num_offseismo),
                   "total_seismometers": int(num_seismo),
                   "online_accelerometers": int(num_onaccel),
                   "offline_accelerometers": int(num_offaccel),
                   "total_accelerometers": int(num_accel),
                   "online_strongmotion": int(num_onstrong),
                   "offline_strongmotion": int(num_offstrong),
                   "total_strongmotion": int(num_strong),
                   "online_satellital": int(num_onsatellital),
                   "offline_satellital": int(num_offsatellital),
                   "total_satellital": int(num_satellital),
                   "online_cellphone": int(num_oncellphone),
                   "offline_cellphone": int(num_offcellphone),
                   "total_cellphone": int(num_cellphone),
                   "online_internet": int(num_oninternet),
                   "offline_internet": int(num_offinternet),
                   "total_internet": int(num_internet),
                   "online_radio": int(num_onradio),
                   "offline_radio": int(num_offradio),
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
    dt = 20
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
