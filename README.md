![Logo](Logo-SGC-01_original.png)

# Checklist
Checklist is a Python module designed for monitoring the real-time availability and performance metrics of seismological stations within the Colombian National Seismological Network (RSNC). 

## Key Features
* Compatible with any standard seismological software for real-time monitoring of earthquakes. Fully tested with [SeisComP](https://www.seiscomp.de/)
* Connects directly to the RSNC's inventory station database (Siigeo).

## Requirements
This module operates on Linux and was built with Python 3.12+. This module requires the installation of the packages found in either pyproject.toml or requirements.txt. Furthermore, you need to have [slinktool](https://github.com/EarthScope/slinktool/tree/main) installed.

> [!IMPORTANT]
> This module is built in a different environment to encapsulate its functionality and to avoid possible dependency conflicts from [SeisComP](https://www.seiscomp.de/) or any other seismological software.

## Installation
To avoid dependency conflicts, we suggest using [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/) as your preferred Python package manager and creating a virtual environment. The installation process might vary slightly depending on whether you choose Miniconda, Conda, or Mamba. In this case, we explain how to start the project using uv and pip in the following section.

### Using uv package manager
Navigate to the module's root folder, ```../checklist/```, and execute the command to establish the virtual environment and install dependencies from pyproject.toml.

```bash
uv sync
```

### Using pip package manager
Navigate to the module's root folder ```../checklist/```. To begin the installation, create the virtual environment with this command:

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
source .venv/bin/activate; python3 <path_to_projectr>/src/main.py <options>
```
> [!NOTE]
> If you are working in .191 RSNC server, it's already configured alias in bash profiles of all users. In this case, you can execute the module directly with the command ```checklist``` according to the following syntaxis:

```bash
checklist <options>
```

where:

* `<path_to_project>`: Need to declare the path to the folder where the module is stored. We recommend to use an alias in bash profile for more convenience.
* `<options>`: There are additional parameters can be declared to activate additional parameters in the routine:
    * `+h` or `+help` Display a menu on terminal which show different avalaible options.
    * `+o` or `+output` Generate CSV files for checklist results in the specified RSNC drive file order.
    * `+p` or `+print` Display delays in a user-friendly manner (day, hour, minute, seconds).
    * `+nat` Restrict performance metrics to RSNC stations only.
    * `+s` or `+stat` Present performance metrics by sensor types.
    * `+st` or `stat_type` Present performance metrics categorized by transmission type.
    * `+t` or `+time` Re-validate stations status after a specified time interval in seconds. By default is set as 30 seconds.
    * `+u` or `+update` Integrate station updates from the Siigeo database.
    * `++offline` Show stations with offline status. Can be combined with others filters.
    * `++intermittent` Show stations with intermittent status. Can be combined with others filters.
    * `++online` Show stations with online status. Can be combined with others filters.
    * `++server` Define server to perform checklist. Avalaible options are: .91, .95, .232, .13, .97 and .2. By default is set as .91.
    * `++save` Produce files containing stations connectivity data and metrics.

> [!NOTE]
> For instance, to check the real-time availability and performance of RSNC stations categorized by sensor types and create the CSV files needed for the RSNC checklist, run the command below:
> ```bash
> checklist +nat +s +o
> ```
> The module saves output files to the current working directory.

## Authority
This project was developed by William Eduardo Peñaranda Arévalo, Geophysical Analyst, with the supervision of Angel Agudelo, Seismologist. Both belong to the working group: Evaluation, Monitoring, and Diagnostic of Geological Dynamics at Colombian Geological Survey (SGC, acronym in spanish).