'''
Created on Apr 30, 2014

@author: TReische
'''

from datetime import datetime, timedelta
from os import path, listdir
from fnmatch import fnmatch


class Poi(object):

    def __init__(self, poi_dir):
        self._poi_dir = poi_dir
        self._file_list = _get_poi_list(self._poi_dir)

    @property
    def file_list(self):
        return self._file_list

    @property
    def dataframe(self):
        pass


def _get_poi_list(poi_dir):
    poilst = []
    for i in range(0, 300):
        dt = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        poilst.append('POI HISTORY ' + dt + '.csv')
        poilst.append('POI OPEN ' + dt + '.csv')

    poifiles = [x for x in listdir(poi_dir) if fnmatch(x, '*.csv')]
    poilst = [x for x in poifiles if x in poilst]
    return poilst


def _merge_data():
    pass
