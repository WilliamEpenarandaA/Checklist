## Author: William Eduardo Peñaranda Arévalo, Seismological Analyst at SGC <ORCID:0000-0002-8545-9181> 
## <Repo:https://github.com/WilliamEpenarandaA/Checklist>
## This file contain the new routine to implement checklist of seismological stations monitored by SGC.
####################################################################################################################################
####################################################################################################################################
import argparse
import os 
import sys
import time
import warnings

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from colorama import Fore, Style, init
from datetime import datetime, UTC
import numpy as np
import pandas as pd
from tqdm import tqdm
from src.config import settings
from src.data_access.load_data import StationRepository
from src.data_access.slinktool_executor import SlinktoolExecutor
from src.services.delay_calculator import DelayCalculator
from src.services.station_analysis import StationAnalysis
from src.utilities.data_formatter import SiigeoFormatter, OtherStationsFormatter
from src.utilities.slinktool_formatter import SlinktoolFormatter
from src.utilities.table_formatter import TableFormatter

## Initialize colorama, avoiding manually reset the text color each time
init(autoreset=True)
Style.RESET_ALL

logger = settings.get_logger(__name__)

## Define function to parse arguments
def read_args():
    prefix = '+'
    parser = argparse.ArgumentParser(prog="Checklist", description="Find the last recorded connection time of seismological stations monitored by SGC.", prefix_chars=prefix)
    parser.add_argument(prefix + "p", prefix + "print", help="Display delays in a user-friendly manner (day, hour, minute, seconds).", action='store_true', required=False)
    parser.add_argument(prefix + "o", prefix + "output", help="Export results as csv files.", action='store_true', required=False)
    parser.add_argument(prefix + "u", prefix + "update", help="Integrate station updates from the Siigeo database", action='store_true', required=False)
    parser.add_argument(prefix + "s", prefix + "stat", help="Present performance metrics by sensor types.", action='store_true', required=False)
    parser.add_argument(prefix + "st", prefix + "stat_type", help="Present performance metrics categorized by transmission type.", action='store_true', required=False)
    parser.add_argument(prefix + "t", prefix + "time", help="Re-validate stations status after a specified time interval in seconds.", type=int, default=30, required=False)
    parser.add_argument(prefix + prefix + "offline", help="Show stations with offline status.", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "intermittent", help="Show stations with intermittent status.", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "online", help="Show stations with online status.", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "server", help="Define server to perform checklist. Avalaible options are: 91, 95, 232, 13, 97 and 2.", type=str, default='91', required=False)
    args_parser = parser.parse_args()
    vars_args = vars(args_parser)

    return vars_args

