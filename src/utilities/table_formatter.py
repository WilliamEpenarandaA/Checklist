# Author: Peñaranda-Arévalo, William <ORCID:0000-0002-8545-9181>
# This python file contains an implementation to format information according to checklist document.

import re
import time
from colorama import Fore
from datetime import datetime, UTC
import numpy as np
import pandas as pd
from src.config import settings

logger = settings.get_logger(__name__)

class TableFormatter:
    """
    Formatter for ordering, filtering, styling, and exporting checklist tables.
    """
    @classmethod
    def order_stations_checklist(cls, stations_data: pd.DataFrame, inter_stations:list):
        """
        Split and sort station records into seismological, accelerograph, and international tables.

        - **National seismological stations**: excludes ``inter_stations`` and
          keeps channels ``'HHZ'``, ``'BHZ'``, ``'EHZ'``, and ``'ELZ'``.
          Stations in ``settings.stations.SHARED_NAT_ORDER`` are sorted by their
          configured order and appended after remaining stations sorted by
          ``['stid', 'loc']``.
        - **National accelerograph stations**: excludes ``inter_stations``,
          keeps channels ``'HNZ'`` and ``'HLZ'``, and sorts by ``['stid', 'loc']``.
        - **International stations**: keeps rows whose ``'stid'`` is in
          ``inter_stations`` and sorts by ``['stid', 'loc']``.

        Parameters
        ----------
        stations_data : pandas.DataFrame
            Evaluated station DataFrame containing at least ``'stid'``,
            ``'loc'``, and ``'channel'`` columns.
        inter_stations : list of str
            Station identifiers belonging to international stations.

        Returns
        -------
        tuple of (pandas.DataFrame, pandas.DataFrame, pandas.DataFrame)
            Tuple ``(seismo_stations, accel_stations, inter_stations)`` of
            sorted DataFrames with reset integer indices.

        Raises
        ------
        KeyError
            If ``'stid'``, ``'loc'``, or ``'channel'`` is missing from
            ``stations_data``.
        """
        # Order National Seismological stations according to checklist xlsx file
        seismo_stations = stations_data.loc[~stations_data['stid'].isin(inter_stations)]
        seismo_stations = seismo_stations.loc[
                        (seismo_stations['channel'] == 'HHZ') | 
                        (seismo_stations['channel'] == 'BHZ') | 
                        (seismo_stations['channel'] == 'EHZ') |
                        (seismo_stations['channel'] == 'ELZ')
                        ]

        shared_nat_stations = seismo_stations.loc[seismo_stations['stid'].isin(settings.stations.SHARED_NAT_ORDER)] 
        shared_nat_stations = shared_nat_stations.sort_values(by='stid', key=lambda x: x.map(settings.stations.SHARED_NAT_ORDER.index))
        seismo_stations = seismo_stations.loc[~seismo_stations['stid'].isin(settings.stations.SHARED_NAT_ORDER)].sort_values(by=['stid', 'loc'], ascending=[True, True])
        seismo_stations = pd.concat([seismo_stations, shared_nat_stations], ignore_index=True).reset_index(drop=True)
        seismo_stations = seismo_stations.loc[~seismo_stations['stid'].isin(inter_stations)]

        # Order National Accelerograph stations according to checklist xlsx file
        accel_stations = stations_data.loc[(stations_data['channel'] == 'HNZ') | (stations_data['channel'] == 'HLZ')]
        accel_stations = accel_stations.sort_values(by=['stid', 'loc'], ascending=[True, True]).reset_index(drop=True)
        accel_stations = accel_stations.loc[~accel_stations['stid'].isin(inter_stations)]

        # Order International stations according to checklist xlsx file
        inter_stations = stations_data.loc[stations_data['stid'].isin(inter_stations)]
        inter_stations = inter_stations.sort_values(by=['stid', 'loc'], ascending=[True, True]).reset_index(drop=True)
        logger.info(Fore.GREEN + "Station data ordered according to checklist!!" + Fore.RESET)

        return seismo_stations, accel_stations, inter_stations
    
    @classmethod
    def extract_inter_stations(cls, inter_data_sgc: pd.DataFrame, inter_stations: pd.DataFrame, channel_dict: dict):
        """
        Filter international station rows by reference channel patterns and location rules.

        For each row in ``inter_data_sgc``, looks up its ``'channel'`` prefix
        in ``channel_dict`` (such as ``settings.stations.INTER_PATTERN_CHANNELS``),
        matches channels in ``inter_stations`` for the same ``'stid'`` using
        ``re.search``, excludes rows where ``'stid'`` is in
        ``settings.stations.SPECIAL_INTER_STATIONS`` and ``loc == '10'``, and
        sorts the result by ``['stid', 'loc']``.

        Parameters
        ----------
        inter_data_sgc : pandas.DataFrame
            Reference international station DataFrame containing ``'stid'`` and
            ``'channel'`` columns.
        inter_stations : pandas.DataFrame
            Candidate international station DataFrame containing ``'stid'``,
            ``'loc'``, and ``'channel'`` columns.
        channel_dict : dict of {str: str}
            Mapping from reference channel names to regex pattern strings.

        Returns
        -------
        pandas.DataFrame
            Filtered and sorted international station DataFrame with a reset
            integer index.

        Raises
        ------
        KeyError
            If ``'stid'``, ``'loc'``, or ``'channel'`` is missing from the
            input DataFrames, or if a channel value is absent from
            ``channel_dict``.
        """
        data = []
        for _, row in inter_data_sgc.iterrows():
            cha = inter_data_sgc.loc[inter_data_sgc['stid'] == row['stid'], 'channel'].item()
            pattern = rf'{channel_dict[cha]}'
            res = list(inter_stations.loc[inter_stations['stid'] == row['stid'], 'channel'])
            interest_channels = [item for item in res if re.search(pattern, item)]
            df = inter_stations[(inter_stations['stid'] == row['stid']) & (inter_stations['channel'].isin(interest_channels))]
            data.append(df)

        inter_stations = pd.concat(data, ignore_index=True)
        inter_stations = inter_stations[~((inter_stations['stid'].isin(settings.stations.SPECIAL_INTER_STATIONS)) & (inter_stations['loc'] == '10'))]
        inter_stations = inter_stations.sort_values(by=['stid', 'loc'], ascending=[True, True]).reset_index(drop=True)
        logger.info(Fore.GREEN + "succesfully extracted international stations!!" + Fore.RESET)

        return inter_stations

    @staticmethod
    def format_status(status_str: str):
        """
        Wrap a status string with ``colorama.Fore`` ANSI color codes.

        Maps ``'Online'`` to green, ``'Intermittent'`` to magenta,
        ``'Offline'`` to red, ``'Future'`` to yellow, and any other value to
        reset styling.

        Parameters
        ----------
        status_str : str
            Station status label.

        Returns
        -------
        str
            ANSI-colored status string terminated with ``Fore.RESET``.
        """
        if status_str == 'Online':
            return Fore.GREEN + status_str + Fore.RESET
        elif status_str == 'Intermittent':
            return Fore.MAGENTA + status_str + Fore.RESET
        elif status_str == 'Offline':
            return Fore.RED + status_str + Fore.RESET
        elif status_str == 'Future':
            return Fore.YELLOW + status_str + Fore.RESET
        else:
            return Fore.RESET + status_str + Fore.RESET
    
    @classmethod
    def filter_vertical_components(cls, stations_data: pd.DataFrame, channel_col:str = 'channel'):
        """
        Filter rows whose channel belongs to ``settings.stations.VERTICAL_SLINKTOOL_CHANNELS``.

        Parameters
        ----------
        stations_data : pandas.DataFrame
            Station DataFrame containing ``channel_col``.
        channel_col : str, default 'channel'
            Column name holding channel identifiers.

        Returns
        -------
        pandas.DataFrame
            Filtered DataFrame with a reset integer index.

        Raises
        ------
        KeyError
            If ``channel_col`` is not present in ``stations_data``.
        """
        stations_data = stations_data[stations_data[channel_col].isin(settings.stations.VERTICAL_SLINKTOOL_CHANNELS)].reset_index(drop=True)
        
        return stations_data

    @classmethod
    def get_display_table(cls, stations_data:pd.DataFrame, name:str, mode:bool):
        """
        Select display columns and filter to vertical components for terminal output.

        Includes ``'delay_'`` when ``mode`` is ``True`` (``['network', 'stid',
        'loc', 'channel', '_last_connection', 'last_connection', 'delay_',
        'status']``) or omits it when ``mode`` is ``False``, then filters to
        vertical channels via ``filter_vertical_components``.

        Parameters
        ----------
        stations_data : pandas.DataFrame
            Station DataFrame containing display columns.
        name : str
            Table label used in the completion log message (e.g.,
            ``'Seismological'``, ``'Acelerographic'``, or
            ``'International'``).
        mode : bool
            If ``True``, includes the formatted ``'delay_'`` column.

        Returns
        -------
        pandas.DataFrame
            Formatted table filtered to vertical sensor channels.

        Raises
        ------
        KeyError
            If any required display column or ``'channel'`` is missing from
            ``stations_data``.
        """
        if mode:
            cols2print = ['network', 'stid', 'loc', 'channel', '_last_connection', 'last_connection', 'delay_', 'status']
        else:
            cols2print = ['network', 'stid', 'loc', 'channel', '_last_connection', 'last_connection', 'status']
        stations_data = stations_data[cols2print]
        stations_data = cls.filter_vertical_components(stations_data)
        logger.info(Fore.GREEN + f"{name} data succesfully formatted to display!!" + Fore.RESET)

        return stations_data
    
    @classmethod
    def export_csv_tables(cls, formatted_table: pd.DataFrame, output_filename: str, status_column:str = 'status', col_name:str = 'checklist'):
        """
        Map status labels to checklist symbols and export vertical channels to CSV.

        Maps ``formatted_table[status_column]`` using
        ``settings.files.SYMBOL_STATUS_CHECKLIST`` into ``col_name``, filters
        vertical channels via ``filter_vertical_components``, and writes
        ``['stid', 'channel', col_name]`` to ``output_filename`` with comma
        separation and without row index.

        Parameters
        ----------
        formatted_table : pandas.DataFrame
            Station DataFrame containing ``'stid'``, ``'channel'``, and
            ``status_column``.
        output_filename : str
            Destination CSV file path (such as ``settings.files.SEISMO_OUT_FILE``,
            ``ACCEL_OUT_FILE``, or ``INTER_OUT_FILE``).
        status_column : str, default 'status'
            Column name containing station status labels.
        col_name : str, default 'checklist'
            Output column name storing mapped checklist symbol strings.

        Returns
        -------
        bool
            ``True`` once the CSV file has been exported.

        Raises
        ------
        KeyError
            If ``'stid'``, ``'channel'``, or ``status_column`` is missing
            from ``formatted_table``.
        OSError
            If ``output_filename`` cannot be created or written to disk.
        """
        formatted_table[col_name] = formatted_table[status_column].map(settings.files.SYMBOL_STATUS_CHECKLIST)
        cols2export = ['stid', 'channel', 'checklist']
        formatted_table = cls.filter_vertical_components(formatted_table)
        formatted_table[cols2export].to_csv(output_filename, sep=',', index=False)
        logger.info(Fore.GREEN + f"{output_filename} exported succesfully!!" + Fore.RESET)

        return True

