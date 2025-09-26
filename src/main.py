## Author: William Eduardo Peñaranda Arévalo, Seismological Analyst at SGC <ORCID:0000-0002-8545-9181> <Github private repo:
## Formation: Geologist and M.Sc. in Geophysics at UIS
## This file contain the new routine to implement checklist of SGC stations.
####################################################################################################################################
####################################################################################################################################
import argparse
import pandas as pd
from network import Network
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
from tqdm import tqdm

## Initialize colorama, avoiding manually reset the text color each time
init(autoreset=True)
Style.RESET_ALL

## Define allowed arguments for the routine
def read_args():
    prefix = '+'
    parser = argparse.ArgumentParser(prog="Checklistv2.0", description="Retrieve last connection datetime of stations managed in SGC", prefix_chars=prefix)
    parser.add_argument(prefix + "p", prefix + "print", help="Print delay times in a readable format (dd HH MM SS)", action='store_true', required=False)
    parser.add_argument(prefix + "o", prefix + "output", help="Save the results on a .csv file", action='store_true', required=False)
    parser.add_argument(prefix + "u", prefix + "update", help="Update station information with Siigeo database", action='store_true', required=False)
    parser.add_argument(prefix + "s", prefix + "stat", help="Print statistics performance of National and International stations", action='store_true', required=False)
    parser.add_argument(prefix + "sn", prefix + "stat_nat", help="Print statistics performance of National stations", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "server", type=str, help="Define the server to request the information. For e.g 232", required=False)
    parser.add_argument(prefix + prefix + "offline", help="Show only offline stations", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "recovering", help="Show only recovering stations", action='store_true', required=False)
    parser.add_argument(prefix + prefix + "online", help="Show only online stations", action='store_true', required=False)
    args_parser = parser.parse_args()
    vars_args = vars(args_parser)
    return vars_args

