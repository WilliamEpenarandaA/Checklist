# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This file has implementation of a client module for executing slinktool queries against configured servers.

import subprocess
from colorama import Fore
from src.config import settings

logger = settings.get_logger(__name__)

class SlinktoolExecutor:
    """Executor utility for building and running ``slinktool`` commands."""

    @classmethod
    def get_port(cls, server):
        """
        Retrieve the configured port mapped to a given server identifier.

        Parameters
        ----------
        server : str
            Server identifier key in ``settings.servers.PORTS`` (for example,
            ``'232'``, ``'13'``, ``'97'``, ``'2'``, ``'91'``, or ``'95'``).

        Returns
        -------
        str or None
            Port string associated with ``server`` (such as ``'16501'`` or
            ``'18000'``), or ``None`` for servers configured without an
            explicit port (``'91'`` and ``'95'``).

        Raises
        ------
        KeyError
            If ``server`` is not defined in ``settings.servers.PORTS``.
        """
        try:
            port = settings.servers.PORTS[server]
            logger.info(Fore.GREEN + "Port stablished succesfully." + Fore.RESET)
            return port

        except KeyError:
            logger.warning(Fore.RED + "Given Server is not defined as a data receiver in environment variables." + Fore.RESET)
            raise

    @classmethod
    def build_command(cls, server: str = None, port:str = None):
        """
        Build the ``slinktool`` command list for querying a server.

        Resolves the target server address via
        ``settings.servers.get_server_ip(server, port)`` and formats the
        command arguments using the ``-Q`` flag.

        Parameters
        ----------
        server : str or None, default None
            Server identifier passed to ``settings.servers.get_server_ip``.
        port : str or None, default None
            Server port string passed to ``settings.servers.get_server_ip``.

        Returns
        -------
        list of str
            Command-line arguments formatted as
            ``['slinktool', '-Q', '<ip>']``.
        """
        ip = settings.servers.get_server_ip(server, port)
        command = ["slinktool", "-Q", f"{ip}"]

        return command

    @classmethod
    def request_info(cls, command: list):
        """
        Execute a ``slinktool`` command via subprocess and return its output lines.

        Runs ``command`` with ``subprocess.run`` using UTF-8 text encoding and
        a 15-second timeout, then splits ``stdout`` into individual lines.

        Parameters
        ----------
        command : list of str
            Command and arguments to execute via ``subprocess.run``.

        Returns
        -------
        list of str
            Lines captured from the standard output (``stdout``) of the
            executed process.

        Raises
        ------
        OSError
            If the ``slinktool`` executable cannot be found or executed (for
            example, ``FileNotFoundError``).
        subprocess.TimeoutExpired
            If ``subprocess.TimeoutExpired`` occurs; command execution exceeds the 
            specified `timeout` duration.
        """
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=15)
        
        except subprocess.TimeoutExpired:
            logger.critical(Fore.RED + "Time expired for requesting information from slinktool." + Fore.RESET)
            raise
            
        output = result.stdout.splitlines()
        logger.info(Fore.GREEN + "Sucessful information request from slinktool." + Fore.RESET)
        
        return output

if __name__ == '__main__':
    port = SlinktoolExecutor.get_port('232')
    comm = SlinktoolExecutor.build_command('232', port)
    output = SlinktoolExecutor.request_info(comm)
    print(f"Numbers of sensors in 232: {len(output)}")