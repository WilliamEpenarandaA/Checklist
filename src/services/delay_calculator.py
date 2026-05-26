# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to .

import pandas as pd
from src.config import settings
from src.data_access.slinktool_executor import SlinktoolExecutor
from src.data_access.load_data import StationRepository
from src.utilities.formatter import SiigeoFormatter, OtherStationsFormatter
from src.utilities.slinktool_formatter import SlinktoolFormatter

class DelayCalculator:

    pass

if __name__ == "__main__":
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
    
    # Load slinktool data 
    port = SlinktoolExecutor.get_port('91')
    comm = SlinktoolExecutor.build_command('91', port)
    output = SlinktoolExecutor.request_info(comm)
    solution = SlinktoolFormatter.extract_info(output)
    data = SlinktoolFormatter.build_dataframe(solution)
    data = SlinktoolFormatter.select_interest_channels(data)

    temp = all_data.set_index('stid')['type_transmission'].to_dict()
    
    def test(row, dict1):
        value = dict1.get(row['stid'])
        return value
    
    data['type_transmission'] = data.apply(lambda row: test(row, temp), axis=1)
    print(data.columns)
    print(data.loc[data['stid'] == 'SDV'])