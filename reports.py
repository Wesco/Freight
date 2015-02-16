"""
Created on Apr 30, 2014

@author: TReische
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from fnmatch import fnmatch
from os import listdir, path


def poi(open_poi_dir: str, history_poi_dir: str, ups_date = datetime.now()) -> pd.DataFrame:
    """
    Return a DataFrame containing POI columns ' PO NUMBER' and 'ORDER'
    :rtype : pd.DataFrame
    """

    # Get list of POI files
    name_func = lambda x: 'POI HISTORY ' + x + '.csv'
    file_list = _get_file_list(history_poi_dir, name_func, ups_date)

    name_func = lambda x: 'POI OPEN ' + x + '.csv'
    file_list.extend(_get_file_list(open_poi_dir, name_func, ups_date))

    # Read the files and merge them into a DataFrame
    df_list = _read_files(file_list,
                          header=1,
                          skip_footer=0,
                          use_cols=[' PO NUMBER', 'ORDER', 'SUPPLIER'],
                          converters={0: str, 1: str, 2: str})
    df = _merge_df(df_list, len(df_list), ' PO NUMBER')
    df['SUPPLIER'] = df['SUPPLIER'].apply(str.upper)
    return df


def customers(oor_dir: str, branch: str, ups_date=datetime.now()) -> pd.DataFrame:
    """
    Return a DataFrame containing CUSTOMERS indexed by ORDER NO
    :rtype : pd.DataFrame
    """

    # Get list of OOR files
    name_func = lambda x: branch + ' ' + x + ' ALLORDERS.csv'
    file_list = _get_file_list(oor_dir, name_func, ups_date)

    # Read the files and merge them into a DataFrame
    df_list = _read_files(file_list,
                          header=1,
                          skip_footer=1,
                          use_cols=[2, 3],
                          converters={'CUSTOMER': str, 'ORDER NO': str})

    df = _merge_df(df_list, len(df_list), 'ORDER NO')
    df.set_index(df['ORDER NO'], inplace=True)
    del df['ORDER NO']
    return df


def suppliers(gaps_dir: str, branch: str) -> pd.DataFrame:
    """
    Return a DataFrame containing stock suppliers indexed by SIM numbers
    :rtype : pd.DataFrame
    """

    file_loc = ""
    file_found = False

    # Look back up to 180 days for a GAPS report
    for i in range(0, 180):
        dt = datetime.today() - timedelta(days=i)
        file_name = "%s %s%s" % (branch, dt.strftime('%Y-%m-%d'), '.csv')
        file_path = path.join(gaps_dir, dt.strftime('%Y'))
        file_loc = path.join(file_path, file_name)

        if path.isfile(file_loc):
            file_found = True
            break

    if file_found is False:
        raise FileNotFoundError(2, "Gaps report not found")

    gaps = pd.read_csv(file_loc,
                       encoding='cp1250',
                       na_values=['  '],
                       usecols=['Sim_mfr_no', 'Sim_item_no', 'Supplier_no'],
                       dtype={'Sim_mfr_no': str,
                              'Sim_item_no': str,
                              'Supplier_no': str})

    gaps.set_index(gaps['Sim_mfr_no'] + gaps['Sim_item_no'], inplace=True)
    del [gaps['Sim_mfr_no'], gaps['Sim_item_no']]

    return gaps


def sales_margin(sm_dir: str, months: int=6) -> pd.DataFrame:
    """
    Return a DataFrame containing Sales and Margin data
    :rtype : pd.DataFrame
    """

    # Create a list of Sales & Margin files
    sm_list = [x for x in listdir(sm_dir)
               if re.search(r'^SM \d{4}-\d{2}-\d{2}\.csv$', x)]

    # Clamp months to the available Sales & Margin range
    months = _clamp(months, 1, len(sm_list))

    # Sort so that the most recent months are first
    sm_list.sort(reverse=True)

    # Join the full path and file names
    # shrink list to the correct number of months
    sm_list = [path.join(sm_dir, x) for x in sm_list[:months]]

    # Create a list of sales and margin DataFrames
    df_list = []
    for i in range(len(sm_list)):
        df_list.append(pd.read_csv(sm_list[i], encoding='cp1250', na_values=[' ', '     ', ''], usecols=['dpc', 'dpc_name', 'mfr', 'item', 'cost'], dtype={'dpc': str, 'dpc_name': str, 'mfr': str, 'item': str, 'cost': np.float}))

    sm_df = pd.concat(df_list)
    sm_df['sim'] = sm_df['mfr'] + sm_df['item']
    sm_df.dropna(inplace=True)
    sm_df = sm_df[sm_df['cost'] > 0]
    sm_df.reset_index(inplace=True, drop=True)

    return sm_df


def _clamp(value, min_value, max_value):
    """
    Return a value within the specified range
    """

    return sorted((min_value, value, max_value))[1]


def _get_file_list(file_dir: str, name_func, start_date=datetime.now()) -> list:
    """
    Return a list of files
    """

    poi_list = []
    for i in range(0, 80):
        dt = (start_date - timedelta(days=i)).strftime('%Y-%m-%d')
        poi_list.append(name_func(dt))

    poi_files = [x for x in listdir(file_dir) if fnmatch(x, '*.csv')]
    poi_list = [path.join(file_dir, x) for x in poi_files if x in poi_list]
    return poi_list


def _read_files(file_list, header, skip_footer, use_cols,
                engine='python', converters=None, dtype=None):
    """
    Return a list of DataFrames.
    """

    lst = []
    for _file in file_list:
        lst.append(pd.read_csv(_file,
                               header=header,
                               skip_footer=skip_footer,
                               usecols=use_cols,
                               converters=converters,
                               dtype=dtype,
                               engine=engine))
    return lst


def _merge_df(lst, length, drop_on=None):
    """
    Return a merged DataFrame
    """

    l = length - 1

    if l == 1:
        df = pd.merge(lst[1], lst[0], how='outer', sort=True)
    else:
        df = pd.merge(lst[l], _merge_df(lst, l, drop_on),
                      how='outer',
                      sort=True)

    if drop_on is not None:
        df.drop_duplicates(drop_on, inplace=True)

    return df