if __name__ == "__main__":
    ti = time.perf_counter()
    params = read_args()

    # Load stations data
    siigeo_data = StationRepository.get_siigeo_stations(params['u'])
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
    port = SlinktoolExecutor.get_port(params['server'])
    comm = SlinktoolExecutor.build_command(params['server'], port)
    output = SlinktoolExecutor.request_info(comm)
    solution = SlinktoolFormatter.extract_info(output)
    slink_data = SlinktoolFormatter.build_dataframe(solution)
    slink_data = SlinktoolFormatter.select_interest_channels(slink_data)
    slink_data = SlinktoolFormatter.assign_transmission(slink_data, all_data)
    slink_data = SlinktoolFormatter.order_cols(slink_data)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        final_data = DelayCalculator.add_stations_untracked(all_data, slink_data)

    # Compute delays of the stations
    actual_time = datetime.now(UTC).replace(tzinfo=None)
    final_data = DelayCalculator.compute_delays(final_data, actual_time, 'last_connection')
    final_data = DelayCalculator.format_delays(final_data, delay_column='delay')

    # Second validation of Delay Time
    dt = params['t']
    if dt <= 15:
        logger.debug(Fore.RED + "Selected time difference can produce inconsistent results!!" + Fore.RESET)

    with tqdm(total=dt, desc=f"Waiting {dt} seconds to execute a new validation") as pbar:
        for _ in range(dt):
            time.sleep(1)
            pbar.update(1)

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

    # Extract delay columns and determine status
    delay1 = final_data['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
    delay2 = final_data2['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
    status = StationAnalysis.get_station_status(delay1, delay2, dt)
    final_data2['status'] = status    

    # Extract previous last connection and add into the second dataframe
    lt1 = final_data['last_connection']
    final_data2['_last_connection'] = lt1

    # Compute performance metrics
    stats = StationAnalysis.sensor_metrics(final_data2) 

    # Separate stations into three groups
    seismo_stations, accel_stations, inter_stations = TableFormatter.order_stations_checklist(final_data2, list(inter_data['stid']))
    inter_stations = TableFormatter.extract_inter_stations(inter_data, inter_stations, settings.stations.INTER_PATTERN_CHANNELS)

    # Save results if it's enabled
    if params['o']:
        TableFormatter.export_csv_tables(seismo_stations, settings.files.SEISMO_OUT_FILE)
        TableFormatter.export_csv_tables(accel_stations, settings.files.ACCEL_OUT_FILE)
        TableFormatter.export_csv_tables(inter_stations, settings.files.INTER_OUT_FILE)

    # Stablish allowed status to be displayed
    allowed_status = ['Online', 'Intermittent', 'Offline', 'N/A', 'Future', 'Error']
    display_status = []
    if params['online']:
        display_status.append('Online')
        display_status.append('Future')
    
    if params['intermittent']:
        display_status.append('Intermittent')
    
    if params['offline']:
        display_status.append('Offline')
        display_status.append('N/A')
        display_status.append('Error')

    if not allowed_status:
        logger.critical(Fore.RED + "Error declaring allowed status to be displayed!!!" + Fore.RESET)
        raise ValueError(Fore.LIGHTRED_EX + "Status not declared as a variable, stopping programm!!!" + Fore.RESET)
    
    if not display_status:
        seismo_stations = seismo_stations.loc[seismo_stations['status'].isin(allowed_status)]
        accel_stations = accel_stations.loc[accel_stations['status'].isin(allowed_status)]
        inter_stations = inter_stations.loc[inter_stations['status'].isin(allowed_status)]
    
    else:
        seismo_stations = seismo_stations.loc[seismo_stations['status'].isin(display_status)]
        accel_stations = accel_stations.loc[accel_stations['status'].isin(display_status)]
        inter_stations = inter_stations.loc[inter_stations['status'].isin(display_status)]

    # Format dataframe results to be displayed in terminal
    _seismo_stations = TableFormatter.get_display_table(seismo_stations, 'Seismological', mode=params['p'])
    _seismo_stations['status'] = _seismo_stations['status'].apply(TableFormatter.format_status)
    _accel_stations = TableFormatter.get_display_table(accel_stations, 'Acelerographic', mode=params['p'])
    _accel_stations['status'] = _accel_stations['status'].apply(TableFormatter.format_status)
    _inter_stations = TableFormatter.get_display_table(inter_stations, 'International', mode=params['p'])
    _inter_stations['status'] = _inter_stations['status'].apply(TableFormatter.format_status)
    logger.info(Fore.GREEN + "Station status formatted succesfully!!" + Fore.RESET)

    with pd.option_context('display.max_rows', None,
                            'display.precision', 1,
                            'display.colheader_justify', 'center',
                            ):
        print(Fore.LIGHTGREEN_EX + '\nDelay times for National Seismological stations:' + Fore.RESET)
        print(_seismo_stations)
        print(Fore.LIGHTGREEN_EX + '\nDelay times for National Acelerometer stations:' + Fore.RESET)
        print(_accel_stations)
        print(Fore.LIGHTGREEN_EX + '\nDelay times for International stations:' + Fore.RESET)
        print(_inter_stations)

    if params['s']:
        print(f"""\nStations in real-time: {stats['online_stations']} (n={stats['total_stations']})
Seismometers in real-time: {stats['online_seismo']} (n={stats['total_seismo']})
Acelerometers in real-time: {stats['online_accel']} (n={stats['total_accel']})
Strong-motion sensors in real-time: {stats['online_strong']} (n={stats['total_strong']})""")
    
    if params['st']:
        print(f"""\nSensors in real-time: {stats['online_stations']} (n={stats['total_stations']})
Satellital sensors in real-time: {stats['online_satellital']} (n={stats['total_satellital']})
Cellphone sensors in real-time: {stats['online_cellphone']} (n={stats['total_cellphone']})
Radio sensors in real-time: {stats['online_radio']} (n={stats['total_radio']})""")

    ## Print computing time spent on the checklist routine
    te = time.perf_counter()
    elapsed_time = te - ti
    print(Fore.LIGHTGREEN_EX + f"\nChecklist routine executed in {round(elapsed_time, 3)} seconds" + Fore.RESET)
