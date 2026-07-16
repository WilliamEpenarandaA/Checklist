# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to format information according to checklist document.

import pandas as pd
import re
from src.config import settings
from colorama import Fore

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

        ## According to Reina, C.; Uruena, A.; Lopez A.; suggestions
        shared_nat_stations = seismo_stations.loc[seismo_stations['stid'].isin(settings.stations.SHARED_NAT_ORDER)] 
        shared_nat_stations = shared_nat_stations.sort_values(by='stid', key=lambda x: x.map(settings.stations.SHARED_NAT_ORDER.index))
        seismo_stations = seismo_stations.loc[~seismo_stations['stid'].isin(settings.stations.SHARED_NAT_ORDER)].sort_values(by=['stid', 'loc'], ascending=[True, True])
        seismo_stations = pd.concat([seismo_stations, shared_nat_stations], ignore_index=True).reset_index(drop=True)

        # Order National Accelerograph stations according to checklist xlsx file
        accel_stations = stations_data.loc[(stations_data['channel'] == 'HNZ') | (stations_data['channel'] == 'HLZ')]
        accel_stations = accel_stations.sort_values(by=['stid', 'loc'], ascending=[True, True]).reset_index(drop=True)

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
        logger.info(Fore.GREEN + "Sucessfully extracted international stations!!" + Fore.RESET)

        return inter_stations

    @classmethod
    def get_color_status(cls, stations_data:pd.DataFrame, status_column:str = 'status'):
        stats = []
        for _, row in stations_data.iterrows():
            if row[status_column] == 'Online':
                color = Fore.GREEN
            elif row[status_column] == 'Recovering':
                color = Fore.MAGENTA
            elif row[status_column] == 'Offline':
                color = Fore.RED
            elif row[status_column] == 'Future':
                color = Fore.YELLOW
            else:
                color = Fore.RESET
            
            status_color = color + row[status_column] + Fore.RESET
            stats.append(status_color)

        stations_data[status_column] = stats
        logger.info(Fore.GREEN + "Station status color obtained sucessfully!!" + Fore.RESET)
        
        return stations_data
    
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

    final_data = DelayCalculator.compute_delays(final_data, 'last_connection')
    final_data = DelayCalculator.format_delays(final_data, delay_column='delay')
    final_data = StationAnalysis.get_station_status(final_data)
    seismo_stations, accel_stations, inter_stations = TableFormatter.order_stations_checklist(final_data, list(inter_data['stid']))
    seismo_stations = TableFormatter.get_display_table(seismo_stations, 'Seismological', mode=False)
    seismo_stations = TableFormatter.get_color_status(seismo_stations)
   
    print(f"\n{seismo_stations}")

    inter_stations = TableFormatter.extract_inter_stations(inter_data, inter_stations, settings.stations.INTER_PATTERN_CHANNELS)
    TableFormatter.export_csv_tables(inter_stations, settings.files.INTER_OUT_FILE)
    inter_stations = TableFormatter.get_display_table(inter_stations, 'International', mode=True)
    inter_stations = TableFormatter.get_color_status(inter_stations)
    print(f"\n{inter_stations}")
    #print(inter_stations['stid'].unique())

    