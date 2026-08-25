![Logo](Logo-SGC-01_original.png)

# Checklist
Checklist is a Python module for verifying the real-time availability and performance metrics of seismological stations monitored by the Colombian National Seismological Network (RSNC) integrated to the architecture of data adqusition and processing based on [SeisComP](https://www.seiscomp.de/) and linked to Siigeo database of RSNC.

## Requirements
This module operates on Linux and was built with Python 3.12+. To use this module, you must install the packages specified in requirements.txt. Some of the key packages are listed below:

* colorama
* openpyxl
* pandas
* seiscomp
* tqdm

> [!IMPORTANT]
> Although [SeisComP](https://www.seiscomp.de/) is a required package to run this module, it's important to highlight that this module is built in a different environment to encapsulate its functionality and to avoid possible dependency conflicts from [SeisComP](https://www.seiscomp.de/).

## Installation
To avoid dependency conflicts, we suggest using [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/) as your preferred Python package manager and creating a virtual environment. The installation process might vary slightly depending on whether you choose Miniconda, Conda, or Mamba. In this case, we explain how to start the project using uv and pip in the following section.

### Using uv package manager
Navigate to the module's root folder, ```../checklist/```, and execute the command to establish the virtual environment and install dependencies from pyproject.toml.

```bash
uv sync
```

### Using pip package manager
Within of module's root folder ```../checklist/```, To begin the installation, create the virtual environment with this command::

```bash
python3 -m venv <ENV_NAME>
```

Next, enable the virtual environment and install the dependencies specified in ```requirements.txt``` executing the following commands below:

```bash
source <ENV_NAME>/bin/activate
pip install -r requirements.txt
```

## Testing
This module contains a suite of tests to confirm that all functionality operates correctly. To check the module, within module's root folder ```../checklist/```, enable the virtual environment and execute the following command:

```bash
python3 -m unittest discover -p "*_test.py" -v
```

If all tests passed correctly, the module is working properly. In other case, please contact to the developer to report the problem.

## Usage
We suggest to set an alias in your bash profile for ease to use. Depending of your Python package manager, to use the module need to execute some of following commands listed below: 

With uv manager:
```bash
uv run <path_to_project>/src/main.py <options>
```
> [!IMPORTANT]
> uv allow us to run the module directly because it automatically load virtual environment associated with the module.

With pip manager:
```bash
source .venv/bin/activate; python3 <path_to_dir>/src/main.py <options>
```
> [!NOTE]
> If you are working in .191 RSNC server, it's not neccesary to declare ```python3```, since Python environment is configured by default. In this case, you can execute the module directly with the command ```checklist``` according to the following structure:

```bash
checklist <options>
```

where:

* `<path_to_dir>`: Need to declare the path to the folder where the routine is stored. We recommend to include it in PATH environment variable for more convenience.
* `<options>`: There are additional parameters can be declared to activate additional parameters in the routine:
    * `+h` or `+help` Display a menu on terminal which show different avalaible options.
    * `+o` or `+output` Export results as csv files.
    * `+p` or `+print` Display delays in a user-friendly manner (day, hour, minute, seconds).
    * `+s` or `+stat` Present performance metrics by sensor types.
    * `+sn` or `+stat_nat` Present performance metrics categorized by transmission types.
    * `+t` or `+time` Re-validate stations status after a specified time interval in seconds. By default is set as 30 seconds.
    * `+u` or `+update` Integrate station updates from the Siigeo database
    * `++offline` Show stations with offline status. Can be combined with others filters.
    * `++intermittent` Show stations with intermittent status. Can be combined with others filters.
    * `++online` Show stations with online status. Can be combined with others filters.
    * `++server` Define server to perform checklist. Avalaible options are: 91, 95, 232, 13, 97 and 2.

> [!NOTE]
> For instance, if we want to verify the real-time availabity and performance metrics by sensor types of monitored RSNC stations and save the results in csv files, we can execute the following command:
> ```bash
> checklist +s +o
> ```

## Authority
This project was developed by William Eduardo Peñaranda Arévalo, Geophysical Analyst, with the supervision of Angel Agudelo, Seismologist. Both belong to the working group: Evaluation, Monitoring, and Diagnostic of Geological Dynamics at Colombian Geological Survey (SGC, acronym in spanish).