## Author: William Eduardo Peñaranda Arévalo, Seismological Analyst at SGC <ORCID:0000-0002-8545-9181> <Github private repo:
## Formation: Geologist and M.Sc. in Geophysics at UIS
## This file contain Wavetime class required to execute checklist of SGC stations.
####################################################################################################################################
####################################################################################################################################
from datetime import datetime, timedelta
from pathlib import Path
import obspy
from colorama import Fore

class Wavetime():
    def __init__(self, year:str, server: str = '232'):
        """
            Constructor of Wavetime Class

            Args:
                year (str): Path to the directory where data files will be stored. Defaults to '../data/'.
                server (str): name of the server to search the information. Defaults to '232'

            Raises:
                ValueError: Trigger if: 
                -url is not a valid string.
                -data_path is not a valid str.
                -server is not a valid str.

            Examples:
                >>> Wavetime(year="2025", server="232")
        """
        if not year or not isinstance(year, str):
            raise ValueError(Fore.LIGHTRED_EX + "Year must be a valid string" + Fore.RESET)
        self.year = year
        if not server or not isinstance(server, str):
            raise ValueError(Fore.LIGHTRED_EX + "Server must be a valid string" + Fore.RESET)
        self.server = server
        
    def define_storage_path(self, year:str, server:str):
        """
        Function to define server folder path.

        Parameters:
        -----------
        year (str): Actual year. stored in a instance variable.
        server (str): Server IP, stored in a instance variable.

        Return:
        -----------
        Path to the server folder (str).
        """
        rpath = '/mnt/'
        srvpath = 'sc' + server + '/'
        return rpath + srvpath + year + '/'

    @staticmethod
    def check_folder(server_path: str, network:str, station:str, channel:str):
        """
        Function to check if a define station folder exists in the server folder.

        Parameters:
        -----------
        server_path(str): Path to the server folder
        network (str): Network code which the selected station belongs.
        station (str): Station code.
        Channel (str): Channel code of the selected station.

        Return:
        -----------
        Path to the station folder (str).
        """
        station = station + "-1" if station == 'CONO' else station
        channel = channel + ".D"
        if not Path(server_path, network, station, channel).is_dir():
            station_folder = "/NFS/"
        else:
            station_folder = Path(server_path, network, station, channel)
        return str(station_folder) 
    
    @staticmethod
    def get_last_wavefile(station_folder:str):
        """
        Function to get the last waveform file stored in the station folder.

        Parameters:
        -----------
        station_folder(str): Path to the station folder in server.

        Return:
        -----------
        Path to the last file of the station folder (str).
        """
        if not station_folder or not isinstance(station_folder, str):
            raise ValueError("Station folder must be a valid string")
        if station_folder == "/NFS/":
            return station_folder
        else:
            station_folder = Path(station_folder)
            files = [f for f in station_folder.iterdir() if f.is_file()]
            files = sorted(files, key=lambda ind: ind.name)
            last_file = str(files[-1])
        return last_file
    
    @staticmethod
    def get_delay(wavefile:str, current_time:datetime):
        """
        Function to compute the delay time and last data stored in the server.

        Parameters:
        -----------
        wavefile(str): path to the last wavefile in station folder.
        current_time (datetime): actual datetime.

        Return:
        -----------
        endtime (datetime): datetime of the last data stored.
        delay (float): time difference in seconds between endtime and actual time.
        """
        if wavefile != "/NFS/" and not Path(wavefile).is_file():
            raise ValueError("Wavefile doesn't exist.")
        current_time = current_time + timedelta(hours=5)
        if wavefile == "/NFS/":
            date = f"{current_time.year}" + "-12-31" + " 23:59:59"
            endtime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            delay = 31536000.0 + 86400.0 # 1 year and one day
            return endtime, delay
        else:
            try:
                stream = obspy.read(wavefile, headonly=True, format='MSEED')
                endtime = stream[0].stats.endtime.datetime
                delay = (current_time - endtime).total_seconds()
            except Exception as err:
                raise Exception(Fore.LIGHTRED_EX + f"{err}" + Fore.RESET)
        return endtime, delay

    @staticmethod
    def get_station_status(delay:float):
        """
        Function to define station status according to delay time.

        Parameters:
        -----------
        delay(float): time difference in seconds between endtime and actual time.

        Return:
        -----------
        status(str): Station status.
        prints(str): delays in a readable format (Day, Hour, Minute, Seconds).
        """
        if not delay or not isinstance(delay, float):
            raise ValueError("Delay must be provided in seconds (float)")
        min, sec = divmod(delay, 60)
        hr, min = divmod(min, 60)
        day, hr = divmod(hr, 24)
        if delay < 0:
            status = 'Future (check)'
            print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"
        elif delay <= 600:  # 10 minutes
            status = 'online'
            print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"
        elif delay > 600 and delay <= 9000: # 2.5 hours
            status = 'recovering'
            print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"
        else:
            status = 'offline'
            print_delay = f"{str(day)} day(s); {str(hr)} hour(s); {str(min)} minutes; {str(round(sec, 1))} seconds"

        return status, print_delay  

if __name__ == "__main__":
    year = '2025'
    server = '232'
    wavetime = Wavetime(year=year, server=server)
    path = wavetime.define_storage_path(wavetime.year, wavetime.server)
    fpath = wavetime.check_folder(server_path=path, network='CM', station='ACH1', channel='HHZ')
    print(fpath)
    l1 = wavetime.get_last_wavefile(fpath)
    print(l1)
    e1, d1 = wavetime.get_delay(l1, datetime.now())
    print(e1, d1)