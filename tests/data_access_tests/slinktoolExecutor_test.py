# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contain unitary tests of SlinktoolExecutor class.

import unittest
from src.data_access.slinktool_executor import SlinktoolExecutor

class SlinktoolExecutorTest(unittest.TestCase):
    """Test suite verifying ``SlinktoolExecutor`` port lookup, command building, and execution."""
    def setUp(self):
        """Initialize test server identifier ``'91'`` and expected ``slinktool`` command."""
        global server
        global theorical_command
        server = '91'

        # Theorical Outputs
        theorical_command = ["slinktool", "-Q", "10.100.100.91"]
        print('setUp method execution....')

    def test_get_port(self):
        """Verify that ``get_port`` returns ``None`` for server ``'91'``."""
        port = SlinktoolExecutor.get_port(server=server)
        self.assertIsNone(port)

    def test_build_command(self):
        """Verify that ``build_command`` builds ``['slinktool', '-Q', '10.100.100.91']``."""
        port = SlinktoolExecutor.get_port(server=server)
        command = SlinktoolExecutor.build_command(server, port)
        self.assertListEqual(command, theorical_command)

    def test_request_info(self):
        """Verify that ``request_info`` returns a non-``None`` output for server ``'91'``."""
        port = SlinktoolExecutor.get_port(server=server)
        command = SlinktoolExecutor.build_command(server, port)
        output = SlinktoolExecutor.request_info(command)
        self.assertIsNotNone(output)


if __name__ == '__main__':
    unittest.main()