from main import getConfig
import os

SERVER_PROPERTIES = None

def load(file):
    return loads(file.read())

def loads(s: str):
    result = {}
    for line in s.split("\n"):
        result[line.split("=")[0]] = "=".join(line.split("=")[1:])
    return result

def load_server_properties():
    global SERVER_PROPERTIES
    with open(os.path.join(os.path.dirname(getConfig()["serverJarPath"]), "server.properties"), encoding="utf-8", mode="r+") as file:
        SERVER_PROPERTIES = load(file)
    