'''
Created on Apr 30, 2014

@author: TReische
'''

from datetime import datetime, timedelta
from pandas import read_csv
from pandas import merge
from pandas import concat
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
    df_list = _read_files(file_list,
                          header=1,
                          skip_footer=0,
                          usecols=[' PO NUMBER', 'ORDER'],
                          converters={0: str, 1: str})
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
    df_list = _read_files(file_list,
                          header=1,
                          skip_footer=1,
                          usecols=[2, 3],
                          converters={'CUSTOMER': str, 'ORDER NO': str})

    df = _merge_df(df_list, len(df_list), 'ORDER NO')
    df.set_index(df['ORDER NO'], inplace=True)
    del df['ORDER NO']
    return df


def Gaps(gaps_dir, branch):
    """
    Return a DataFrame containing Gaps
    """

    fileName = ""
    df = None

    for i in range(0, 180):
        dt = datetime.today() - timedelta.days(i)
        fileName = "%s %s" % branch, dt

    filePath = path.join(gaps_dir, fileName)
    if path.isfile(filePath):
        df = read_csv(filePath, )

    return df


def SM(sm_dir):
    """
    Return a DataFrame containing Sales and Margin data
    """

    # List of wanted files
    sm_list = []
    for dt in _prev_months(6):
        fname = 'SM ' + dt.strftime('%Y-%m') + '-01.csv'
        sm_list.append(fname)

    # List of existing files
    sm_files = [x for x in listdir(sm_dir) if fnmatch(x, '*.csv')]

    # Wanted files that exist
    file_list = [path.join(sm_dir, x) for x in sm_files if x in sm_list]

    df_list = _read_files(file_list,
                         header=0,
                         skip_footer=0,
                         usecols=['dpc', 'dpc_name', 'mfr', 'item', 'sales'],
                         engine='c',
                         dtype={'dpc': str,
                                'dpc_name': str,
                                'mfr': str,
                                'item': str,
                                'sales': float})

    for i in range(0, len(df_list)):
        df = df_list[i]
        df_list[i] = df[df['sales'].apply(lambda y: y > 0)].dropna()

    merged_df = concat(df_list)

    return merged_df


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


def _read_files(file_list, header, skip_footer, usecols,
                engine='python', converters=None, dtype=None):
    """
    Return a list of DataFrames.
    """

    lst = []
    for _file in file_list:
        lst.append(read_csv(_file,
                            header=header,
                            skip_footer=skip_footer,
                            usecols=usecols,
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
        df = merge(lst[1], lst[0], how='outer', sort=True)
    else:
        df = merge(lst[l], _merge_df(lst, l, drop_on), how='outer', sort=True)

    if drop_on != None:
        df.drop_duplicates(drop_on, inplace=True)

    return df


def _prev_months(months=1):
    dt_list = []
    prevdt = datetime.now()

    for i in range(1, months + 1):  # @UnusedVariable
        currdt = prevdt - timedelta(days=prevdt.day)
        dt_list.append(currdt)
        prevdt = currdt

    return dt_list