if __name__ == '__main__':
    from src.data_access.slinktool_executor import SlinktoolExecutor
    from src.data_access.load_data import StationRepository
    from src.services.delay_calculator import DelayCalculator
    from src.services.station_analysis import StationAnalysis
    from src.utilities.data_formatter import SiigeoFormatter, OtherStationsFormatter
    from src.utilities.slinktool_formatter import SlinktoolFormatter

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
        df = strategy.default_connection(df)
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
    slink_data = SlinktoolFormatter.build_dataframe(solution)
    slink_data = SlinktoolFormatter.select_interest_channels(slink_data)
    slink_data = SlinktoolFormatter.assign_transmission(slink_data, all_data)
    slink_data = SlinktoolFormatter.order_cols(slink_data)

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        final_data = DelayCalculator.add_stations_untracked(all_data, slink_data)

    actual_time = datetime.now(UTC).replace(tzinfo=None)
    final_data = DelayCalculator.compute_delays(final_data, actual_time, 'last_connection')
    final_data = DelayCalculator.format_delays(final_data, delay_column='delay')
    dt = 30
    time.sleep(dt)
    output = SlinktoolExecutor.request_info(comm)
    solution = SlinktoolFormatter.extract_info(output)
    slink_data = SlinktoolFormatter.build_dataframe(solution)
    slink_data = SlinktoolFormatter.select_interest_channels(slink_data)
    slink_data = SlinktoolFormatter.assign_transmission(slink_data, all_data)
    slink_data = SlinktoolFormatter.order_cols(slink_data)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        final_data2 = DelayCalculator.add_stations_untracked(all_data, slink_data)
    actual_time = datetime.now(UTC).replace(tzinfo=None)
    final_data2 = DelayCalculator.compute_delays(final_data2, actual_time, 'last_connection')
    final_data2 = DelayCalculator.format_delays(final_data2, delay_column='delay')

    ## Extract delay columns
    delay1 = final_data['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
    delay2 = final_data2['delay'].dt.total_seconds().fillna(np.nan).to_numpy()
    status = StationAnalysis.get_station_status(delay1, delay2, dt)
    final_data2['delay1_seconds'] = delay1
    final_data2['delay2_seconds'] = delay2
    final_data2['status'] = status

    seismo_stations, accel_stations, inter_stations = TableFormatter.order_stations_checklist(final_data2, list(inter_data['stid']))
    print(f"\n{seismo_stations}")

    inter_stations = TableFormatter.extract_inter_stations(inter_data, inter_stations, settings.stations.INTER_PATTERN_CHANNELS)
    TableFormatter.export_csv_tables(inter_stations, settings.files.INTER_OUT_FILE)
    inter_stations = TableFormatter.get_display_table(inter_stations, 'International', mode=True)
    inter_stations['status'] = inter_stations['status'].apply(TableFormatter.format_status)
    print(f"\n{inter_stations}")