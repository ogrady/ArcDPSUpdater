import sys
import os
import shutil
import urllib.request
import re
import hashlib
import configparser

BASE_URL = "https://www.deltaconnected.com/arcdps/x64/"

D3D9_DLL_NAME = "d3d9.dll"
D3D9_DLL_URL = BASE_URL + D3D9_DLL_NAME
MD5_CHK_URL =  D3D9_DLL_URL + ".md5sum"

def download_d3d9():
    try:
        path,response = urllib.request.urlretrieve(D3D9_DLL_URL)
        return path
    except urllib.error.URLError as urle:
        print(urle)
        return False

def download_checksum():
    try:
        data = "".join([s.decode("utf-8") for s in urllib.request.urlopen(MD5_CHK_URL)])
        md5 = re.findall("^[^\s]*", data)
        if len(md5) == 0:
            print("Could not find a valid MD5 hash in remote.")
            return False
        return md5[0]
    except urllib.error.URLError as urle:
        print(urle)
        return False

def check_checksum(file, checksum):
    with open(file, "rb") as fh:
        m = hashlib.md5()
        for chunk in iter(lambda: fh.read(4096), b""):
            m.update(chunk)
        h = m.hexdigest()
        return h == checksum
    return False

def main(args):
    config = configparser.ConfigParser()
    config.read("config.ini")
    gw2path = config["GW2"]["path"]
    
    chk = download_checksum()
    d3d9_path = "%s/%s" % (gw2path, D3D9_DLL_NAME)
    if os.path.isfile(d3d9_path) and check_checksum(d3d9_path, chk):
        print("ArcDPS is already up to date.")
    else:            
        path = download_d3d9()
        if check_checksum(path, chk):
            shutil.move(path, "%s/%s" % (gw2path, D3D9_DLL_NAME))
            print("Successfully updated ArcDPS.")
        else:
            print("Could not verify integrity of downloaded DLL.")

if __name__ == '__main__':
    main(sys.argv[1:])