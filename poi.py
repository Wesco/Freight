'''
Created on Apr 30, 2014

@author: TReische
'''

from datetime import datetime, timedelta
from os import path
from glob import glob


class Poi(object):

    def __init__(self, poi_dir):
        self._poi_dir = poi_dir

    @property
    def file_list(self):
        return _get_file_list(self._poi_dir)


def _get_file_list(poi_dir):
    poilst = []
    for i in range(0, 300):
        dt = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        poilst.append('POI HISTORY ' + dt + '.csv')
        poilst.append('POI OPEN ' + dt + '.csv')

    poifiles = glob(path.join(poi_dir, '*.csv'))
    poilst = [x for x in poifiles if x in poilst]

    print poilst

    return poilst
