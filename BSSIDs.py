import sys
import os

os.system('netsh wlan show networks mode=bssid c  >> interface.txt')
fp = open('interface.txt')