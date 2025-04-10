import os;
import zipfile;
from datetime import datetime;
import shutil
from main import getConfig

BACKUP_PATH = os.path.join(os.path.dirname(getConfig()["serverJarPath"]), "backups")

def create_backup(world_folder):
    output_file = os.path.join(BACKUP_PATH, f"{os.path.basename(world_folder)}-{datetime.now().strftime('%Y%m%d%H%M%S')}.zip")
    print(output_file)
    if not os.path.exists(BACKUP_PATH):
        os.mkdir(BACKUP_PATH)
        with open(output_file, mode="w+"):
            pass
    create_backup_with_custom_name(world_folder, output_file)

def create_backup_with_custom_name(world_folder, output_file):
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(world_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, world_folder)
                zipf.write(file_path, arcname)

def back(world_folder, backup):
    shutil.rmtree(world_folder)
    os.mkdir(world_folder)
    with zipfile.ZipFile(backup, "r") as zipf:
        zipf.extractall(world_folder)