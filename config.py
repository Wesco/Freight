'''
Created on Apr 30, 2014

@author: TReische
'''

from ConfigParser import ConfigParser
import StringIO
import csv


class Config(object):

    def __init__(self, cfg_file='config.ini'):
        self._cfg_defaults = \
        {
         'watch_dir': r'\\br3615gaps\gaps\UPS\drop_in',
         'open_poi_dir': r'\\br3615gaps\gaps\3615 POI Report\OPEN',
         'history_poi_dir': r'\\br3615gaps\gaps\3615 POI Report\HISTORY',
         'oor_dir': r'\\br3615gaps\gaps\3615 117 Report\DETAIL\ByOrderDate',
         'output_dir': r'\\br3615gaps\gaps\UPS',
         'branch': '3615',
         'email_to': 'treische@wesco.com',
         'email_from': 'treische@wesco.com',
         'incoming_search': 'wesco,5521',
        }

        self._cfg = ConfigParser(self._cfg_defaults)
        print cfg_file
        self._cfg.read(cfg_file)

        if not self._cfg.has_section('settings'):
            self._cfg.add_section('settings')

    def reload_config(self):
        self._cfg.read('config.ini')

    @property
    def watch_dir(self):
        return self._cfg.get('settings', 'watch_dir')

    @property
    def open_poi_dir(self):
        return self._cfg.get('settings', 'open_poi_dir')

    @property
    def hist_poi_dir(self):
        return self._cfg.get('settings', 'history_poi_dir')

    @property
    def oor_dir(self):
        return self._cfg.get('settings', 'oor_dir')

    @property
    def output_dir(self):
        return self._cfg.get('settings', 'output_dir')

    @property
    def branch(self):
        return self._cfg.get('settings', 'branch')

    @property
    def email_to(self):
        return self._cfg.get('settings', 'email_to')

    @property
    def email_from(self):
        return self._cfg.get('settings', 'email_from')

    @property
    def incoming_search(self):
        inc = self._cfg.get('settings', 'incoming_search')
        inc = inc.replace("\n", ",")
        strio = StringIO.StringIO(inc)
        lst = csv.reader(strio)
        result = []
        result.extend(y for x in lst for y in x if y != '')
        return result
