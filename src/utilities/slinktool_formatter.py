# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This file has implementation of.

import pandas as pd
from colorama import Fore
from datetime import datetime
from src.config import settings

logger = settings.get_logger(__name__)

class SlinktoolFormatter:

    @classmethod
    def extract_info(cls, input: list):
        res = []
        format_date = "%Y/%m/%d %H:%M:%S.%f"
        logger.info(Fore.GREEN + f"Number of sensors to be processed: {len(input)}" + Fore.RESET)

        for element in input:
            tmp = "".join(element).split()

            if len(tmp) == 9:
                net = tmp[0]
                stid = tmp[1]
                loc = None
                channel = tmp[2]
                last_conn = str(tmp[7] + ' ' + tmp[8])
                last_conn = datetime.strptime(last_conn, format_date)
                data = (net, stid, loc, channel, last_conn)         
                res.append(data)
            
            elif len(tmp) == 10:
                net = tmp[0]
                stid = tmp[1]    
                loc = tmp[2]
                channel = tmp[3]
                last_conn = str(tmp[8] + ' ' + tmp[9])
                last_conn = datetime.strptime(last_conn, format_date)
                data = (net, stid, loc, channel, last_conn)
                res.append(data)
            
            else:
                logger.warning(Fore.RED + "Mismatch case processing slinktool output!!!" + Fore.RESET)

        logger.info(Fore.GREEN + "Success!!" + Fore.RESET)

        return res        

    @classmethod
    def build_dataframe(cls, input:list):
        cols = ['network', 'stid', 'loc', 'channel', 'last_connection']
        try:
            data = pd.DataFrame(input, columns=cols)
            logger.info(Fore.GREEN + "Dataframe created sucessfully!!" + Fore.RESET)

        except ValueError as err:
            logger.critical(Fore.RED + f"Error. Column mismatch or data issue. {err}" + Fore.RESET)
        
        except Exception as err:
            logger.critical(Fore.RED + f"An unexpected error ocurred: {err}" + Fore.RESET)

        return data
    
    @classmethod
    def select_interest_channels(cls, slinktool_data: pd.DataFrame):
        slinktool_data = slinktool_data.loc[slinktool_data['channel'].isin(settings.stations.AVALAIBLE_SLINKTOOL_CHANNELS)]
        logger.info(Fore.GREEN + f"Selection of the {len(slinktool_data)} field sensors completed sucessfully!!" + Fore.RESET)
        
        return slinktool_data

    @classmethod
    def assign_transmission(cls, slinktool_data: pd.DataFrame, sgc_data: pd.DataFrame):
        ref_dict = sgc_data.set_index('stid')['type_transmission'].to_dict()

        def get_transmission(row, ref_dict: dict):
            value = ref_dict.get(row['stid'])
            return value
        
        slinktool_data['type_transmission'] = slinktool_data.apply(lambda row: get_transmission(row, ref_dict), axis=1)
        logger.info(Fore.GREEN + "Transmission type assigned sucessfully!!" + Fore.RESET)
        
        return slinktool_data
    
    @classmethod
    def order_cols(cls, slinktool_data: pd.DataFrame):
        slinktool_data = slinktool_data[['network', 'stid', 'loc', 'channel', 'type_transmission',
       'last_connection']]
        cols2convert = ['network', 'stid', 'loc', 'channel', 'type_transmission']
        slinktool_data[cols2convert] = slinktool_data[cols2convert].astype("string[pyarrow]")
        logger.info(Fore.GREEN + "Dataframe formatted sucessfully according to SGC data!!" + Fore.RESET)
        return slinktool_data

if __name__ == '__main__':
    from src.data_access.slinktool_executor import SlinktoolExecutor
    from src.data_access.load_data import StationRepository
    from src.utilities.data_formatter import SiigeoFormatter, OtherStationsFormatter
    
    port = SlinktoolExecutor.get_port('91')
    comm = SlinktoolExecutor.build_command('91', port)
    output = SlinktoolExecutor.request_info(comm)
    solution = SlinktoolFormatter.extract_info(output)
    slink_data = SlinktoolFormatter.build_dataframe(solution)
    print(f"Number of channels avaliable in 91: {len(slink_data)}")
    print(slink_data.columns)
    slink_data = SlinktoolFormatter.select_interest_channels(slink_data)
    
    # Load stations data
    siigeo_data = StationRepository.get_siigeo_stations()
    shared_data = StationRepository.get_shared_stations()
    inter_data = StationRepository.get_inter_stations()

    data = {'siigeo': siigeo_data, 'shared': shared_data, 'inter': inter_data}
    format_data = {}
    for key, df in data.items():
        strategy = SiigeoFormatter() if key == 'siigeo' else OtherStationsFormatter()
        df = strategy.rename_cols(df)
        df = strategy.assign_data_types(df)
        df = strategy.infer_channel(df)
        df = strategy.filter_data(df)
        format_data[key] = df     

    siigeo_data = format_data['siigeo']
    shared_data = format_data['shared']
    inter_data = format_data['inter']
    all_data = pd.concat([siigeo_data, shared_data, inter_data], ignore_index=True)
    
    slink_data = SlinktoolFormatter.assign_transmission(slink_data, all_data)
    print(slink_data.loc[slink_data['stid'] == 'SDV'])

    slink_data = SlinktoolFormatter.order_cols(slink_data)
    print(slink_data.dtypes)