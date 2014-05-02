'''
Created on Apr 30, 2014

@author: TReische
'''


def Poi(poi_dir):
    name_func = [lambda x: 'POI HISTORY ' + x + '.csv',
                 lambda x: 'POI OPEN ' + x + '.csv']
    file_list = _get_file_list(poi_dir, name_func)

    return _merge_data(file_list, len(file_list))


def Oor(oor_dir):
    name_func = [lambda x: '3615 ' + x + 'ALLORDERS.csv']
    file_list = _get_file_list(oor_dir, name_func)
    return _merge_data(file_list, len(file_list))


def _get_file_list(file_dir, name_func):
    from fnmatch import fnmatch
    from datetime import datetime, timedelta
    from os import listdir

    poilst = []
    for i in range(0, 300):
        dt = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')

        if type(name_func) is list:
            for func in name_func:
                poilst.append(func(dt))
        else:
            poilst.append(name_func(dt))

    poifiles = [x for x in listdir(file_dir) if fnmatch(x, '*.csv')]
    poilst = [x for x in poifiles if x in poilst]
    return poilst


def _merge_data(lst, length):
    from pandas import merge

    l = length - 1

    if l == 1:
        df = merge(lst[1], lst[0], how='outer', sort=True)
    else:
        df = merge(lst[l], _merge_data(lst, l), how='outer', sort=True)

    return df
