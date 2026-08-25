# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contain unitary tests of StationAnalysis class.

import numpy as np
import pandas as pd
import unittest
from datetime import datetime
from src.config import settings
from src.services.delay_calculator import DelayCalculator
from src.services.station_analysis import StationAnalysis

class StationAnalysisTest(unittest.TestCase):

    def setUp(self):
        global base_data
        global base_data2
        global parsed_datetime
        global parsed_datetime2
        global theorical_status
        global theorical_diffs
        global theorical_status_dt
        global theorical_metrics
        base_data = {'network': ['CM', 'CM', 'CM', 'GT', 'CM', 'NU', 'CM'], 
                         'stid': ['APAC', 'APAC', 'APAC', 'LPAZ', 'CSAMU', 'APQN', 'PIZC'], 
                         'loc': ['00', '00', '00', '00', '10', None, '10'], 
                         'channel': ['HHE', 'HHN', 'HHZ', 'BHZ', 'HNZ', 'HHZ', 'HNZ'], 
                         'type_transmission': ['Satelital', 'Satelital', 'Satelital', 'Internet', 'Celular', 'Internet', 'Celular'], 
                         'last_connection': ['2026/07/19 11:14:08.1583', '2026/07/19 11:14:09.2983', '2026/07/19 11:14:09.3383', '2026/07/19 11:13:20.8000', None, None, '2026/07/19 04:16:36.9845']
                         }

        base_data2 = {'network': ['CM', 'CM', 'CM', 'GT', 'CM', 'NU', 'CM'], 
                                 'stid': ['APAC', 'APAC', 'APAC', 'LPAZ', 'CSAMU', 'APQN', 'PIZC'], 
                                 'loc': ['00', '00', '00', '00', '10', None, '10'], 
                                 'channel': ['HHE', 'HHN', 'HHZ', 'BHZ', 'HNZ', 'HHZ', 'HNZ'], 
                                 'type_transmission': ['Satelital', 'Satelital', 'Satelital', 'Internet', 'Celular', 'Internet', 'Celular'], 
                                 'last_connection': ['2026/07/19 11:15:08.1583', '2026/07/19 11:15:09.2983', '2026/07/19 11:15:09.3383', '2026/07/19 11:14:20.8000', None, None, '2026/07/19 06:16:36.9845']
                                 }
        
        parsed_datetime = datetime.strptime('2026/07/19 11:14:38', "%Y/%m/%d %H:%M:%S").replace(tzinfo=None)
        parsed_datetime2 = datetime.strptime('2026/07/19 11:15:38', "%Y/%m/%d %H:%M:%S").replace(tzinfo=None)
        
        # Theorical outputs
        theorical_status = ['Online', 'Online', 'Online', 'Online', 'N/A', 'N/A', 'Offline']
        theorical_status_dt = ['Online', 'Online', 'Online', 'Online', 'N/A', 'N/A', 'Recovering']
        theorical_diffs = pd.Series([0.0, 0.0, 0.0, 0.0, np.nan, np.nan, -7140.0], name='diff_delays')
        theorical_metrics = {'online_stations': 2, 'total_stations': 5, 'online_seismo': 2, 'total_seismo': 3, 
                             'online_accel': 0, 'total_accel': 2, 'online_strong': 0, 'total_strong': 0, 
                             'online_satellital': 0, 'total_satellital': 0, 'online_cellphone': 0, 
                             'total_cellphone': 0, 'online_internet': 0, 'total_internet': 0, 
                             'online_radio': 0, 'total_radio': 0}
        print('setUp method execution....')

    def test_get_station_status(self):
        dt = 10 
        delay1 = pd.Series([-600, 10, 20, 80, 210, 2000, pd.NaT], dtype=object).fillna(np.nan).to_numpy()
        delay2 = pd.Series([-610, 10, 9, 92, 200, 2300, pd.NaT], dtype=object).fillna(np.nan).to_numpy()
        res = StationAnalysis.get_station_status(delay1, delay2, dt)
        res = res.tolist()
        theorical_status = ["Future", "Online", "Online", "Intermittent", "Intermittent", "Offline", "N/A"]

        self.assertListEqual(res, theorical_status)

    def test_sensor_metrics(self):
        data = pd.DataFrame(base_data)
        data2 = pd.DataFrame(base_data2)
        res = DelayCalculator.compute_delays(data, datetime_column='last_connection', datetime=parsed_datetime)
        res2 = DelayCalculator.compute_delays(data2, datetime_column='last_connection', datetime=parsed_datetime2)
        delay1 = res['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
        delay2 = res2['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
        status = StationAnalysis.get_station_status(delay1, delay2, 60)
        res2['status'] = status
        metrics = StationAnalysis.sensor_metrics(res2)
        
        self.assertDictEqual(metrics, theorical_metrics)


if __name__ == '__main__':
    unittest.main()