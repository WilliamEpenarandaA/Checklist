# Checklist
Checklist is a Python routine developed for checking real-time data availability of total number of SGC stations from RSNC (Colombian National Seismological Network) directly in servers of data adquisition and connected to Siigeo's database. The Siigeo information is updated every month or can be forced to update at any time. Also allow to compute performance metrics of the Seismological network in real-time.

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
We recommend to create a virtual environment to avoid conflicts with other dependencies using [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/) as Python preferred package manager, although you can use miniconda, conda or mamba, but the installation could slightly vary. In this case we explain how to start the project using uv and pip in the following section.

### Using UV package manager
Here, it's quite simple, you need just to run the following command which creates the virtual environment and install the required dependencies listed in the pyproject.toml. 

```bash
uv sync
```

### Using pip package manager
To build the project in the directory, first you need to create the virtual environment as follows:

```bash
python3 -m venv <ENV_NAME>
```

Then, you activate the virtual environment and install the required dependencies listed in requirements.txt executing the following commands:

```bash
source <ENV_NAME>/bin/activate
pip install -r requirements.txt
```

```bash
uv run <path_to_project>/src/main.py <options>
```

## Usage
To use the project, we recommend to set an alias in your bash profile for ease to use. Just need to run the following commands in terminal which depends which package manager you use: 

With uv:
```bash
uv run <path_to_project>/src/main.py <options>
```

and with Pip:
```bash
python3 <path_to_dir>/src/main.py <options>
```

where:

* `<path_to_dir>`: Need to declare the path to the folder where the routine is stored. We recommend to include it in PATH environment variable for more convenience.
* `<options>`: There are additional parameters can be declared to activate additional parameters in the routine:
    * `+h` or `+help`  display a menu on terminal which show different avalaible options.
    * `+n` or `+n_process` number of process to use in parallel. Recommended to set as 8 to reduce computing time. It's limited to 10 according to capacities of server processor. 
    * `+o` or `+output`  Save the results on csv files. Only allowed for 91, 232 and 13 servers.
    * `+p` or `+print`  Print delay times in a readable format (dd HH MM SS) in terminal.
    * `+u` or `+update`  Update station information with Siigeo database.
    * `+s` or `+stat`  Print performance of National and International stations in terminal. Only allowed for 91, 232 and 13 servers.
    * `+sn` or `+stat_nat`  Print performance of National stations in terminal divided by type of transmission.
    * `++offline` Print checklist of stations with offline status. Can be combined with others filters.
    * `++recovering` Print checklist of stations with recovering status. Can be combined with others filters.
    * `++online` Print checklist of stations with online status. Can be combined with others filters.
    * `++server` Define server to perform checklist process. Avalaible options are: 91, 232, 13, 97 and 2.
    * `++wave` Compute delay times for stations not tracked by slinktool module. Only allowed in 91 and 232 server.

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
