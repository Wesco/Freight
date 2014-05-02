'''
Created on Apr 30, 2014

@author: TReische
'''

from pandas import merge as _merge


def Poi(poi_dir):
    name_func = [lambda x: 'POI HISTORY ' + x + '.csv',
                 lambda x: 'POI OPEN ' + x + '.csv']
    file_list = _get_file_list(poi_dir, name_func)
    df_list = _read_files(file_list, 1, 0, [1, 40])
    df = _merge_data(df_list, len(file_list))
    df.drop_duplicates(' PO NUMBER', inplace=True)
    return df


def Oor(oor_dir):
    name_func = [lambda x: '3615 ' + x + 'ALLORDERS.csv']
    file_list = _get_file_list(oor_dir, name_func)
    return _merge_data(file_list, len(file_list))


def _get_file_list(file_dir, name_func):
    from fnmatch import fnmatch
    from datetime import datetime, timedelta
    from os import listdir, path

    poilst = []
    for i in range(0, 300):
        dt = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')

        if type(name_func) is list:
            for func in name_func:
                poilst.append(func(dt))
        else:
            poilst.append(name_func(dt))

    poifiles = [x for x in listdir(file_dir) if fnmatch(x, '*.csv')]
    poilst = [path.join(file_dir, x) for x in poifiles if x in poilst]
    return poilst


def _read_files(file_list, header, skip_footer, usecols):
    """
    Return a list of dataframes.
    """
    from pandas.io.parsers import read_csv

    lst = []
    for _file in file_list:
        lst.append(read_csv(_file,
                            header=header,
                            skip_footer=skip_footer,
                            usecols=usecols))
    return lst


def _merge_data(lst, length):
    l = length - 1

    if l == 1:
        df = _merge(lst[1], lst[0], how='outer', sort=True)
    else:
        df = _merge(lst[l], _merge_data(lst, l), how='outer', sort=True)

    return df
