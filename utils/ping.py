import os

def ping(ip):
    return os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1") == 0