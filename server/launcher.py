import subprocess
import threading
import os
import wx

def create_process(path: str, callback) -> subprocess.Popen:
    process = subprocess.Popen(["java", "-jar", path, "--nogui"], cwd=os.path.dirname(path), 
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    threading.Thread(target=lambda *args: handle_shutdown(process, callback)).start()
    return process

def listen_output(process: subprocess.Popen, log_text: wx.TextCtrl):
    while process.poll() is None:
        if process.stdout is not None:
            wx.CallAfter(log_text.AppendText, process.stdout.readline())

def send(process: subprocess.Popen, command: str):
    if not process.stdin.closed:
        process.stdin.write(command.encode() + b"\n")
        process.stdin.flush()

def handle_shutdown(process: subprocess.Popen, callback):
    process.wait()
    callback(process.poll())
