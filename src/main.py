## Author: William Eduardo Peñaranda Arévalo, Seismological Analyst at SGC <ORCID:0000-0002-8545-9181> <Github private repo:
## Formation: Geologist and M.Sc. in Geophysics at UIS
## This file contain the new routine to implement checklist of SGC stations.
####################################################################################################################################
####################################################################################################################################
import argparse
import concurrent.futures
import pandas as pd
import time
from network import Network
from wavetime import Wavetime
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
from tqdm import tqdm

## Initialize colorama, avoiding manually reset the text color each time
init(autoreset=True)
Style.RESET_ALL

## Define required functions
def run_calculations(station_info:pd.Series, mode:bool=False):
    """
    Function to perform calculations of last connection datetime an delay for a given station.

    Parameters:
    -----------
    station_info (Pd.Series): Station parameters. It should contain following information:
    (0) Station ID (str). For instance APAC.
    (1) Channel (str). For example HHZ. (Optional). Used in International and Shared stations 
    (2) Channel location (str). Allowed values are: 00, 10, 11, 20, 30, 40
    
    mode (bool). default false. Allow to activate channel input directly without infering from Channel location code.

    Return:
    -----------
    last_time (datetime): last UTC datetime connection of channel of station. For stations not tracked by
        slinktool module, was set as 1970-01-01 00:00:00 UTC.
    delay (float): delay in total seconds of channel of the correspond stations. Delay value was set as -99999
        for stations not tracking by slinktool module. 
    cha (str): string code of the correspond channel in station.
    """
    if station_info.empty:
        raise ValueError("Station info must be provided!!!")
    station_code = station_info['id']
    channel_code = station_info['channel_code']
    if mode:
        cha = station_info['channel']
    else:
        cha = network.assign_channel(station_code, channel_code)
    last_time = network.compute_last_times(server=server, port=port, station_code=station_code, channel=cha)
    delay = network.compute_delays(last_time)  
    return last_time, delay, cha

# Stablish allowed arguments for the routine
def read_args():
    prefix = '+'
    parser = argparse.ArgumentParser(prog="Checklistv2.0", description="Retrieve last connection datetime of stations managed in SGC.", prefix_chars=prefix)
    parser.add_argument(prefix + "p", prefix + "print", help="Print delay times in a readable format (dd HH MM SS).", action='store_true', required=False)
    parser.add_argument(prefix + "o", prefix + "output", help="Save the results on a .csv file. Only allowed for 91, 232 and 13 servers.", action='store_true', required=False)
    parser.add_argument(prefix + "u", prefix + "update", help="Update station information with Siigeo database", action='store_true', required=False)
    parser.add_argument(prefix + "s", prefix + "stat", help="Print statistics performance of National and International stations. Only allowed for 91, 232 and 13 servers.", action='store_true', required=False)
    parser.add_argument(prefix + "sn", prefix + "stat_nat", help="Print statistics performance of National stations", action='store_true', required=False)
    parser.add_argument(prefix + "n", prefix + "n_process", help="Number of process to use (recommended to reduce computation time), by default is setting only to one.", type=int, default=1, required=False)
    parser.add_argument(prefix + prefix + "offline", help="Show only offline stations.", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "recovering", help="Show only recovering stations.", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "online", help="Show only online stations.", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "wave", help="Compute delay times for stations not tracked by slinktool module. Only allowed in 232 server.", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "server", help="Define server to perform checklist process. Avalaible options are: 91, 232, 13, 97 and 2.", type=str, default='91', required=False)
    args_parser = parser.parse_args()
    vars_args = vars(args_parser)
    return vars_args

