# Checklist

Checklist is a Python routine developed for checking real-time data availability of total number of SGC stations from RSNC (Colombian National Seismological Network) directly in Seiscomp 232 server and connected to Siigeo's database. This information is updated every month or can be forced to update.

## Requirements

The routine was developed on Python >= 3.7x and running on Linux systems. The routine required the following packages (a detailed list is in requirements.txt):

* pandas
* tqdm
* slinktool
* request
* colorama
* openpyxl

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
python3 <path_to_dir>/main.py <options>
```

where:

* `<path_to_dir>`: Need to declare the path to the folder where the routine is stored. We recommend to include it in PATH environment variable for more convenience.
* `<options>`: There are additional parameters can be declared to activate additional parameters in the routine:
    * `+h` or `+help`  display a help menu which shows the allowed parameters and its working.
    * `+o` or `+output`  Save the results on a .csv file.
    * `+p` or `+print`  Print delay times in a readable format (dd HH MM SS) in terminal.
    * `+u` or `+update`  Update station information with Siigeo database.
    * `+s` or `+stat`  Print statistics performance of National and International stations in terminal.
    * `+sn` or `+stat_nat`  Print statistics performance of National stations in terminal.
    * `++server` Define the server to request the information. For e.g 232.
    * `++offline` Print checklist of stations with offline status. Can be combined with others filters.
    * `++recovering` Print checklist of stations with recovering status. Can be combined with others filters.
    * `++online` Print checklist of stations with online status. Can be combined with others filters.

> [!NOTE]
> For instance, if we want to verify the availabity of the whole network with the corresponding metrics for National and International stations and save the results in a csv file, we can execute the following command:
> ```bash
> python3 <path_to_dir>/main.py +s +o
> ```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

## Authority
This project was developed by William Eduardo Peñaranda Arévalo, Seismological Analyst, with the supervision of Angel Agudelo, Seismologist. Both belong to the working group: Evaluation, Monitoring, and Diagnostic of Geological Dynamics at RSNC. The use of this code is restricted only for internal purposes at RSNC, subject to the institution's internal policies and regulations, and cannot be shared without prior authorization. Intelectual property of this routine belongs to RSNC.
