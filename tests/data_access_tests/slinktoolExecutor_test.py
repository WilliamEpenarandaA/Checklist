# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contain unitary tests of SlinktoolExecutor class.

import unittest
from src.data_access.slinktool_executor import SlinktoolExecutor

class SlinktoolExecutorTest(unittest.TestCase):

    def setUp(self):
        global server
        global theorical_command
        server = '91'

        # Theorical Outputs
        theorical_command = 'slinktool -Q 10.100.100.91'
        print('setUp method execution....')

    def test_get_port(self):
        port = SlinktoolExecutor.get_port(server=server)
        self.assertIsNone(port)

    def test_build_command(self):
        port = SlinktoolExecutor.get_port(server=server)
        command = SlinktoolExecutor.build_command(server, port)
        self.assertEqual(command, theorical_command)

    def test_request_info(self):
        port = SlinktoolExecutor.get_port(server=server)
        command = SlinktoolExecutor.build_command(server, port)
        output = SlinktoolExecutor.request_info(command)
        self.assertIsNotNone(output)


if __name__ == '__main__':
    unittest.main()