if __name__ == "__main__":
    ti = time.perf_counter()
    params = read_args()
    current_time = datetime.now()
    current_strtime = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Current system time: {current_strtime}")
    path = str(Path(__file__).absolute().parent.parent)
    data_path = str(Path(path, "data"))
    available_servers = ['232', '13', '97', '2', '91']

    ## Add a hard cap in number of process to avoid server memory collapse in parallel processing
    if params['n'] < 0 or not isinstance(params['n'], int):
        raise ValueError(Style.BRIGHT + Fore.LIGHTRED_EX + "Number of proccess must be a positive integer" + Fore.RESET)
    elif params['n'] > 10:
        raise ValueError(Style.BRIGHT + Fore.LIGHTRED_EX + "Number of process exceeds the limit of the server procesor. Please use a number of process less than 10" + Fore.RESET)
    else:
        print(Style.BRIGHT + Fore.LIGHTGREEN_EX + "Number of Process are according with server capacities" + Fore.RESET)

    ## Initialize Network class and download siigeo data
    if params['server'] and params['server'] not in available_servers:
        raise ValueError(Fore.LIGHTRED_EX + "Server not available to run checklist." + Fore.RESET)
    network = Network(data_path, server=params['server'])
    siigeo_file = network.download_siigeo_data(network.get_url, data_path, current_time, params['u'])
    shared_file = "shared_stations.json"
    inter_file = "inter_stations.json"
    df1, df2, df3 = network.load_data(data_path, siigeo_file, shared_file, inter_file)
    network.format_station_dataframes(df1, df2, df3)

    ## Define server IP and port to request the information
    server, port = network.define_server(network.server)
    if network.server not in ['232', '91']:
        stats = network.request_server_stations(server, port)
        network.filter_stations(stats)

    ## Calculate delay times for stations in siigeo, shared and international dataframes
    last_siigeo = []
    delays_siigeo = []
    cha_siigeo = []
    last_shared = []
    delays_shared = []
    cha_shared = []
    last_inter = []
    delays_inter = []
    cha_inter = []

    ## Loop over each dataframe and compute last connection times and delays
    if params['n'] == 1:
        for _, row in tqdm(network.siigeo_data.iterrows(), desc= Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of national stations' + Fore.RESET, total=len(network.siigeo_data), bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"):
            last_time, delay, cha = run_calculations(row)
            last_siigeo.append(last_time)
            delays_siigeo.append(delay)
            cha_siigeo.append(cha)
        for _, row in tqdm(network.shared_data.iterrows(), desc=Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of shared national stations' + Fore.RESET, total=len(network.shared_data), bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"):
            last_time, delay, cha = run_calculations(row, True)
            last_shared.append(last_time)
            delays_shared.append(delay)
            cha_shared.append(cha)
        for _, row in tqdm(network.inter_data.iterrows(), desc=Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of international stations' + Fore.RESET, total=len(network.inter_data), bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"):
            last_time, delay, cha = run_calculations(row, True)
            last_inter.append(last_time)
            delays_inter.append(delay)
            cha_inter.append(cha)
    else:
        ## Implementation of Parallel processing. Thanks to Garcia, K for his valuable explanations.
        with concurrent.futures.ProcessPoolExecutor(max_workers=params['n']) as executor:
            if len(network.siigeo_data) != 0:
                res = list(tqdm(executor.map(run_calculations, [row for _, row in network.siigeo_data.iterrows()]), total=len(network.siigeo_data),\
                                desc=Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of national stations' + Fore.RESET, bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"))
                last_siigeo, delays_siigeo, cha_siigeo = zip(*res)
                last_siigeo, delays_siigeo, cha_siigeo = list(last_siigeo), list(delays_siigeo), list(cha_siigeo) 
            if len(network.shared_data) != 0:
                res = list(tqdm(executor.map(run_calculations, [row for _, row in network.shared_data.iterrows()], [True]*len(network.shared_data)), total=len(network.shared_data),\
                                desc=Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of shared national stations' + Fore.RESET, bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"))
                last_shared, delays_shared, cha_shared = zip(*res)
                last_shared, delays_shared, cha_shared = list(last_shared), list(delays_shared), list(cha_shared)
            if len(network.inter_data) !=0:
                res = list(tqdm(executor.map(run_calculations, [row for _, row in network.inter_data.iterrows()], [True]*len(network.inter_data)), total=len(network.inter_data),\
                                desc=Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of international stations' + Fore.RESET, bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"))
                last_inter, delays_inter, cha_inter = zip(*res)
                last_inter, delays_inter, cha_inter = list(last_inter), list(delays_inter), list(cha_inter)
    
    ## Join the results into station dataframes
    network.compile_connection_information(last_siigeo, delays_siigeo, cha_siigeo, last_shared, delays_shared, cha_shared, last_inter, delays_inter, cha_inter)

    ## Get status of each station in National and International groups
    nat_data = pd.concat([network.siigeo_data, network.shared_data])
    prints, status = network.get_station_status(nat_data)
    nat_data['delay_readable'] = prints
    nat_data['status'] = status
    if network.server in ['232', '13', '91']:
        inter_data = network.inter_data
        prints, status = network.get_station_status(inter_data)
        inter_data['delay_readable'] = prints
        inter_data['status'] = status
    
    ## Separate National stations in Seismometers and Accelerometers
    seismo_nat_data = nat_data.loc[(nat_data['channel'] == 'HHZ') | (nat_data['channel'] == 'BHZ') | (nat_data['channel'] == 'EHZ')]
    accel_nat_data = nat_data.loc[(nat_data['channel'] == 'HNZ') | (nat_data['channel'] == 'HLZ')]

    ## Order stations by checklist defined format
    seismo_nat_data = network.order_seismo_stations(seismo_nat_data)
    accel_nat_data = network.order_accel_stations(accel_nat_data)
    if network.server in ['232', '13', '91']:
        inter_data = network.order_inter_stations(inter_data)

    ## Enable computation of delay times for stations not tracking by slinktool
    if params['wave'] and params['server'] == '232':
        wavetime = Wavetime(year=str(current_time.year), server=network.server)
        wpath = wavetime.define_storage_path(wavetime.year, wavetime.server)
        for ind, row in seismo_nat_data.iterrows():
            if row['status'] == "Station not tracking by slinktool":
                foldpath = wavetime.check_folder(server_path=wpath, network=row['network_code'], station=row['id'], channel=row['channel'])
                filepath = wavetime.get_last_wavefile(foldpath)
                endtime, delay = wavetime.get_delay(filepath, datetime.now())
                status, prints = wavetime.get_station_status(delay)
                seismo_nat_data.at[ind, 'last_connection'] = endtime
                seismo_nat_data.at[ind, 'delay_readable'] = prints
                seismo_nat_data.at[ind, 'status'] = status
        for ind, row in accel_nat_data.iterrows():
            if row['status'] == "Station not tracking by slinktool":
                foldpath = wavetime.check_folder(server_path=wpath, network=row['network_code'], station=row['id'], channel=row['channel'])
                filepath = wavetime.get_last_wavefile(foldpath)
                endtime, delay = wavetime.get_delay(filepath, datetime.now())
                status, prints = wavetime.get_station_status(delay)
                accel_nat_data.at[ind, 'last_connection'] = endtime
                accel_nat_data.at[ind, 'delay_readable'] = prints
                accel_nat_data.at[ind, 'status'] = status
        for ind, row in inter_data.iterrows():
            if row['status'] == "Station not tracking by slinktool":
                foldpath = wavetime.check_folder(server_path=wpath, network=row['network_code'], station=row['id'], channel=row['channel'])
                filepath = wavetime.get_last_wavefile(foldpath)
                endtime, delay = wavetime.get_delay(filepath, datetime.now())
                status, prints = wavetime.get_station_status(delay)
                inter_data.at[ind, 'last_connection'] = endtime
                inter_data.at[ind, 'delay_readable'] = prints
                inter_data.at[ind, 'status'] = status
        
    ## Apply arguments in the execution of the routine  
    if params['p']:
       cols = ['network_code', 'id', 'channel_code', 'channel', 'last_connection', 'delay_readable', 'status']
       seismo_nat_data = seismo_nat_data[cols]
       accel_nat_data = accel_nat_data[cols]
       if network.server in ['232', '13', '91']:
            inter_data = inter_data[cols]
    else:
        cols = ['network_code', 'id', 'channel_code', 'channel', 'last_connection', 'status']
        seismo_nat_data = seismo_nat_data[cols]
        accel_nat_data = accel_nat_data[cols]
        if network.server in ['232', '13', '91']:
            inter_data = inter_data[cols]
    if params['online'] and params['recovering']:
        seismo_nat_data = seismo_nat_data.loc[(seismo_nat_data['status'] != 'offline') | (seismo_nat_data['status'] != 'Station not tracking by slinktool')]
        accel_nat_data = accel_nat_data.loc[(accel_nat_data['status'] != 'offline') | (accel_nat_data['status'] != 'Station not tracking by slinktool')]
        if network.server in ['232', '13', '91']:
            inter_data = inter_data.loc[(inter_data['status'] != 'offline') | (inter_data['status'] != 'Station not tracking by slinktool')]    
    elif params['offline'] and params['recovering']:
        seismo_nat_data = seismo_nat_data.loc[(seismo_nat_data['status'] != 'online')]
        accel_nat_data = accel_nat_data.loc[accel_nat_data['status'] != 'online']
        if network.server in ['232', '13', '91']:
            inter_data = inter_data.loc[inter_data['status'] != 'online']
    elif params['online']:
        seismo_nat_data = seismo_nat_data.loc[seismo_nat_data['status'] == 'online']
        accel_nat_data = accel_nat_data.loc[accel_nat_data['status'] == 'online']
        if network.server in ['232', '13', '91']:
            inter_data = inter_data.loc[inter_data['status'] == 'online']
    elif params['recovering']:
        seismo_nat_data = seismo_nat_data.loc[seismo_nat_data['status'] == 'recovering']
        accel_nat_data = accel_nat_data.loc[accel_nat_data['status'] == 'recovering']
        if network.server in ['232', '13', '91']:
            inter_data = inter_data.loc[inter_data['status'] == 'recovering']
    elif params['offline']:
        seismo_nat_data = seismo_nat_data.loc[(seismo_nat_data['status'] == 'offline') | (seismo_nat_data['status'] == 'Station not tracking by slinktool')]
        accel_nat_data = accel_nat_data.loc[(accel_nat_data['status'] == 'offline') | (accel_nat_data['status'] == 'Station not tracking by slinktool')]
        if network.server in ['232', '13', '91']:
            inter_data = inter_data.loc[(inter_data['status'] == 'offline') | (inter_data['status'] == 'Station not tracking by slinktool')]
    else:
        seismo_nat_data = seismo_nat_data
        accel_nat_data = accel_nat_data
        if network.server in ['232', '13', '91']:
            inter_data = inter_data

    ## Configure a nice view for printing results
    seismo_nat_data = seismo_nat_data.rename(columns={'network_code':'network', 'channel_code': 'loc'})
    accel_nat_data = accel_nat_data.rename(columns={'network_code':'network', 'channel_code': 'loc'})
    if network.server in ['232', '13', '91']:
        inter_data = inter_data.rename(columns={'network_code':'network', 'channel_code': 'loc'})
    seismo_nat_data['status_'] = seismo_nat_data['status'].apply(Network.get_status_color)
    accel_nat_data['status_'] = accel_nat_data['status'].apply(Network.get_status_color)
    if network.server in ['232', '13', '91']:
        inter_data['status_'] = inter_data['status'].apply(Network.get_status_color)

    with pd.option_context('display.max_rows', None,
                            'display.precision', 1,
                            'display.colheader_justify', 'center',
                            ):
            print(Style.BRIGHT + Fore.LIGHTGREEN_EX + '\nDelay times for national seismological stations:' + Fore.RESET)
            print(seismo_nat_data.loc[:, seismo_nat_data.columns != 'status'])
            print(Style.BRIGHT + Fore.LIGHTGREEN_EX + '\nDelay times for national accelerometer stations:' + Fore.RESET)
            print(accel_nat_data.loc[:, accel_nat_data.columns != 'status'])
            if network.server in ['232', '13', '91']:
                print(Style.BRIGHT + Fore.LIGHTGREEN_EX + '\nDelay times for international stations:' + Fore.RESET)
                print(inter_data.loc[:, inter_data.columns != 'status'])

    ## Obtain connection performance of the stations
    if params['sn']:
        online_seismo, online_accel, online_nat, total_nat = network.get_nat_statistics(nat_data, seismo_nat_data, accel_nat_data)
        transmission_parameters = network.get_type_transmission(nat_data)
        print(Fore.LIGHTMAGENTA_EX + "\nNumber of national stations in real-time: " + Fore.LIGHTGREEN_EX + f"{online_nat}" + Fore.RESET + f" (N={total_nat})")
        print(Fore.LIGHTMAGENTA_EX + "Number of seismometers in real-time: " + Fore.LIGHTGREEN_EX + f"{online_seismo}" + Fore.RESET)
        print(Fore.LIGHTMAGENTA_EX + "Number of accelerometers in real-time: " + Fore.LIGHTGREEN_EX + f"{online_accel}" + Fore.RESET)
        print(Fore.LIGHTMAGENTA_EX + "Number of satelital stations in real-time: " + Fore.LIGHTGREEN_EX + f"{transmission_parameters[1]}" + Fore.RESET + f" (N={transmission_parameters[0]})")
        print(Fore.LIGHTMAGENTA_EX + "Number of celular stations in real-time: " + Fore.LIGHTGREEN_EX + f"{transmission_parameters[3]}" + Fore.RESET + f" (N={transmission_parameters[2]})")
        print(Fore.LIGHTMAGENTA_EX + "Number of internet stations in real-time: " + Fore.LIGHTGREEN_EX + f"{transmission_parameters[5]}" + Fore.RESET + f" (N={transmission_parameters[4]})")
        print(Fore.LIGHTMAGENTA_EX + "Number of radio stations in real-time: " + Fore.LIGHTGREEN_EX + f"{transmission_parameters[7]}" + Fore.RESET + f" (N={transmission_parameters[6]})")

    elif params['s'] and network.server in ['232', '13', '91']:
        online_nat, total_nat, online_inter, total_inter = network.get_station_statistics(nat_data, inter_data)
        print(Fore.LIGHTMAGENTA_EX + "\nNumber of national stations in real-time:" + Fore.LIGHTGREEN_EX + f" {online_nat}" + Fore.RESET + f" (N={total_nat})")
        print(Fore.LIGHTMAGENTA_EX + "Number of international stations in real-time:" + Fore.LIGHTGREEN_EX + f" {online_inter}" + Fore.RESET + f" (N={total_inter})")
    else:
         print(Fore.LIGHTBLUE_EX + "\nNot computing any connection statistics!!!" + Fore.RESET)

    ## Storage checklist results into csv files    
    if params['o'] and network.server in ['232', '13', '91']:
        seismo_fname = 'seismo_checklist.csv'
        accel_fname = 'accel_checklist.csv'
        inter_fname = 'inter_checklist.csv'
        network.save_checklist(seismo_nat_data, seismo_fname)
        network.save_checklist(accel_nat_data, accel_fname)
        network.save_checklist(inter_data, inter_fname)
    else:
        print(Fore.LIGHTBLUE_EX + "Not saving checklist results in correspond files!!!" + Fore.RESET)
    
    ## Print computing time spent on the checklist routine
    te = time.perf_counter()
    elapsed_time = te - ti
    print(Fore.LIGHTGREEN_EX + f"Checklist routine executed in {round(elapsed_time, 1)} seconds")
