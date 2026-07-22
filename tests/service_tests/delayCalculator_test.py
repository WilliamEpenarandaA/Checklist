# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contain unitary tests of DelayCalculator class.

import numpy as np
import pandas as pd
import unittest
from datetime import datetime
from pandas.testing import assert_frame_equal
from src.services.delay_calculator import DelayCalculator

class DelayCalculatorTest(unittest.TestCase):

    def setUp(self):
        global base_data
        global base_sgc_data
        global base_slink_data
        global parsed_datetime
        global theorical_delays
        global theorical_stations_df
        base_data = {'network': ['CM', 'CM', 'CM', 'GT', 'CM', 'NU'], 
                         'stid': ['APAC', 'APAC', 'APAC', 'LPAZ', 'CSAMU', 'APQN'], 
                         'loc': ['00', '00', '00', '00', '10', None], 
                         'channel': ['HHE', 'HHN', 'HHZ', 'BHZ', 'HNZ', 'HHZ'], 
                         'type_transmission': ['Satelital', 'Satelital', 'Satelital', 'Internet', 'Celular', 'Internet'], 
                         'last_connection': ['2026/07/19 11:14:08.1583', '2026/07/19 11:14:09.2983', '2026/07/19 11:14:09.3383', '2026/07/19 11:13:20.8000', None, None]}
        
        base_sgc_data = (('CM', 'APAC', '00', 'HHE', 'Satelital'), 
                 ('CM', 'APAC', '00', 'HHN', 'Satelital'), 
                 ('CM', 'APAC', '00', 'HHZ', 'Satelital'), 
                 ('GT', 'LPAZ', None, 'BHZ', 'Internet'),
                 ('CM', 'CSAMU', '10', 'HNZ', 'Celular'),
                 ('NU', 'APQN', None, 'HHZ', 'Internet')
                 )
        
        base_slink_data = (('CM', 'APAC', '00', 'HHE', 'Satelital', '2026/07/19 09:55:11.1583'),
                ('CM', 'APAC', '00', 'HHN', 'Satelital', '2026/07/19 09:55:11.1583'),
                ('CM', 'APAC', '00', 'HHZ', 'Satelital', '2026/07/19 09:55:11.1583'),
                ('GT', 'LPAZ', '00', 'BHZ', 'Internet', '2026/07/19 10:10:37.5750')
                )
        
        parsed_datetime = datetime.strptime('2026/07/19 11:14:38', "%Y/%m/%d %H:%M:%S")        

        # Theorical outputs
        theorical_stations_df = {'network': ['CM', 'CM', 'CM', 'GT', 'CM', 'NU'], 
                         'stid': ['APAC', 'APAC', 'APAC', 'LPAZ', 'CSAMU', 'APQN'], 
                         'loc': ['00', '00', '00', '00', '10', None], 
                         'channel': ['HHE', 'HHN', 'HHZ', 'BHZ', 'HNZ', 'HHZ'], 
                         'type_transmission': ['Satelital', 'Satelital', 'Satelital', 'Internet', 'Celular', 'Internet'], 
                         'last_connection': ['2026/07/19 09:55:11.1583', '2026/07/19 09:55:11.1583', '2026/07/19 09:55:11.1583', '2026/07/19 10:10:37.5750', None, None]}
        
        theorical_delays = np.array([29841700, 28701700, 28661700, 77200000, 'NaT', 'NaT'], dtype='timedelta64[us]')
        print('setUp method execution....')
    
    def test_add_stations_untracked(self):
        cols_sgc = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        station_data = pd.DataFrame(base_sgc_data, columns=cols_sgc)
        cols_ = ['network', 'stid', 'loc', 'channel', 'type_transmission', 'last_connection']
        slink_data = pd.DataFrame(base_slink_data, columns=cols_)
        res = DelayCalculator.add_stations_untracked(station_data=station_data, slinktool_data=slink_data)
        
        theorical_res = pd.DataFrame(theorical_stations_df)
        theorical_res['network'] = theorical_res['network'].fillna(pd.NA).astype("string[pyarrow]") # Convert nan numpy to pd.NA format
        theorical_res['stid'] = theorical_res['stid'].fillna(pd.NA).astype("string[pyarrow]") # Convert nan numpy to pd.NA format
        theorical_res['loc'] = theorical_res['loc'].fillna(pd.NA).astype("string[pyarrow]") # Convert nan numpy to pd.NA format
        theorical_res['channel'] = theorical_res['channel'].fillna(pd.NA).astype("string[pyarrow]") # Convert nan numpy to pd.NA format
        theorical_res['type_transmission'] = theorical_res['type_transmission'].fillna(pd.NA).astype("string[pyarrow]") # Convert nan numpy to pd.NA format

        assert_frame_equal(res, theorical_res) #if want to avoid nan differences, select check_dtype option to False

    def test_compute_delays(self):
        data = pd.DataFrame(base_data)
        res = DelayCalculator.compute_delays(data, datetime_column='last_connection', datetime=parsed_datetime)
        delays = res['delay'].to_numpy()

        np.testing.assert_array_equal(delays, theorical_delays)

if __name__ == '__main__':
    unittest.main()