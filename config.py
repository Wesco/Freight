'''
Created on Apr 30, 2014

@author: TReische
'''

from ConfigParser import SafeConfigParser
from StringIO import StringIO
import csv
from getpass import getuser


class Config(object):

    def __init__(self, cfg_file='config.ini'):
        user = getuser()
        self._cfg_defaults = \
        {
         'watch_dir': r'\\br3615gaps\gaps\UPS\drop_in',
         'open_poi_dir': r'\\br3615gaps\gaps\3615 POI Report\OPEN',
         'history_poi_dir': r'\\br3615gaps\gaps\3615 POI Report\HISTORY',
         'oor_dir': r'\\br3615gaps\gaps\3615 117 Report\DETAIL\ByOrderDate',
         'output_dir': r'\\br3615gaps\gaps\UPS',
         'write_to_disk': 'yes',
         'branch': '3615',
         'incoming_search': 'wesco,5521',
         'send_email': 'yes',
         'send_to': user + '@wesco.com',
         'send_from': user + '@wesco.com',
        }

        self._cfg = SafeConfigParser(self._cfg_defaults)
        self._cfg.read(cfg_file)

        cfg_sections = ['settings', 'email', 'branch']
        for section in cfg_sections:
            if not self._cfg.has_section(section):
                self._cfg.add_section(section)

    def reload_config(self):
        self._cfg = SafeConfigParser(self._cfg_defaults)
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
    def write_to_disk(self):
        return self._cfg.getboolean('settings', 'write_to_disk')

    @property
    def branch(self):
        return self._cfg.get('branch', 'branch')

    @property
    def incoming_search(self):
        inc = self._cfg.get('branch', 'incoming_search').replace("\n", ",")
        lst = csv.reader(StringIO(inc))
        result = []
        result.extend(y for x in lst for y in x if y != '')
        return result

    @property
    def send_email(self):
        return self._cfg.getboolean('email', 'send_email')

    @property
    def send_to(self):
        return self._cfg.get('email', 'send_to')

    @property
    def send_from(self):
        return self._cfg.get('email', 'send_from')
