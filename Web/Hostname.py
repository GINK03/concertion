import socket
import os
from os import environ as E

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

_hostname = None

def hostname():
    global _hostname
    if _hostname is None:
        if 'HOSTNAME' in E:
            _hostname = E['HOSTNAME']
        else:
            _hostname = get_ip() + ':8000'
    return _hostname

if __name__ == '__main__':
    print('my hostname is', hostname())

    
