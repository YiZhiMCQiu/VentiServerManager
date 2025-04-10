import wx;
import json;
import os;
from frame import *;

config = None
VSM_PATH = os.path.join(os.path.expanduser("~"), ".vsm")
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".vsm", "vsm.cfg")


if not os.path.exists(CONFIG_PATH):
    if not os.path.exists(VSM_PATH):
        os.mkdir(VSM_PATH)
    with open(CONFIG_PATH, encoding="utf-8", mode="w+") as file:
        file.write("{}")
with open(CONFIG_PATH, encoding="utf-8", mode="r+") as cfg:
    config = json.load(cfg)

def setConfig(key, value):
    config[key] = value
    with open(CONFIG_PATH, encoding="utf-8", mode="w+") as cfg:
        json.dump(config, cfg)

def getConfig():
    return config

def getTitleFont():
    return wx.Font(pointSize=20, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD, underline=False)

if __name__ == "__main__":
    app = wx.App()
    app.SetAppName("Venti Server Manager")

    mainFrame = MainFrame()
    mainFrame.Show(True)

    app.MainLoop()