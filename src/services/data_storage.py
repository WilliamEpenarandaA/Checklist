# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contain unitary tests of ResultRepository class.

from colorama import Fore
from datetime import datetime, UTC
import json
import numpy as np
import pandas as pd
from src.config import settings

logger = settings.get_logger(__name__)

class ResultRepository:

    @classmethod
    def save_results(cls):
        pass

    @classmethod
    def save_metrics(cls):
        pass

class CsvResult(ResultRepository):

    @classmethod
    def save_results(cls, station_data:pd.DataFrame, cols:list):

        #Construct filename
        date_format = "%Y%m%d%H%M%S"
        date_now = datetime.now(UTC).strftime(date_format)
        fname = date_now + "_checklist.csv"
        station_data.to_csv(fname, columns=cols, index=False, float_format="%.5f")
        logger.info(Fore.GREEN + f"checklist results stored succesfully in {fname}." + Fore.RESET)

        return True

class JsonResult(ResultRepository):

    @classmethod
    def save_metrics(cls, metrics:dict):

        #Construct filename
        date_format = "%Y%m%d%H%M%S"
        date_now = datetime.now(UTC).strftime(date_format)
        fname = date_now + "_metrics.json"

        with open(fname, 'w', encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)

        logger.info(Fore.GREEN + f"metrics stored succesfully in {fname}." + Fore.RESET)
        
        return True