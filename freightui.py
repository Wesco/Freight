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
        self.Show()

    def OnInit(self):
        panel1 = wx.Panel(self, -1)
        panel1.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        panel2 = wx.Panel(self, -1)
        panel2.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        panel3 = wx.Panel(self, -1)
        panel3.SetSizer(wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5))

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(panel1, 0, wx.EXPAND)
        hsizer.Add(panel2, 1, wx.EXPAND)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(hsizer, 1, wx.EXPAND)
        vsizer.Add(panel3, 0, wx.EXPAND)

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

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLBSelect, id=101)

        # Create listbox2
        self.listbox2 = wx.ListCtrl(parent=panel2,
                               id=102,
                               size=(400, -1),
                               style=wx.LC_REPORT | wx.LC_SINGLE_SEL)

        self.listbox2.InsertColumn(0, 'Setting')
        self.listbox2.InsertColumn(1, 'Value')
        self.listbox2.SetColumnWidth(0, 120)
        self.listbox2.SetColumnWidth(1, 250)

        # Add self.listbox to panel2
        panel2.Sizer.Add(item=self.listbox2,
                         proportion=1,
                         flag=wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM,
                         border=5)

        # Panel 3
        upsstatictext = wx.StaticText(panel3, id=201, label='UPS Report')
        upstextctrl = wx.TextCtrl(panel3, id=202)
        upsbutton = wx.Button(panel3, id=203, label='Browse')

        outputstatictext = wx.StaticText(panel3, id=301, label='Output File')
        outputtextctrl = wx.TextCtrl(panel3, id=302)
        outputbutton = wx.Button(panel3, id=303, label='Browse')

        panel3.Sizer.AddMany([(upsstatictext, 0, wx.LEFT, 7),
                              (upstextctrl, 0, wx.EXPAND),
                              (upsbutton, wx.RIGHT, 7),
                              (outputstatictext, 0, wx.LEFT, 7),
                              (outputtextctrl, 0, wx.EXPAND | wx.BOTTOM, 7),
                              (outputbutton, 0, wx.BOTTOM | wx.RIGHT, 7)])

        panel3.Sizer.AddGrowableCol(1, 0)

        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        self.Fit()
        self.SetMinSize(wx.Size(400, 250))
        self.SetSize((540, 375))

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
