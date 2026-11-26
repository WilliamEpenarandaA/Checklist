# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contain service module for persisting station checklist results and sensor metrics.  

from colorama import Fore
from datetime import datetime, UTC
import json
import numpy as np
import pandas as pd
from src.config import settings

logger = settings.get_logger(__name__)

class ResultRepository:
    """
    Base repository interface for storing station checklist results and metrics.
    """

    @classmethod
    def save_results(cls):
        """
        Placeholder method for saving station checklist results.

        Subclasses override this method to implement format-specific
        persistence.
        """
        pass

    @classmethod
    def save_metrics(cls):
        """
        Placeholder method for saving computed station metrics.

        Subclasses override this method to implement format-specific
        persistence.
        """
        pass

class CsvResult(ResultRepository):
    """
    CSV storage implementation for exporting station checklist results.
    """

    @classmethod
    def save_results(cls, station_data:pd.DataFrame, cols:list):
        """
        Export selected columns of station data to a UTC-timestamped CSV file.

        Builds a filename in the current working directory matching the pattern
        ``'<YYYYMMDDHHMMSS>_checklist.csv'`` using the current UTC time, and
        writes ``station_data`` without the row index while formatting
        floating-point numbers to five decimal places (``'%.5f'``). In
        ``main.py``, ``cols`` is passed as ``['network', 'stid', 'loc',
        'channel', 'type_transmission', 'conn_time_initial',
        'latency_sec_initial', 'conn_time_next', 'latency_sec_next',
        'status']``.

        Parameters
        ----------
        station_data : pandas.DataFrame
            DataFrame containing processed station checklist records.
        cols : list of str
            Column names from ``station_data`` to write to the CSV file.

        Returns
        -------
        bool
            ``True`` once the CSV file has been written.

        Raises
        ------
        KeyError
            If any column name in ``cols`` is not present in ``station_data``.
        OSError
            If the target CSV file cannot be created or written to disk.
        """

        #Construct filename
        date_format = "%Y%m%d%H%M%S"
        date_now = datetime.now(UTC).strftime(date_format)
        fname = date_now + "_checklist.csv"
        station_data.to_csv(fname, columns=cols, index=False, float_format="%.5f")
        logger.info(Fore.GREEN + f"checklist results stored succesfully in {fname}." + Fore.RESET)

        return True

class JsonResult(ResultRepository):
    """
    JSON storage implementation for exporting station connectivity metrics.
    """

    @classmethod
    def save_metrics(cls, metrics:dict):
        """
        Serialize station metrics to a UTC-timestamped UTF-8 JSON file.

        Builds a filename in the current working directory matching the pattern
        ``'<YYYYMMDDHHMMSS>_metrics.json'`` using the current UTC time, and
        writes ``metrics`` formatted with a 4-space indentation.

        Parameters
        ----------
        metrics : dict
            Dictionary of computed station metrics to serialize as JSON.

        Returns
        -------
        bool
            ``True`` once the JSON file has been written.

        Raises
        ------
        TypeError
            If ``metrics`` contains values that are not JSON serializable.
        OSError
            If the target JSON file cannot be created or written to disk.
        """

        #Construct filename
        date_format = "%Y%m%d%H%M%S"
        date_now = datetime.now(UTC).strftime(date_format)
        fname = date_now + "_metrics.json"

        with open(fname, 'w', encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)

        logger.info(Fore.GREEN + f"metrics stored succesfully in {fname}." + Fore.RESET)
        
        return True