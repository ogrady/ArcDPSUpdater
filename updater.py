import sys
import os
import shutil
import urllib.request
import re
import hashlib
import configparser

BASE_URL = "https://www.deltaconnected.com/arcdps/x64/"

D3D11_DLL_NAME = "d3d11.dll"
D3D11_DLL_URL = BASE_URL + D3D11_DLL_NAME
MD5_CHK_URL =  D3D11_DLL_URL + ".md5sum"

opener = urllib.request.URLopener()
opener.addheader("User-Agent", "whatever")


def download_d3d11():
    try:
        path,response = opener.retrieve(D3D11_DLL_URL)
        return path
    except urllib.error.URLError as urle:
        print("Error while downloading d3d11 from %s" % D3D11_DLL_URL,)
        print(urle)
        return False

def download_checksum():
    try:
        data = "".join([s.decode("utf-8") for s in opener.open(MD5_CHK_URL)])
        md5 = re.findall("^[^\s]*", data)
        if len(md5) == 0:
            print("Could not find a valid MD5 hash in remote.")
            return False
        return md5[0]
    except urllib.error.URLError as urle:
        print("Error while checking checksum from %s" % MD5_CHK_URL,)
        print(urle)
        return False

def check_checksum(file, checksum):
    with open(file, "rb") as fh:
        if not file:
            return False
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
    d3d11_path = "%s/%s" % (gw2path, D3D11_DLL_NAME)
    if os.path.isfile(d3d11_path) and check_checksum(d3d11_path, chk):
        print("ArcDPS is already up to date.")
    else:            
        path = download_d3d11()
        if check_checksum(path, chk):
            shutil.move(path, "%s/%s" % (gw2path, D3D11_DLL_NAME))
            print("Successfully updated ArcDPS.")
        else:
            print("Could not verify integrity of downloaded DLL.")

if __name__ == '__main__':
    main(sys.argv[1:])