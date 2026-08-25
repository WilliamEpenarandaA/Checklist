# Checklist
Checklist is a Python routine developed for checking real-time data availability of total number of SGC stations from RSNC (Colombian National Seismological Network) directly in servers of data adquisition and connected to Siigeo's database. The Siigeo information is updated every month or can be forced to update at any time.

## Requirements
The routine was developed on Python >= 3.7x and running on Linux systems. The routine required the following packages (a detailed list is in requirements.txt):

* concurrent
* colorama
* obspy
* openpyxl
* pandas
* slinktool (Seiscomp module)
* tqdm

## Installation
We recommend using the package manager [pip](https://pip.pypa.io/en/stable/) to install python, although you can use miniconda, conda or mamba as the default python package manager, but the instructions could slightly vary. Then, we suggest creating an isolated virtual environment to avoid conflicts with other dependencies, as follows:

To create a virtual environment using Pip manager:
```bash
python3 -m venv {environment_name}
```

To create a virtual environmen using conda manager:
```bash
conda create -n {environment_name}
```

Make sure you activate the virtual environment before installing the required dependencies. Finally, run the following command to install the dependencies using pip manager:

```bash
pip install -r requirements.txt
``` 

## Usage
To use the routine just need to execute the following command in the terminal: 

```bash
python3 <path_to_dir>/src/main.py <options>
```

where:

* `<path_to_dir>`: Need to declare the path to the folder where the routine is stored. We recommend to include it in PATH environment variable for more convenience.
* `<options>`: There are additional parameters can be declared to activate additional parameters in the routine:
    * `+h` or `+help`  display a menu on terminal which show different avalaible options.
    * `+n` or `+n_process` number of process to use in parallel. Recommended to set as 8 to reduce computing time. It's limited to 10 according to capacities of server processor. 
    * `+o` or `+output`  Save the results on csv files. Only allowed for 232 and 13 servers.
    * `+p` or `+print`  Print delay times in a readable format (dd HH MM SS) in terminal.
    * `+u` or `+update`  Update station information with Siigeo database.
    * `+s` or `+stat`  Print performance of National and International stations in terminal. Only allowed for 232 and 13 servers.
    * `+sn` or `+stat_nat`  Print performance of National stations in terminal divided by type of transmission.
    * `++offline` Print checklist of stations with offline status. Can be combined with others filters.
    * `++recovering` Print checklist of stations with recovering status. Can be combined with others filters.
    * `++online` Print checklist of stations with online status. Can be combined with others filters.
    * `++server` Define server to perform checklist process. Avalaible options are: 232, 13, 97 and 2.
    * `++wave` Compute delay times for stations not tracked by slinktool module. Only allowed in 232 server.

> [!IMPORTANT]
> If any station is not being tracked by slinktool module, last connection datetime is defined a default value of **1970-01-01 00:00:00**.
> `++wave` allow to compute last connection of a station using last data stored in waveform files in server. If a station has not data in the current year, delay time assign a default value of **one year and one day** before the current time and last connection datetime assign a default value of **last day of the previous year**. For example: if the year is 2025, last connection will be **2024-12-31 23:59:59**.

> [!NOTE]
> For instance, if we want to verify the availabity of the whole network with the corresponding metrics for National and International stations and save the results in csv files, we can execute the following command:
> ```bash
> python3 <path_to_folder>/src/main.py +s +o
> ```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

## Authority
This project was developed by William Eduardo Peñaranda Arévalo, Seismological Analyst, with the supervision of Angel Agudelo, Seismologist. Both belong to the working group: Evaluation, Monitoring, and Diagnostic of Geological Dynamics at SGC. The use of this code is restricted only for internal purposes at SGC, subject to the institution's internal policies and regulations, and cannot be shared without prior authorization. Intelectual property of this routine belongs to SGC.
