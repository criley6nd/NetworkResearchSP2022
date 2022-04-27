# import speedtest

# st = speedtest.Speedtest()

# for i in range(0,10):
# 	print(int(st.download()/1000000), "mb/s")


import os
import sys
import speedtest
from datetime import datetime
from multiprocessing import Process
from getDeviceData import getDeviceData
import subprocess
from packetParse import packetParse

def f():
	#os.system("tshark -w pshark.pcap -a duration:20 -i Wi-Fi -F pcap")
	results = subprocess.check_output(['tshark', '-w', 'pshark.pcap', '-a', 'duration:20','-i','Wi-Fi','-F','pcap']).decode()
	
	

if __name__ == '__main__':
	dt = str(datetime.now()).split()
	#creates directory with the date as the title
	path = os.getcwd()
	date = dt[0] 
	dirname = path + '\\' + date + '\\' + sys.argv[1]
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	getDeviceData(dt, dirname)
	p = Process(target=f, args=())
	p.start()
	speeds = 5
	tests = 0
	f = open(dirname+'\\speeds.txt', 'w')
	for i in range(0,speeds):
		print(f'doing speedtest {i + 1}', end='\r')
		st = speedtest.Speedtest()
		dspeed = int(st.download()/1000000)
		tests += dspeed
		f.write(str(dspeed) + '\n')
	print(f'\x1b[Kdownload speed is {tests / speeds} mb/s')
	p.join()
	packetParse(dirname, 'pshark.pcap')
	os.remove('pshark.pcap')
	








