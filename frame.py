if __name__ == "__main__":
    __import__("os").system("python main.py")
    exit()

import wx;
import wx.stc as stc;
import wx.grid as gridlib;
from server.launcher import *;
import threading;
from lexer import PropertiesLexer;
from main import getConfig, setConfig, getTitleFont;
import json;
from server.backup import *
from server import properties

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, -1, "Venti Server Manager", style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        if "serverJarPath" not in getConfig():
            self.request_select_server()
        properties.load_server_properties()
        self.panel = wx.Panel(self)
        self.state_button = wx.Button(self.panel, label="启动")
        self.state_button.Bind(wx.EVT_BUTTON, self.on_button_click)

        self.restart_button = wx.Button(self.panel, label="重启")
        self.restart_button.Bind(wx.EVT_BUTTON, self.on_restart_button_click)
        self.restart_button.Disable()

        view_info_button = wx.Button(self.panel, label="查看信息")
        view_info_button.Bind(wx.EVT_BUTTON, lambda event: ServerInfoFrame().Show(True))

        edit_properties_button = wx.Button(self.panel, label="编辑server.properties")
        edit_properties_button.Bind(wx.EVT_BUTTON, lambda *args:ServerPropertiesFrame(self.on_restart_button_click, os.path.join(os.path.dirname(getConfig()["serverJarPath"]), "server.properties")).Show(True))

        self.log_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.command_ctrl = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.command_ctrl.SetHint("> 输入指令")
        self.command_ctrl.Bind(wx.EVT_TEXT_ENTER, self.commit_command)

        reset_server_button = wx.Button(self.panel, label="更改服务器")
        reset_server_button.Bind(wx.EVT_BUTTON, self.on_reset_server_button_click)

        backup_button = wx.Button(self.panel, label="备份管理")
        backup_button.Bind(wx.EVT_BUTTON, lambda event: BackupFrame(self.on_restart_button_click).Show(True))

        title_text = wx.StaticText(self.panel, label=os.path.basename(os.path.dirname(getConfig()["serverJarPath"])))
        title_text.SetFont(getTitleFont())

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(title_text, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.state_button, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.restart_button, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(edit_properties_button, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(view_info_button, 0, wx.ALL | wx.EXPAND, 5)
        left_sizer.Add(backup_button, 0, wx.ALL | wx.EXPAND, 5)
        left_sizer.AddStretchSpacer(1)
        left_sizer.Add(reset_server_button, 0, wx.EXPAND | wx.ALL, 5)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(self.command_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(left_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(right_sizer, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(main_sizer)

        
        self.server_process = None


        self.SetSize((800, 600))
        self.Center()

    def on_button_click(self, event):
        if self.server_process is None:
            self.log_text.Clear()
            self.server_process = create_process(getConfig()["serverJarPath"], self.on_process_end)
            threading.Thread(target=lambda *args: listen_output(self.server_process, self.log_text)).start()
            self.state_button.SetLabel("强制关闭")
            self.restart_button.Enable()
        else:
            if wx.MessageBox("服务器仍在运行！\n若您强制关闭服务器，一些更改可能不会被保存。", "警告", wx.YES_NO | wx.ICON_WARNING) == wx.YES:
                self.server_process.kill()
                self.server_process = None
                self.state_button.SetLabel("启动")
    
    def on_restart_button_click(self, *args):
        if self.server_process == None:
            self.on_button_click(None)
        else:
            send(self.server_process, "kick @a 服务器正在重启")
            send(self.server_process, "stop")
            threading.Thread(target=self.restart).start()

    def restart(self):
        self.server_process.wait()
        self.server_process = create_process(getConfig()["serverJarPath"], self.on_process_end)
        wx.CallAfter(self.log_text.Clear)
        wx.CallAfter(self.restart_button.Enable)
        wx.CallAfter(self.state_button.SetLabel, "强制关闭")
        threading.Thread(target=lambda *args: listen_output(self.server_process, self.log_text)).start()

    def commit_command(self, event):
        if self.server_process is None:
            wx.MessageBox("未启动服务器！", "错误", wx.OK | wx.ICON_ERROR)
        else:
            send(self.server_process, self.command_ctrl.GetValue())
            self.command_ctrl.Clear()
    
    def on_process_end(self, exit_code):
        wx.CallAfter(self.log_text.AppendText, "[VSM] 进程已结束，退出代码" + str(exit_code) + "。\n")
        self.server_process = None
        self.state_button.SetLabel("启动")
        self.restart_button.Disable()
    
    def request_select_server(self):
        with wx.FileDialog(self, "选择服务器核心", wildcard="Java归档 (*.jar)|*.jar",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                setConfig("serverJarPath", fileDialog.GetPath())
    
    def on_reset_server_button_click(self, event):
        self.request_select_server()
        self.Close()
        MainFrame().Show(True)

class ServerPropertiesFrame(wx.Frame):
    def __init__(self, restart, path):
        super().__init__(None, -1, "设置server.properties", style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.restart_callback = restart
        self.file_path = path

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.code = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.HSCROLL)
        self.code.SetFont(wx.Font(pointSize=16, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL, underline=False))
        with open(path, encoding="utf-8", mode="r+") as file:
            self.code.SetValue(file.read())

        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_button = wx.Button(self.panel, label="保存")
        self.cancel_button = wx.Button(self.panel, label="取消")
        self.save_and_restart_button = wx.Button(self.panel, label="保存并重启")

        self.save_button.Bind(wx.EVT_BUTTON, self.save_button_click)
        self.cancel_button.Bind(wx.EVT_BUTTON, lambda *args: self.Close())
        self.save_and_restart_button.Bind(wx.EVT_BUTTON, self.save_and_restart_button_click)

        bottom_sizer.Add(self.save_button, 0, wx.ALL | wx.EXPAND, 5)
        bottom_sizer.Add(self.cancel_button, 0, wx.ALL | wx.EXPAND, 5)
        bottom_sizer.Add(self.save_and_restart_button, 0, wx.ALL | wx.EXPAND, 5)

        self.sizer.Add(self.code, 1, wx.ALL | wx.EXPAND, 5)
        self.sizer.Add(bottom_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.panel.SetSizer(self.sizer)

        self.SetSize((800, 600))
        self.Center()
    
    def save_button_click(self, event):
        print(event)
        self.save()
        self.Close()

    def save_and_restart_button_click(self, event):
        self.save()
        self.Close()
        self.restart_callback()

    def save(self):
        with open(self.file_path, encoding="utf-8", mode="w+") as file:
            file.write(self.code.GetValue())

class ServerInfoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, -1, "", style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.server_path = os.path.dirname(getConfig()["serverJarPath"])
        self.server_name = os.path.basename(self.server_path)
        self.SetTitle(self.server_name)

        if not os.path.exists(os.path.join(self.server_path, "versions")):
            wx.MessageBox("请先启动一次服务器！", "错误", wx.OK | wx.ICON_ERROR)
            self.Close()
        else:
            self.server_version = list(filter(lambda file: file != ".DS_Store", os.listdir(os.path.join(self.server_path, "versions"))))[0]
            self.ops = []
            self.banned_players = []
            with open(os.path.join(self.server_path, "ops.json"), encoding="utf-8", mode="r+") as file:
                ops = json.load(file)
                for op in ops:
                    self.ops.append({"name": op["name"], "level": op["level"]})
            with open(os.path.join(self.server_path, "banned-players.json"), encoding="utf-8", mode="r+") as file:
                banned_players = json.load(file)
                for banned_player in banned_players:
                    self.banned_players.append({"name": banned_player["name"], "handler": banned_player["source"], "reason": banned_player["reason"]})
            
            info_text = wx.StaticText(panel, label="基本信息")
            info_text.SetFont(getTitleFont())


            sizer.Add(info_text, 0, wx.ALL | wx.EXPAND, 5)
            sizer.Add(wx.StaticText(panel, label=f"服务端版本: {self.server_version}"), 0, wx.ALL | wx.EXPAND, 5)

            banned_players_grid_text = wx.StaticText(panel, label="封禁名单")
            banned_players_grid_text.SetFont(getTitleFont())
            self.banned_players_grid = gridlib.Grid(panel)
            self.banned_players_grid.CreateGrid(len(self.banned_players), 3)

            self.banned_players_grid.SetColLabelValue(0, "玩家名")
            self.banned_players_grid.SetColLabelValue(1, "处理人")
            self.banned_players_grid.SetColLabelValue(2, "原因")
            for i in range(0, len(self.banned_players)):
                self.banned_players_grid.SetRowLabelValue(i, f"#{i+1}")
                self.banned_players_grid.SetCellValue(i, 0, self.banned_players[i]["name"])
                self.banned_players_grid.SetCellValue(i, 1, self.banned_players[i]["handler"])
                self.banned_players_grid.SetCellValue(i, 2, self.banned_players[i]["reason"])
            self.banned_players_grid.AutoSizeColumns()
            self.banned_players_grid.AutoSizeRows()
            self.banned_players_grid.AutoSizeColLabelSize(2)
            self.banned_players_grid.EnableEditing(False)
            self.banned_players_grid.SetScrollbars(0, 0, 0, 0)

            ops_grid_text = wx.StaticText(panel, label="管理员名单")
            ops_grid_text.SetFont(getTitleFont())
            self.ops_grid = gridlib.Grid(panel)
            self.ops_grid.CreateGrid(len(self.ops), 2)

            self.ops_grid.SetColLabelValue(0, "玩家名")
            self.ops_grid.SetColLabelValue(1, "权限等级")
            for i in range(0, len(self.ops)):
                self.ops_grid.SetRowLabelValue(i, f"#{i+1}")
                self.ops_grid.SetCellValue(i, 0, self.ops[i]["name"])
                self.ops_grid.SetCellValue(i, 1, str(self.ops[i]["level"]))
            self.ops_grid.AutoSizeColumns()
            self.ops_grid.AutoSizeRows()
            self.ops_grid.EnableEditing(False)
            self.ops_grid.SetScrollbars(0, 0, 0, 0)
            
            sizer.Add(banned_players_grid_text, 0, wx.ALL | wx.EXPAND, 5)
            sizer.Add(self.banned_players_grid, 0, wx.ALL | wx.EXPAND, 5)
            sizer.Add(ops_grid_text, 0, wx.ALL | wx.EXPAND, 5)
            sizer.Add(self.ops_grid, 0, wx.ALL | wx.EXPAND, 5)
            panel.SetSizer(sizer)

            self.SetSize((500, 400))

class BackupFrame(wx.Frame):
    def __init__(self, restart_callback):
        super().__init__(None, -1, "备份列表", style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.restart = restart_callback
        self.world_folder = properties.SERVER_PROPERTIES["level-name"]

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        if not os.path.exists(BACKUP_PATH):
            os.mkdir(BACKUP_PATH)

        backups_text = wx.StaticText(panel, label="备份列表")
        backups = list(filter(lambda file: file != ".DS_Store", os.listdir(BACKUP_PATH)))

        self.backups_list = wx.Choice(panel, choices=backups)
        self.backups_list.SetSelection(0)

        apply_button = wx.Button(panel, label="应用")
        apply_button.Bind(wx.EVT_BUTTON, self.apply_backup)
        apply_and_restart_button = wx.Button(panel, label="应用并重启")
        apply_and_restart_button.Bind(wx.EVT_BUTTON, self.apply_backup_and_restart)
        backup_button = wx.Button(panel, label="创建备份")
        backup_button.Bind(wx.EVT_BUTTON, self.backup)

        bottom_sizer.Add(apply_button, 0, wx.ALL | wx.EXPAND, 5)
        bottom_sizer.Add(apply_and_restart_button, 0, wx.ALL | wx.EXPAND, 5)
        bottom_sizer.Add(backup_button, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(backups_text, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.backups_list, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(bottom_sizer, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
    
    def apply_backup(self, event):
        selected_backup = self.backups_list.GetStringSelection()
        if selected_backup == None:
            wx.MessageBox("请先选择一个备份！", "错误", wx.ICON_ERROR | wx.OK)
            return False
        back(world_folder=os.path.join(os.path.dirname(BACKUP_PATH), self.world_folder), backup=os.path.join(BACKUP_PATH, selected_backup))
        return True

    def apply_backup_and_restart(self, event):
        if self.apply_backup(event):
            self.restart(event)
    
    def backup(self, *args):
        create_backup(self.world_folder)
        wx.MessageBox("备份成功", "提示", wx.ICON_INFORMATION | wx.OK)
        self.Close()
        BackupFrame(self.restart).Show(True)