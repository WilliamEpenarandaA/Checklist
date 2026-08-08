# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to format information according to checklist document.

import re
import time
from colorama import Fore
from datetime import datetime, UTC
import numpy as np
import pandas as pd
from src.config import settings

logger = settings.get_logger(__name__)

class TableFormatter:
    
    @classmethod
    def order_stations_checklist(cls, stations_data: pd.DataFrame, inter_stations:list):
        # Order National Seismological stations according to checklist xlsx file
        seismo_stations = stations_data.loc[~stations_data['stid'].isin(inter_stations)]
        seismo_stations = seismo_stations.loc[
                        (seismo_stations['channel'] == 'HHZ') | 
                        (seismo_stations['channel'] == 'BHZ') | 
                        (seismo_stations['channel'] == 'EHZ')
                        ]

        shared_nat_stations = seismo_stations.loc[seismo_stations['stid'].isin(settings.stations.SHARED_NAT_ORDER)] 
        shared_nat_stations = shared_nat_stations.sort_values(by='stid', key=lambda x: x.map(settings.stations.SHARED_NAT_ORDER.index))
        seismo_stations = seismo_stations.loc[~seismo_stations['stid'].isin(settings.stations.SHARED_NAT_ORDER)].sort_values(by=['stid', 'loc'], ascending=[True, True])
        seismo_stations = pd.concat([seismo_stations, shared_nat_stations], ignore_index=True).reset_index(drop=True)
        seismo_stations = seismo_stations.loc[~seismo_stations['stid'].isin(inter_stations)]

        # Order National Accelerograph stations according to checklist xlsx file
        accel_stations = stations_data.loc[(stations_data['channel'] == 'HNZ') | (stations_data['channel'] == 'HLZ')]
        accel_stations = accel_stations.sort_values(by=['stid', 'loc'], ascending=[True, True]).reset_index(drop=True)
        accel_stations = accel_stations.loc[~accel_stations['stid'].isin(inter_stations)]

        # Order International stations according to checklist xlsx file
        inter_stations = stations_data.loc[stations_data['stid'].isin(inter_stations)]
        inter_stations = inter_stations.sort_values(by=['stid', 'loc'], ascending=[True, True]).reset_index(drop=True)
        logger.info(Fore.GREEN + "Station data ordered according to checklist!!" + Fore.RESET)

        return seismo_stations, accel_stations, inter_stations
    
    @classmethod
    def extract_inter_stations(cls, inter_data_sgc: pd.DataFrame, inter_stations: pd.DataFrame, channel_dict: dict):
        data = []
        for _, row in inter_data_sgc.iterrows():
            cha = inter_data_sgc.loc[inter_data_sgc['stid'] == row['stid'], 'channel'].item()
            pattern = rf'{channel_dict[cha]}'
            res = list(inter_stations.loc[inter_stations['stid'] == row['stid'], 'channel'])
            interest_channels = [item for item in res if re.search(pattern, item)]
            df = inter_stations[(inter_stations['stid'] == row['stid']) & (inter_stations['channel'].isin(interest_channels))]
            data.append(df)

        inter_stations = pd.concat(data, ignore_index=True)
        inter_stations = inter_stations[~((inter_stations['stid'].isin(settings.stations.SPECIAL_INTER_STATIONS)) & (inter_stations['loc'] == '10'))]
        inter_stations = inter_stations.sort_values(by=['stid', 'loc'], ascending=[True, True]).reset_index(drop=True)
        logger.info(Fore.GREEN + "succesfully extracted international stations!!" + Fore.RESET)

        return inter_stations

    @staticmethod
    def format_status(status_str: str):
        if status_str == 'Online':
            return Fore.GREEN + status_str + Fore.RESET
        elif status_str == 'Intermittent':
            return Fore.MAGENTA + status_str + Fore.RESET
        elif status_str == 'Offline':
            return Fore.RED + status_str + Fore.RESET
        elif status_str == 'Future':
            return Fore.YELLOW + status_str + Fore.RESET
        else:
            return Fore.RESET + status_str + Fore.RESET
    
    @classmethod
    def filter_vertical_components(cls, stations_data: pd.DataFrame, channel_col:str = 'channel'):
        stations_data = stations_data[stations_data[channel_col].isin(settings.stations.VERTICAL_SLINKTOOL_CHANNELS)].reset_index(drop=True)
        
        return stations_data

    @classmethod
    def get_display_table(cls, stations_data:pd.DataFrame, name:str, mode:bool):
        if mode:
            cols2print = ['network', 'stid', 'loc', 'channel', 'last_connection', 'delay_', 'status']
        else:
            cols2print = ['network', 'stid', 'loc', 'channel', 'last_connection', 'status']
        stations_data = stations_data[cols2print]
        stations_data = cls.filter_vertical_components(stations_data)
        logger.info(Fore.GREEN + f"{name} data succesfully formatted to display!!" + Fore.RESET)

        return stations_data
    
    @classmethod
    def export_csv_tables(cls, formatted_table: pd.DataFrame, output_filename: str, status_column:str = 'status', col_name:str = 'checklist'):
        formatted_table[col_name] = formatted_table[status_column].map(settings.files.SYMBOL_STATUS_CHECKLIST)
        cols2export = ['stid', 'channel', 'checklist']
        formatted_table = cls.filter_vertical_components(formatted_table)
        formatted_table[cols2export].to_csv(output_filename, sep=',', index=False)
        logger.info(Fore.GREEN + f"{output_filename} exported succesfully!!" + Fore.RESET)

        return True

if __name__ == '__main__':
    from src.data_access.slinktool_executor import SlinktoolExecutor
    from src.data_access.load_data import StationRepository
    from src.services.delay_calculator import DelayCalculator
    from src.services.station_analysis import StationAnalysis
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

    actual_time = datetime.now(UTC).replace(tzinfo=None)
    final_data = DelayCalculator.compute_delays(final_data, actual_time, 'last_connection')
    final_data = DelayCalculator.format_delays(final_data, delay_column='delay')
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

    seismo_stations, accel_stations, inter_stations = TableFormatter.order_stations_checklist(final_data2, list(inter_data['stid']))
    print(f"\n{seismo_stations}")

    inter_stations = TableFormatter.extract_inter_stations(inter_data, inter_stations, settings.stations.INTER_PATTERN_CHANNELS)
    TableFormatter.export_csv_tables(inter_stations, settings.files.INTER_OUT_FILE)
    inter_stations = TableFormatter.get_display_table(inter_stations, 'International', mode=True)
    inter_stations['status'] = inter_stations['status'].apply(TableFormatter.format_status)
    print(f"\n{inter_stations}")