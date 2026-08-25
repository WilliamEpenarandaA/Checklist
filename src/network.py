## Author: William Eduardo Peñaranda Arévalo, Seismological Analyst at SGC <ORCID:0000-0002-8545-9181> <Github private repo:
## Formation: Geologist and M.Sc. in Geophysics at UIS
## This file contain network class required to execute checklist of SGC stations.
####################################################################################################################################
####################################################################################################################################
import json
import pandas as pd
import requests
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
from colorama import Fore, Style

def measure_time(func):
    def wrapper(*args, **kwargs):
        init_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - init_time
        print(f"Method {func.__name__} execution time: {elapsed_time:.5f} seconds")
        return result
    return wrapper

class Network:
    def __init__(self, data_path: str, url:str = 'https://siigeo.sgc.gov.co/stations/stationExcelCodLocation/', server:str = '232'):
        """
            Constructor of Network Class

            Args:
                data_path (str): Path to the directory where data files will be stored. Defaults to '../data/'.
                url (str): URL of Siigeo intranet service. By default is defined by: https://siigeo.sgc.gov.co/stations/stationExcelCodLocation/
                server (str): IP server to request the information.

            Raises:
                ValueError: Trigger if:
                -data_path is not a valid str. 
                -url is not a valid string.
                -server is not a valid str.

            Examples:
                >>> Network(data_path="../data/", url="https://siigeo.sgc.gov.co/stations/stationExcelCodLocation/", server='232')
        """
        if not Path(data_path).is_dir():
            raise ValueError(Fore.LIGHTRED_EX + "Provided data folder no exist." + Fore.RESET)
        self.data_path = data_path
        if not url or not isinstance(url, str):
            raise ValueError(Fore.LIGHTRED_EX + "URL must be a valid string." + Fore.RESET)
        if not server or not isinstance(server, str):
            raise ValueError(Fore.LIGHTRED_EX + "Server must be a valid string" + Fore.RESET)
        self.__url = url
        self.siigeo_data = pd.DataFrame()
        self.shared_data = pd.DataFrame()
        self.inter_data = pd.DataFrame()
        self.server = server
        
    @property
    def get_url(self):
        return self.__url
    
    @get_url.setter
    def set_url(self, url: str):
        self.__url = url
 
    def define_server(self, server:str):
        """
        Function to define server ip and port to request the information.

        Parameters:
        -----------
        server (str): Server IP, stored in a instance variable.

        Return:
        -----------
        server (str): Last digits of server IP
        port (str): Digit of the port for the correspond server IP.
        """
        server_dict = {"232":"16501", "13":"16501", "97":"18000", "2":"18000", "91":"18000", "95":"18000"}
        port = server_dict[server]
        if server != '2':
            server = '100.' + server
        else:
            server = '101.' + server
        return server, port
    
    def request_server_stations(self, server:str, port:str):
        """
        Function to request stations which are sending information to a particular server.
        
        Parameters:
        -----------
        server (str): Last two groups of three digits of server ip.
        port (str): port number to connect to the server.

        Return:
        -----------
        output (list): Station list which are in the given server.
        """
        command = f"slinktool -Q 10.100.{server}:{port} | awk -F' ' '!seen[$2]++' |" + " awk '{print $2}'"
        result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        output = result.stdout.splitlines()
        return output
 
    def download_siigeo_data(self, url:str, data_path: str, current_time: datetime, action:bool):
        """
        Function to download the information of stations in Siigeo intranet service.

        Parameters:
        -----------
        data_path (str): Path to the directory where data files will be stored. Defaults to '../data/'.
        url (str): URL of Siigeo intranet service.
        current time in a datetime object.
        action (bool): True or False    
        
        Return:
        -----------
        filename(str) with station information downloaded from Siigeo intranet service. 
        """
        filename = "siigeo_stations.xlsx"
        file_path = Path(data_path, filename)

        if file_path.is_file():
            ti_m = file_path.stat().st_mtime #In Linux systems, created and modification is the same due to every time file is open count as modified
            m_ti = datetime.fromtimestamp(ti_m)
            dt = (current_time - m_ti).total_seconds()

            if dt > 30*86400 or action: # 30 days in seconds
                print(Fore.LIGHTBLUE_EX + "Refreshing stations information from siigeo!!!" + Fore.RESET)
                response = requests.get(url, verify=None)
                open(file_path, 'wb').write(response.content)
        
        else:
            print(Fore.LIGHTBLUE_EX + "Downloading stations information from siigeo!!!" + Fore.RESET)
            response = requests.get(url, verify=None)
            open(file_path, 'wb').write(response.content)

        return filename

    def load_data(self, data_path: str, nat_stations_filename: str, shared_stations_filename: str, inter_stations_filename: str):
        """
        Function to load the information of national and international stations.

        Parameters:
        -----------
        data_path (str): Path to the directory where data files will be stored. Defaults to '../data/'.
        nat_stations_filename (str): filename with information of national stations from Siigeo intranet service.
        shared_stations_filename (str): filename with information of shared national stations.
        inter_stations_filename (str): filename with information of international stations.    
        
        Return:
        -----------
        siigeo_data (Pd.DataFrame): Dataframe with the information of national stations from Siigeo intranet service.
        shared_data (Pd.DataFrame): Dataframe with the information of shared national stations.
        inter_data (Pd.DataFrame): Dataframe with the information of international stations. 
        """
        if not Path(data_path, nat_stations_filename).is_file():
            raise ValueError(Fore.LIGHTRED_EX + "Provided National data file no exist." + Fore.RESET)
        siigeo_data = pd.read_excel(Path(data_path, nat_stations_filename), dtype={'CÓDIGO LOCALIZACION':str})
        cols = ['IDENTIFICADOR', 'NOMBRE', 'ESTADO ESTACIÓN', 'CÓDIGO LOCALIZACION', 'ESTADO COD LOC.',\
            'TIPO DE TRANSMISIÓN', 'TIPO DE ESTACIÓN', 'TIPO DE ADQUISICIÓN']
        siigeo_data = siigeo_data[cols]
        if not Path(data_path, shared_stations_filename).is_file():
            raise ValueError(Fore.LIGHTRED_EX + "Provided Shared data file no exist." + Fore.RESET)
        with open(Path(data_path, shared_stations_filename), 'r') as file:
            shared_data = json.load(file)
        shared_data = pd.DataFrame.from_dict(shared_data)
        shared_data = shared_data.astype(dtype={"CODIGO CANAL":str})
        if not Path(data_path, inter_stations_filename).is_file():
            raise ValueError(Fore.LIGHTRED_EX + "Provided International data file no exist." + Fore.RESET)
        with open(Path(data_path, inter_stations_filename), 'r') as file:
            inter_data = json.load(file)
        inter_data = pd.DataFrame.from_dict(inter_data)

        return siigeo_data, shared_data, inter_data
    
    def format_station_dataframes(self, siigeo_data: pd.DataFrame, shared_data: pd.DataFrame, inter_data: pd.DataFrame):
        """
        Function to process and filter information of national, shared and international stations.

        Parameters:
        -----------
        siigeo_data (Pd.DataFrame): Dataframe with the information of national stations from Siigeo intranet service.
        shared_data (Pd.DataFrame): Dataframe with the information of shared national stations.
        inter_data (Pd.DataFrame): Dataframe with the information of international stations.  
        
        Return:
        -----------
        self.siigeo_data (Pd.DataFrame): Instance with filtered information of national stations from Siigeo intranet service.
        self.shared_data (Pd.DataFrame): Instance with filtered information of shared national stations.
        self.inter_data (Pd.DataFrame): Instance with filtered information of international stations. 
        """
        if siigeo_data.empty or not isinstance(siigeo_data, pd.DataFrame):
            raise ValueError(Fore.LIGHTRED_EX + "Siigeo data must be provided in a valid dataframe!!!" + Fore.RESET)
        siigeo_data = siigeo_data.rename(columns={'IDENTIFICADOR':'id', 'NOMBRE':'name', 'ESTADO ESTACIÓN':'station_status',\
            'CÓDIGO LOCALIZACION':'channel_code', 'ESTADO COD LOC.':'channel_status',\
            'TIPO DE TRANSMISIÓN':'type_transmission', 'TIPO DE ESTACIÓN':'type_station',\
            'TIPO DE ADQUISICIÓN':'type_adquissition'})
        
        ## Assign correct data types in each column of siigeo_dataframe
        siigeo_data['channel_code'] = siigeo_data['channel_code'].fillna('').astype(str)
        siigeo_data['station_status'] = siigeo_data['station_status'].astype(str).str.lower()
        siigeo_data['type_transmission'] = siigeo_data['type_transmission'].astype(str).str.lower()
        siigeo_data['type_station'] = siigeo_data['type_station'].astype(str).str.lower()
        siigeo_data['type_adquissition'] = siigeo_data['type_adquissition'].astype(str).str.lower()

        ## Include network code as a column in siigeo_dataframe
        siigeo_data['network_code'] = 'CM'
        siigeo_data= siigeo_data.loc[(siigeo_data['station_status'] == 'activa')] ## Dropping retired stations
        siigeo_data = siigeo_data.loc[(siigeo_data['type_adquissition'] != 'descarga')]  ## Ignoring stations that don't have real-time data transmission

        if shared_data.empty or not isinstance(shared_data, pd.DataFrame):
            raise ValueError(Fore.LIGHTRED_EX + "Shared data must be provided in a valid dataframe." + Fore.RESET)
        shared_data = shared_data.rename(columns={'IDENTIFICADOR':'id', 'NOMBRE':'name', 'ESTADO ESTACIÓN':'station_status',\
            'CODIGO RED': 'network_code', 'CODIGO SENSOR': 'channel', 'CODIGO CANAL':'channel_code', 'ESTADO ESTACION':'station_status',\
            'TIPO DE TRANSMISION':'type_transmission', 'TIPO DE ADQUISICION':'type_adquissition'})
        
        ## Assign correct data types in each column of shared_dataframe
        shared_data['channel'] = shared_data['channel'].fillna('').astype(str)
        shared_data['channel_code'] = shared_data['channel_code'].fillna('').astype(str)
        shared_data['network_code'] = shared_data['network_code'].fillna('').astype(str)
        shared_data['station_status'] = shared_data['station_status'].astype(str).str.lower()
        shared_data['type_transmission'] = shared_data['type_transmission'].astype(str).str.lower()
        shared_data['type_adquissition'] = shared_data['type_adquissition'].astype(str).str.lower()

        if inter_data.empty or not isinstance(inter_data, pd.DataFrame):
            raise ValueError(Fore.LIGHTRED_EX + "International data is empty." + Fore.RESET)
        inter_data = inter_data.rename(columns={'IDENTIFICADOR':'id', 'NOMBRE':'name',\
            'CODIGO RED': 'network_code', 'CODIGO SENSOR': 'channel', 'CODIGO CANAL':'channel_code', 'ESTADO ESTACION':'station_status',\
            'TIPO DE TRANSMISION':'type_transmission', 'TIPO DE ADQUISICION':'type_adquissition'})

        ## Assign correct data types in each column of inter_dataframe
        inter_data['channel'] = inter_data['channel'].fillna('').astype(str)
        inter_data['channel_code'] = inter_data['channel_code'].fillna('').astype(str)
        inter_data['network_code'] = inter_data['network_code'].fillna('').astype(str)
        inter_data['station_status'] = inter_data['station_status'].astype(str).str.lower()
        inter_data['type_transmission'] = inter_data['type_transmission'].astype(str).str.lower()
        inter_data['type_adquissition'] = inter_data['type_adquissition'].astype(str).str.lower()

        ## Subset dataframes to only include relevant columns and store them in the instance
        print(Style.BRIGHT + Fore.LIGHTGREEN_EX + "Dataframes formatted successfully!!!" + Style.RESET_ALL)
        self.siigeo_data = siigeo_data[['network_code', 'id', 'channel_code', 'type_transmission']]
        self.shared_data = shared_data[['network_code', 'id', 'channel', 'channel_code', 'type_transmission']]
        self.inter_data = inter_data[['network_code', 'id', 'channel', 'channel_code', 'type_transmission']]
        return True
  
    def filter_stations(self, stations:list):
        """
        Function to filter stations from siigeo, shared and international files which are in the given server.
        
        This function modify following atributes of the class: self.siigeo, self.shared and self.inter data.  

        Parameters:
        -----------
        stations (list): Station list that are sending information in the given server.

        Return:
        -----------
        bool: T.
        """
        if not stations or not isinstance(stations, list):
            raise ValueError(Fore.LIGHTRED_EX + "Not provided stations in server or in a format different to a list." + Fore.RESET)
        self.siigeo_data = self.siigeo_data[self.siigeo_data['id'].isin(stations)]
        self.shared_data = self.shared_data[self.shared_data['id'].isin(stations)]
        self.inter_data = self.inter_data[self.inter_data['id'].isin(stations)]
        return True

    def assign_channel(self, station_code: str, channel_code: str):
        """
        Function to assing string code to channel of the correspond station.

        Parameters:
        -----------
        station_code(str): ID of station
        channel_code(str): numeric code of correspond channel in station  
        
        Return:
        -----------
        channel (str): string code of the correspond channel in station.
        """
        ## Map channel codes to string representations. Declare special cases.
        channel_strcode = {'': 'Z', '00':'HHZ', '01': 'HHZ', '10':'HNZ', '11':'HNZ', '20':'EHZ', '30':'HHZ', '40':'HLZ'}
        if channel_code not in channel_strcode:
            raise KeyError(Fore.LIGHTRED_EX + "Invalid channel code provided." + Fore.RESET)
        if station_code == 'ROSC' and channel_code == '':
            channel = 'BHZ'
        else:
            channel = channel_strcode[channel_code]
        return channel
 
    def compute_last_times(self, server:str, port:str, station_code:str, channel:str):
        """
        Function to compute channel last connection in channel of the correspond station.

        Parameters:
        -----------
        server(str): two last codes of server
        port(str): port to connect
        station_code(str): ID of station  
        channel (str): string code of correspond channel in station.
        
        Return:
        -----------
        last_connection (datetime): last UTC datetime connection of channel of station. For stations not tracked by
        slinktool module, was set as 1970-01-01 00:00:00 UTC.
        """
        special_inter_stations = ['JTS', 'SDV']
        if server != '91':
            if station_code in special_inter_stations:    
                command = f"slinktool -Q 10.100.{server}:{port} | grep -w {station_code} | grep -w {channel} | grep 00"
            else:
                command = f"slinktool -Q 10.100.{server}:{port} | grep -w {station_code} | grep -w {channel}"
        else:
            if station_code in special_inter_stations:
                command = f"slinktool -Q 10.100.{server} | grep -w {station_code} | grep -w {channel} | grep 00"
            else:
                command = f"slinktool -Q 10.100.{server} | grep -w {station_code} | grep -w {channel}"

        result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        if result.returncode != 0:
            #print(Style.BRIGHT + Fore.LIGHTRED_EX + f"No output from Slinktool, asignning a default value last connection to 1970-01-01 00:00:00.0, please check if {station_code} {channel} exists!!" + Style.RESET_ALL)
            return datetime(1970, 1, 1, 0, 0, 0, 0)
        
        output = "".join(result.stdout).split()
        format_date = "%Y/%m/%d %H:%M:%S.%f"  
        if len(output) < 10:
            last_connection = str(output[7] + ' ' + output[8]) #strip remove trailing whitespaces and new lines
    
        else:
            last_connection = str(output[8]).strip() + ' ' + str(output[9]).strip() #strip remove trailing whitespaces and new lines
        
        last_connection = datetime.strptime(last_connection, format_date)
        return last_connection
 
    def compute_delays(self, current_time:datetime, last_connection: datetime):
        """
        Function to calculate delay in seconds of channel of the correspond station.

        Parameters:
        -----------
        current time in datetime object.
        last_connection (datetime): last UTC datetime connection of channel of the correspond station.
        
        Return:
        -----------
        delay(float): delay in total seconds of channel of the correspond stations. Delay value was set as -99999
        for stations not tracking by slinktool module.
        """
        current_time = current_time + timedelta(hours=5)
        if last_connection is not None and last_connection != datetime(1970, 1, 1, 0, 0, 0, 0):
            delay = (current_time - last_connection).total_seconds()  # Delay in minutes
            pass
        else:
            delay = -99999
        return delay

    def compile_connection_information(self, last_siigeo: list, delay_siigeo:list, channel_siigeo: list, last_shared: list, delay_shared: list, channel_shared: list, last_inter: list, delay_inter: list, channel_inter: list):
        """
        Function to compile last connection and delays information of national, shared and international stations.

        Parameters:
        -----------
        last_siigeo(list): List of last connection of channels of the correspond national stations.
        delay_siigeo(list): List of delays of channels of the correspond national stations.
        last_shared(list): List of last connection of channels of the correspond shared national stations.
        delay_shared(list): List of delays of channels of the correspond shared national stations.
        last_inter(list): List of last connection of channels of the correspond international stations.
        delay_inter(list): List of delays of channels of the correspond international stations.
        
        Return:
        -----------
        self.siigeo_data (Pd.DataFrame): Instance with processed information of national stations from Siigeo intranet service.
        self.shared_data (Pd.DataFrame): Instance with processed information of shared national stations.
        self.inter_data (Pd.DataFrame): Instance with processed information of international stations. 
        """
        if not last_siigeo or not isinstance(last_siigeo, list):
            raise ValueError(Fore.LIGHTRED_EX + "last connections of siigeo stations must be in a valid list." + Fore.RESET)
        if not delay_siigeo or not isinstance(delay_siigeo, list):
            raise ValueError(Fore.LIGHTRED_EX + "Delays times of siigeo stations must be in a valid list." + Fore.RESET)
        if not channel_siigeo or not isinstance(channel_siigeo, list):
            raise ValueError(Fore.LIGHTRED_EX + "Channels of siigeo stations must be in a valid list." + Fore.RESET)
        siigeo_data = self.siigeo_data
        siigeo_data['last_connection'] = last_siigeo
        siigeo_data['delay_seconds'] = delay_siigeo
        siigeo_data['channel'] = channel_siigeo
        self.siigeo_data = siigeo_data
        if not last_shared or not isinstance(last_shared, list):
            raise ValueError("last connections of shared stations must be a valid list.")
        if not delay_shared or not isinstance(delay_shared, list):
            raise ValueError("Delays times of shared stations must be in a valid list.")
        if not channel_shared or not isinstance(channel_shared, list):
            raise ValueError("Channels of shared stations must be in a valid list.")
        shared_data = self.shared_data
        shared_data['last_connection'] = last_shared
        shared_data['delay_seconds'] = delay_shared
        shared_data['channel'] = channel_shared
        self.shared_data = shared_data
        if self.server in ['232', '13', '91', '95']:
            if not last_inter or not isinstance(last_inter, list):
                raise ValueError("last connections of international stations must be a valid list.")
            if not delay_inter or not isinstance(delay_inter, list):
                raise ValueError("Delays times of international stations must be in a valid list.")
            if not channel_inter or not isinstance(channel_inter, list):
                raise ValueError("Channels of international stations must be in a valid list.")
            inter_data = self.inter_data
            inter_data['last_connection'] = last_inter
            inter_data['delay_seconds'] = delay_inter
            inter_data['channel'] = channel_inter
            self.inter_data = inter_data
        return True

    @staticmethod
    def get_station_status(data:pd.DataFrame):
        """
        Function to define station status of each station.

        Parameters:
        -----------
        data(Pd.DataFrame): Dataframe with information of stations connectivity.
        
        Return:
        -----------
        print(list): delays in a readable format (Day, Hour, Minute, Seconds).
        status(list): status of channel of each station.
        """
        if not isinstance(data, pd.DataFrame) or data.empty:
            raise ValueError(Fore.LIGHTRED_EX + "Data must be provided in a valid dataframe!!!" + Fore.RESET)
        prints = []
        status = []
        delays = data['delay_seconds'].astype(float).tolist()
        for delay in delays:
            min, sec = divmod(delay, 60)
            hr, min = divmod(min, 60)
            day, hr = divmod(hr, 24)

            if delay == -99999:
                status.append("Station not tracking by slinktool")
                print_delay = "No delay time available"
                prints.append(print_delay)

            elif delay < 0:
                status.append('Future (check)')
                print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"
                prints.append(print_delay)
            
            elif delay <= 600:  # 10 minutes
                status.append('online')
                print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"
                prints.append(print_delay)

            elif delay > 600 and delay <= 9000: # 2.5 hours
                status.append('recovering')
                print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"
                prints.append(print_delay)
            
            else:
                status.append('offline')
                print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"
                prints.append(print_delay)

        return prints, status  

    @staticmethod
    def order_seismo_stations(data_stations):
        """
        Function to order national seismological stations according to checklist excel file.

        Parameters:
        -----------
        data_stations(Pd.DataFrame): Dataframe with information of national seismological stations connectivity.
        
        Return:
        -----------
        data_stations(Pd.DataFrame): Dataframe with information of national seismological stations connectivity ordered.
        """
        if not isinstance(data_stations, pd.DataFrame) or data_stations.empty:
            raise ValueError(Fore.LIGHTRED_EX + "National Seismological stations data must be in a valid Dataframe!!!" + Fore.RESET)

        ## According to Reina, C.; Uruena, A.; Lopez A.; suggestions, Shared OVS stations will be at the end of the station list.
        ovs_man = ['AGAM', 'ANIM', 'ELAM', 'NIDM', 'PIRM', 'SJUM', 'TAPM']
        ovs_pop = ['BELO', 'CONO', 'SOTO', 'PALO']
        ovs_pa = ['BODP', 'GCUF', 'GUAP']
        uq = ['PBLA', 'RIBER']
        sts = [*uq, *ovs_man, *ovs_pop, *ovs_pa]

        shared_stations = data_stations.loc[data_stations['id'].isin(sts)]
        shared_stations = shared_stations.sort_values(by='id', key=lambda x: x.map(sts.index))
        data_stations = data_stations.loc[~data_stations['id'].isin(sts)].sort_values(by=['id', 'channel_code'], ascending=[True, True])
        data_stations = pd.concat([data_stations, shared_stations], ignore_index=True).reset_index(drop=True)

        return data_stations
 
    @staticmethod
    def get_status_color(status:str):
        """
        Function to configure a colorful view of status results.
        
        Parameters:
        -----------
        status (str): Status of each station

        Return:
        -----------
        status_color(str): Status of each station in a Colorama format
        """
        if not status or not isinstance(status, str):
            raise ValueError("Status must be a valid string!!!") 
        if status == 'online':
            color = Fore.LIGHTGREEN_EX
        elif status == 'recovering':
            color = Fore.LIGHTMAGENTA_EX
        elif status == 'offline':
            color = Fore.LIGHTRED_EX
        elif status == 'Station not tracking by slinktool':
            color = Fore.LIGHTBLUE_EX
        else:
            color = Fore.RESET
        status_color = color + status + Fore.RESET
        return status_color

    @staticmethod
    def order_accel_stations(data_stations):
        """
        Function to order national accelerometer stations according to checklist excel file.

        Parameters:
        -----------
        data_stations(Pd.DataFrame): Dataframe with information of national accelerometer stations connectivity.
        
        Return:
        -----------
        data_stations(Pd.DataFrame): Dataframe with information of national accelerometer stations connectivity ordered.
        """
        if not isinstance(data_stations, pd.DataFrame) or data_stations.empty:
            raise ValueError(Fore.LIGHTRED_EX + "National Accelerographic stations data must be in a valid Dataframe!!!" + Fore.RESET)
        data_stations = data_stations.sort_values(by=['id', 'channel_code'], ascending=[True, True]).reset_index(drop=True)
        return data_stations
 
    @staticmethod
    def order_inter_stations(data_stations):
        """
        Function to order international stations according to checklist excel file.

        Parameters:
        -----------
        data_stations(Pd.DataFrame): Dataframe with information of international stations connectivity.
        
        Return:
        -----------
        data_stations(Pd.DataFrame): Dataframe with information of international stations connectivity ordered.
        """
        if not isinstance(data_stations, pd.DataFrame) or data_stations.empty:
            raise ValueError(Fore.LIGHTRED_EX + "International stations data must be in a valid Dataframe!!!" + Fore.RESET)
        data_stations = data_stations.sort_values(by='id').reset_index(drop=True)
        return data_stations
 
    @staticmethod
    def get_nat_statistics(national_stations, seismo_nat_stations, accel_nat_stations):
        """
        Function to get connectivity statistics of national stations.

        Parameters:
        -----------
        national_stations(Pd.DataFrame): Dataframe with information of ordered national stations connectivity.
        seismo_nat_stations(Pd.DataFrame): Dataframe with information of ordered national seismological stations connectivity.
        accel_nat_stations(Pd.DataFrame): Dataframe with information of ordered national accelerometer stations connectivity.
        
        Return:
        -----------
        number_seismo_stations(int): Total number of online Seismometer stations.
        number_accel_stations(int): Total number of online Acelerometer stations.
        online_number_stations(int): Total number of online national stations.
        total_number_stations(int): Total number of stations.
        """
        if not isinstance(national_stations, pd.DataFrame) or national_stations.empty:
            raise ValueError(Fore.LIGHTRED_EX + "National stations data must be in a valid Dataframe!!!" + Fore.RESET)
        
        if not isinstance(seismo_nat_stations, pd.DataFrame) or seismo_nat_stations.empty:
            raise ValueError("Seismological stations must be in a valid Dataframe!!!")
        
        if not isinstance(accel_nat_stations, pd.DataFrame) or accel_nat_stations.empty:
            raise ValueError("Accelographic stations must be in a valid Dataframe!!!")
        number_seismo_stations = len(seismo_nat_stations.loc[(seismo_nat_stations['status'] == 'online')]['id'].unique())
        number_accel_stations = len(accel_nat_stations.loc[accel_nat_stations['status'] == 'online']['id'].unique())
        online_number_stations = len(national_stations.loc[national_stations['status'] == 'online']['id'].unique())
        total_number_stations = len(national_stations['id'].unique())

        return number_seismo_stations, number_accel_stations, online_number_stations, total_number_stations

    @staticmethod
    def get_station_statistics(national_stations, international_stations):
        """
        Function to get connectivity statistics of national and international stations.

        Parameters:
        -----------
        national_stations(Pd.DataFrame): Dataframe with information of ordered national stations connectivity.
        international_stations(Pd.DataFrame): Dataframe with information of ordered international stations connectivity.
        
        Return:
        -----------
        online_nat_stations(int): Total number of online national stations.
        total_nat_stations(int): Total number of national stations.
        online_inter_stations(int): Total number of online international stations.
        total_inter_stations(int): Total number of international stations.
        """
        if not isinstance(national_stations, pd.DataFrame) or national_stations.empty:
            raise ValueError(Fore.LIGHTRED_EX + "National stations data must be in a valid Dataframe!!!" + Fore.RESET)
        
        if not isinstance(international_stations, pd.DataFrame) or international_stations.empty:
            raise ValueError(Fore.LIGHTRED_EX + "International stations data must be in a valid Dataframe!!!" + Fore.RESET)

        online_nat_stations = len(national_stations.loc[(national_stations['status'] == 'online')]['id'].unique())
        total_nat_stations = len(national_stations['id'].unique())
        online_inter_stations = len(international_stations.loc[(international_stations['status'] == 'online')]['id'].unique())
        total_inter_stations = len(international_stations['id'].unique())

        return online_nat_stations, total_nat_stations, online_inter_stations, total_inter_stations    

    @staticmethod
    def get_type_transmission(national_stations):
        """
        Function to divide online national stations by type of transmission.

        Parameters:
        -----------
        national_stations(Pd.DataFrame): Dataframe with information of ordered national stations connectivity.
        
        Return:
        -----------
        List with the statistics of online and total number of national stations by type of transmission. Order: online and total of satelital stations;
        online and total of celular stations; online and total of internet stations and online and total of radio stations. 
        """
        if not isinstance(national_stations, pd.DataFrame) or national_stations.empty:
            raise ValueError("National stations data must be in a valid Dataframe!!!")
        
        #sat_stations = national_stations.loc[(national_stations['type_transmission'] == 'satelital leo')]
        sat_stations = national_stations.loc[(national_stations['type_transmission'] == 'satelital leo') | (national_stations['type_transmission'] == 'satelital')]
        cel_stations = national_stations.loc[national_stations['type_transmission'] == 'celular']
        internet_stations = national_stations.loc[national_stations['type_transmission'] == 'internet']
        radio_stations = national_stations.loc[national_stations['type_transmission'] == 'radio']

        number_sat_stations = len(sat_stations['id'].unique())
        online_sat_stations = len(sat_stations.loc[sat_stations['status'] == 'online']['id'].unique())
        number_cel_stations = len(cel_stations['id'].unique())
        online_cel_stations = len(cel_stations.loc[cel_stations['status'] == 'online']['id'].unique())
        number_internet_stations = len(internet_stations['id'].unique())
        online_internet_stations = len(internet_stations.loc[internet_stations['status'] == 'online']['id'].unique())
        number_radio_stations = len(radio_stations['id'].unique())
        online_radio_stations = len(radio_stations.loc[radio_stations['status'] == 'online']['id'].unique())

        return [number_sat_stations, online_sat_stations, number_cel_stations, online_cel_stations, number_internet_stations, online_internet_stations, number_radio_stations, online_radio_stations]
    
    @staticmethod
    def save_checklist(stations_data:pd.DataFrame, stations_fname:str):
        """
        Function to storage checklist results.

        Parameters:
        -----------
        stations_data(Pd.DataFrame): Dataframe with information of stations connectivity.
        stations_fname(str): Name of the file.
        
        Return:
        -----------
        stations_data file storage in local path.
        """
        if not isinstance(stations_data, pd.DataFrame) or stations_data.empty:
            raise ValueError(Fore.LIGHTRED_EX + "Stations data must be provided in a valid Dataframe!!!" + Fore.RESET)

        tmp = []
        for ind, row in stations_data.iterrows():
            if row['status'] == 'online':
                tmp.append('')
            elif row['status'] == 'recovering':
                tmp.append('--')
            elif row['status'] == 'offline' or row['status'] == 'Station not tracking by slinktool':
                tmp.append('x')
            elif row['status'] == 'Future (check)':
                tmp.append('?')
            else:
                tmp.append('#')
        stations_data['checklist'] = tmp
        cols = ['id', 'channel', 'checklist']
        stations_data = stations_data[cols]
        stations_data.to_csv(stations_fname, sep=' ', index=False)
        return True

