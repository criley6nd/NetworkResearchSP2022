import sys
import os

os.system('netsh wlan show networks mode=bssid  >> interface.txt')
fp = open('interface.txt')