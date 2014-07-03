'''
Created on Apr 30, 2014

@author: TReische
'''

from datetime import datetime, timedelta
from pandas import read_csv, read_excel
from pandas import merge
from fnmatch import fnmatch
from os import listdir, path


def Poi(open_poi_dir, history_poi_dir):
    """
    Return a DataFrame containing POI columns ' PO NUMBER' and 'ORDER'
    """

    # Get list of POI files
    name_func = lambda x: 'POI HISTORY ' + x + '.csv'
    file_list = _get_file_list(history_poi_dir, name_func)

    name_func = lambda x: 'POI OPEN ' + x + '.csv'
    file_list.extend(_get_file_list(open_poi_dir, name_func))

    # Read the files and merge them into a DataFrame
    df_list = _read_files(file_list, 1, 0, [1, 40])
    df = _merge_df(df_list, len(df_list), ' PO NUMBER')
    return df


def Oor(oor_dir):
    """
    Return a DataFrame containing OOR columns 'CUSTOMER', and 'ORDER NO'
    """

    # Get list of OOR files
    name_func = lambda x: '3615 ' + x + ' ALLORDERS.csv'
    file_list = _get_file_list(oor_dir, name_func)

    # Read the files and merge them into a DataFrame
    df_list = _read_files(file_list, 1, 1, [2, 3])
    df = _merge_df(df_list, len(df_list), 'ORDER NO')
    df.set_index(df['ORDER NO'], inplace=True)
    del df['ORDER NO']
    return df


def Gaps(gaps_dir, branch):
    """
    Return a DataFrame containing Gaps
    """

    file_name = ""
    df = None

    for i in range(0, 180):
        dt = datetime.today() - timedelta.days(i)
        file_name = "%s %s" % branch, dt

    if path.isfile(path.join(gaps_dir, file_name)):
        df = read_csv()

    return df


def SM(sm_dir):
    """
    Return a DataFrame containing Sales and Margin data
    """

    dt = datetime.today().strftime('%Y-%m-%d')
    sm_file = path.join(sm_dir, 'SM ' + dt + '.xlsx')
    df = None

    if path.isfile(sm_file):
        df = read_excel(io=sm_file, sheetname='Sheet1', parse_cols='D,K,L,O')
        df = df[df['sales'].apply(lambda x: x > 0)].dropna()

    return df


def _get_file_list(file_dir, name_func):
    """
    Return a list of files
    """

    poilst = []
    for i in range(0, 300):
        dt = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        poilst.append(name_func(dt))

    poifiles = [x for x in listdir(file_dir) if fnmatch(x, '*.csv')]
    poilst = [path.join(file_dir, x) for x in poifiles if x in poilst]
    return poilst


def _read_files(file_list, header, skip_footer, usecols):
    """
    Return a list of DataFrames.
    """

    lst = []
    for _file in file_list:
        lst.append(read_csv(_file,
                            header=header,
                            skip_footer=skip_footer,
                            usecols=usecols))
    return lst


def _merge_df(lst, length, drop_on):
    """
    Return a merged DataFrame
    """

    l = length - 1

    if l == 1:
        df = merge(lst[1], lst[0], how='outer', sort=True)
    else:
        df = merge(lst[l], _merge_df(lst, l, drop_on), how='outer', sort=True)

    df.drop_duplicates(drop_on, inplace=True)
    return df