if __name__ == "__main__":
    params = read_args()
    current_time = datetime.now()
    current_strtime = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Current time (Local time): {current_strtime}")
    path = str(Path(__file__).absolute().parent.parent)
    data_path = str(Path(path, "data"))

    ## Initialize Network class and download siigeo data
    if params['server']:
        network = Network(data_path, server= params['server'])
    else:
        network = Network(data_path)

    siigeo_file = network.download_siigeo_data(network.get_url, data_path, current_time, params['u'])
    shared_file = "shared_stations.json"
    inter_file = "inter_stations.json"
    df1, df2, df3 = network.load_data(data_path, siigeo_file, shared_file, inter_file)
    network.format_station_dataframes(df1, df2, df3)

    ## Define server IP and port to request the information
    server, port = network.define_server(network.server)

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
    for _, row in tqdm(network.siigeo_data.iterrows(), desc= Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of national stations' + Fore.RESET, total=len(network.siigeo_data), bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"):
        station_code = row['id']
        channel_code = row['channel_code']
        cha = network.assign_channel(station_code, channel_code)
        last_time = network.compute_last_times(server=server, port=port, station_code=station_code, channel=cha)
        delay = network.compute_delays(datetime.now(), last_time)  
    # print(f"Station: {station_code}, Channel: {channel_code}, Delay: {delay}")
        last_siigeo.append(last_time)
        delays_siigeo.append(delay)
        cha_siigeo.append(cha)

    for _, row in tqdm(network.shared_data.iterrows(), desc=Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of shared national stations' + Fore.RESET, total=len(network.shared_data), bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"):
        station_code = row['id']
        channel_code = row['channel_code']
        cha = network.assign_channel(station_code, channel_code)
        last_time = network.compute_last_times(server=server, port=port, station_code=station_code, channel=cha)
        delay = network.compute_delays(datetime.now(), last_time)
    #    print(f"Station: {station_code}, Channel: {channel_code}, Delay: {delay}")
        last_shared.append(last_time)
        delays_shared.append(delay)
        cha_shared.append(cha)

    for _, row in tqdm(network.inter_data.iterrows(), desc=Style.BRIGHT + Fore.LIGHTGREEN_EX + 'Computing delay times of international stations' + Fore.RESET, total=len(network.inter_data), bar_format="{desc}: {bar:80} {percentage:.1f}% [{n_fmt}/{total}]"):
        station_code = row['id']
        channel_code = row['channel_code']
        cha = network.assign_channel(station_code, channel_code)
        last_time = network.compute_last_times(server=server, port=port, station_code=station_code, channel=cha)
        delay = network.compute_delays(datetime.now(), last_time)
    #    print(f"Station: {station_code}, Channel: {channel_code}, Delay: {delay}")
        last_inter.append(last_time)
        delays_inter.append(delay)
        cha_inter.append(cha)
    network.compile_connection_information(last_siigeo, delays_siigeo, cha_siigeo, last_shared, delays_shared, cha_shared, last_inter, delays_inter, cha_inter)
    
    ## Get status of each station in National and International groups
    nat_data = pd.concat([network.siigeo_data, network.shared_data])
    prints, status = network.get_station_status(nat_data)
    nat_data['delay_readable'] = prints
    nat_data['status'] = status
    inter_data = network.inter_data
    prints, status = network.get_station_status(inter_data)
    inter_data['delay_readable'] = prints
    inter_data['status'] = status
    
    ## Separate National stations in Seismometers and Accelerometers
    seismo_nat_data = nat_data.loc[(nat_data['channel'] == 'HHZ') | (nat_data['channel'] == 'Z') | (nat_data['channel'] == 'EHZ')]
    accel_nat_data = nat_data.loc[(nat_data['channel'] == 'HNZ') | (nat_data['channel'] == 'HLZ')]

    ## Order stations by checklist defined format
    seismo_nat_data = network.order_seismo_stations(seismo_nat_data)
    accel_nat_data = network.order_accel_stations(accel_nat_data)
    inter_data = network.order_inter_stations(inter_data)

    ## Apply arguments in the execution of the routine 
    if params['p']:
       cols = ['network_code', 'id', 'channel_code', 'channel', 'last_connection', 'delay_readable', 'status']
       seismo_nat_data = seismo_nat_data[cols]
       accel_nat_data = accel_nat_data[cols]
       inter_data = inter_data[cols] 

    else:
        cols = ['network_code', 'id', 'channel_code', 'channel', 'last_connection', 'status']
        seismo_nat_data = seismo_nat_data[cols]
        accel_nat_data = accel_nat_data[cols]
        inter_data = inter_data[cols]

    if params['online'] and params['recovering']:
        seismo_nat_data = seismo_nat_data.loc[(seismo_nat_data['status'] != 'offline') | (seismo_nat_data['status'] != 'Station not tracking by slinktool')]
        accel_nat_data = accel_nat_data.loc[(accel_nat_data['status'] != 'offline') | (accel_nat_data['status'] != 'Station not tracking by slinktool')]
        inter_data = inter_data.loc[(inter_data['status'] != 'offline') | (inter_data['status'] != 'Station not tracking by slinktool')]    
    elif params['offline'] and params['recovering']:
        seismo_nat_data = seismo_nat_data.loc[(seismo_nat_data['status'] != 'online')]
        accel_nat_data = accel_nat_data.loc[accel_nat_data['status'] != 'online']
        inter_data = inter_data.loc[inter_data['status'] != 'online']
    elif params['online']:
        seismo_nat_data = seismo_nat_data.loc[seismo_nat_data['status'] == 'online']
        accel_nat_data = accel_nat_data.loc[accel_nat_data['status'] == 'online']
        inter_data = inter_data.loc[inter_data['status'] == 'online']
    elif params['recovering']:
        seismo_nat_data = seismo_nat_data.loc[seismo_nat_data['status'] == 'recovering']
        accel_nat_data = accel_nat_data.loc[accel_nat_data['status'] == 'recovering']
        inter_data = inter_data.loc[inter_data['status'] == 'recovering']
    elif params['offline']:
        seismo_nat_data = seismo_nat_data.loc[(seismo_nat_data['status'] == 'offline') | (seismo_nat_data['status'] == 'Station not tracking by slinktool')]
        accel_nat_data = accel_nat_data.loc[(accel_nat_data['status'] == 'offline') | (accel_nat_data['status'] == 'Station not tracking by slinktool')]
        inter_data = inter_data.loc[(inter_data['status'] == 'offline') | (inter_data['status'] == 'Station not tracking by slinktool')]
    else:
        seismo_nat_data = seismo_nat_data
        accel_nat_data = accel_nat_data
        inter_data = inter_data

    ## Configure a nice view for printing results
    seismo_nat_data = seismo_nat_data.rename(columns={'network_code':'network', 'channel_code': 'loc'})
    accel_nat_data = accel_nat_data.rename(columns={'network_code':'network', 'channel_code': 'loc'})
    inter_data = inter_data.rename(columns={'network_code':'network', 'channel_code': 'loc'})
    seismo_nat_data['status_'] = seismo_nat_data['status'].apply(Network.get_status_color)
    accel_nat_data['status_'] = accel_nat_data['status'].apply(Network.get_status_color)
    inter_data['status_'] = inter_data['status'].apply(Network.get_status_color)

    with pd.option_context('display.max_rows', None,
                            'display.precision', 1,
                            'display.colheader_justify', 'center',
                            ):
            print(Style.BRIGHT + Fore.LIGHTGREEN_EX + '\nDelay times for national seismological stations:' + Fore.RESET)
            print(seismo_nat_data.loc[:, seismo_nat_data.columns != 'status'])
            print(Style.BRIGHT + Fore.LIGHTGREEN_EX + '\nDelay times for national accelerometer stations:' + Fore.RESET)
            print(accel_nat_data.loc[:, accel_nat_data.columns != 'status'])
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

    elif params['s']:
        online_nat, total_nat, online_inter, total_inter = network.get_station_statistics(nat_data, inter_data)
        print(Fore.LIGHTMAGENTA_EX + "\nNumber of national stations in real-time:" + Fore.LIGHTGREEN_EX + f" {online_nat}" + Fore.RESET + f" (N={total_nat})")
        print(Fore.LIGHTMAGENTA_EX + "Number of international stations in real-time:" + Fore.LIGHTGREEN_EX + f" {online_inter}" + Fore.RESET + f" (N={total_inter})")
    else:
         print(Fore.LIGHTBLUE_EX + "\nNot computing any connection statistics!!!" + Fore.RESET)

    ## Storage checklist results into csv files    
    if params['o']:
        seismo_fname = 'seismo_checklist.csv'
        accel_fname = 'accel_checklist.csv'
        inter_fname = 'inter_checklist.csv'
        network.save_checklist(seismo_nat_data, seismo_fname)
        network.save_checklist(accel_nat_data, accel_fname)
        network.save_checklist(inter_data, inter_fname)
    else:
        print(Fore.LIGHTBLUE_EX + "Not storaging checklist results in files!!!" + Fore.RESET)

    elapsed_time = (datetime.now() - current_time).total_seconds()
    print(Fore.LIGHTGREEN_EX + f"Checklist routine executed in {round(elapsed_time, 1)} seconds")