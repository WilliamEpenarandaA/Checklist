# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This file has implementation of a slinktool client.

import subprocess
from colorama import Fore
from src.config import settings

logger = settings.get_logger(__name__)

class SlinktoolExecutor:
    
    @classmethod
    def get_port(cls, server):
        try:
            port = settings.servers.PORTS[server]
            logger.info(Fore.GREEN + "Port stablished succesfully." + Fore.RESET)
            return port

        except KeyError:
            logger.warning(Fore.RED + "Given Server is not defined as a data receiver in environment variables." + Fore.RESET)
            raise


    @classmethod
    def build_command(cls, server: str = None, port:str = None):
        ip = settings.servers.get_server_ip(server, port)
        command = f"slinktool -Q {ip}"

        return command

    @classmethod
    def request_info(cls, command: str):
        result = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        output = result.stdout.splitlines()
        logger.info(Fore.GREEN + "Sucessful information request from slinktool." + Fore.RESET)
        
        return output

if __name__ == '__main__':
    port = SlinktoolExecutor.get_port('232')
    comm = SlinktoolExecutor.build_command('232', port)
    output = SlinktoolExecutor.request_info(comm)
    print(f"Numbers of sensors in 232: {len(output)}")
