'''
Created on May 23, 2014

@author: TReische
'''

import wx
import glob
import config


def getconfig(cfg):
    conf = config.Config(cfg)
    return conf.raw_config()


def getfiles():
    lst = glob.glob('*.ini')
    return lst


class MainWindow(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, -1, title)
        self.listbox = None
        self.listbox2 = None
        self.OnInit()
        self.Layout()
        self.Center()
        self.Show()

    def OnInit(self):
        panel1 = wx.Panel(self, -1)
        panel1.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        panel2 = wx.Panel(self, -1)
        panel2.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        panel3 = wx.Panel(self, -1)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(panel1, 0, wx.EXPAND)
        hsizer.Add(panel2, 1, wx.EXPAND)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(hsizer, 1, wx.EXPAND)
        vsizer.Add(panel3, 1, wx.EXPAND)

        # Add to panel1
        self.listbox = wx.ListCtrl(parent=panel1,
                             id=101,
                             size=(120, -1),
                             style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listbox.InsertColumn(0, 'Config')
        self.listbox.SetColumnWidth(0, 120)

        file_list = getfiles()
        for i in file_list:
            self.listbox.Append((i,))

        panel1.Sizer.Add(item=self.listbox,
                         proportion=1,
                         flag=wx.ALL | wx.EXPAND,
                         border=5)

        # Create self.listbox
        self.listbox2 = wx.ListCtrl(parent=panel2,
                               id=102,
                               size=(400, -1),
                               style=wx.LC_REPORT | wx.LC_SINGLE_SEL)

        self.listbox2.InsertColumn(0, 'Setting')
        self.listbox2.InsertColumn(1, 'Value')
        self.listbox2.SetColumnWidth(0, 120)
        self.listbox2.SetColumnWidth(1, 250)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLBSelect, id=101)

        # Add self.listbox to panel2
        panel2.Sizer.Add(item=self.listbox2,
                         proportion=1,
                         flag=wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM,
                         border=5)

        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        self.Fit()

    def OnLBSelect(self, event):
        lst = getconfig(event.Label)
        self.listbox2.DeleteAllItems()
        for y in lst:
            self.listbox2.Append(y)


class freightApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        MainWindow('Freight')


if __name__ == '__main__':
    app = freightApp()
    app.MainLoop()
