'''
Created on Apr 30, 2014

@author: TReische
'''

from ConfigParser import ConfigParser


class Config(object):

    def __init__(self):
        self._cfg_defaults = {'watch-dir': '\\\\raspi\\shared\\ups',
                              'poi-dir': '\\\\raspi\\shared\\POI History',
                              'oor-dir': '\\\\raspi\\shared\\117 History'}

        self._cfg = ConfigParser(self._cfg_defaults)
        self._cfg.read('config.ini')

        if not self._cfg.has_section('settings'):
            self._cfg.add_section('settings')

    def reload_config(self):
        self._cfg.read('config.ini')

    @property
    def watch_dir(self):
        return self._cfg.get('settings', 'watch-dir')

    @property
    def poi_dir(self):
        return self._cfg.get('settings', 'poi-dir')

    @property
    def oor_dir(self):
        return self._cfg.get('settings', 'oor-dir')
