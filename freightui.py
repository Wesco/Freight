'''
Created on May 23, 2014

@author: TReische
'''

import wx
import glob
import config


def getconfig():
    conf = config.Config()
    return conf.raw_config()


def getfiles():
    lst = glob.glob('*.ini')
    return lst


class MainWindow(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, -1, title)
        self.OnInit()
        self.Layout()
        self.Center()
        self.Show()

    def OnInit(self):
        panel1 = wx.Panel(self, -1)
        panel1.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        panel2 = wx.Panel(self, -1)
        panel2.SetSizer(wx.FlexGridSizer(2, 3, 5, 5))
        panel3 = wx.Panel(self, -1)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(panel1, 0, wx.EXPAND)
        hsizer.Add(panel2, 1, wx.EXPAND)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(hsizer, 1, wx.EXPAND)
        vsizer.Add(panel3, 1, wx.EXPAND)

        # Add to panel1
        file_list = getfiles()
        listbox = wx.ListBox(panel1, -1, (-1, -1), (-1, 156), file_list)
        panel1.Sizer.Add(
                         listbox, 1, wx.TOP | wx.RIGHT | wx.LEFT | wx.BOTTOM, 5
                         )

        # Add to panel2
        lst = [x + " : " + str(y) for x, y in getconfig()]
        listbox2 = wx.ListCtrl(panel2, -1, (-1, -1), (-1, 156))
        listbox2.InsertColumn(0, 'Derp')
        #listbox2.SetItemCount(0, len(lst))
        for x, y in enumerate(lst):
            listbox2.Append(y)
            #listbox2.SetStringItem(x, 0, y)
        panel2.Sizer.Add(listbox2, 1, wx.TOP | wx.BOTTOM | wx.RIGHT, 5)

        # Add to panel3

        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        self.Fit()


class freightApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        MainWindow('Freight')


if __name__ == '__main__':
    app = freightApp()
    app.MainLoop()
