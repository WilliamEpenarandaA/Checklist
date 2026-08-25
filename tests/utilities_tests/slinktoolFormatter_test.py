# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contain unitary tests of SlinktoolFormatter class.

import pandas as pd
import unittest
from src.config import settings
from src.data_access.slinktool_executor import SlinktoolExecutor
from src.utilities.slinktool_formatter import SlinktoolFormatter

class SlinktoolFormatterTest(unittest.TestCase):

    def setUp(self):
        global input
        server = '91'
        port = SlinktoolExecutor.get_port(server)
        comm = SlinktoolExecutor.build_command(server, port)
        input = SlinktoolExecutor.request_info(comm)
        print('setUp method execution....')

    def test_extract_info(self):
        output = SlinktoolFormatter.extract_info(input) 
        self.assertIsInstance(output, list)
        self.assertTrue(all(isinstance(item, tuple) for item in output))

    def test_build_dataframe(self):
        output = SlinktoolFormatter.extract_info(input) 
        df = SlinktoolFormatter.build_dataframe(output)
        theorical_cols = ['network', 'stid', 'loc', 'channel', 'last_connection']
        cols = list(df.columns)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertListEqual(cols, theorical_cols)

    def test_select_interest_channels(self):
        output = SlinktoolFormatter.extract_info(input) 
        df = SlinktoolFormatter.build_dataframe(output)
        df = SlinktoolFormatter.select_interest_channels(df)
        channels = sorted(list(df['channel'].unique()))
        theorical_channels = sorted(settings.stations.AVALAIBLE_SLINKTOOL_CHANNELS)
        self.assertListEqual(channels, theorical_channels)

if __name__ == '__main__':
    unittest.main()