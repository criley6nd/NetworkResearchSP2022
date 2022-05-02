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
import pandas as pd

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
	addresses, coords = getDeviceData(dt, dirname)
	p = Process(target=f, args=())
	p.start()
	speeds = 2
	tests = 0
	f = open(dirname+'\\speeds.txt', 'w')
	for i in range(0,speeds):
		print(f'doing speedtest {i + 1}', end='\r')
		st = speedtest.Speedtest()
		dspeed = int(st.download()/1000000)
		tests += dspeed
		f.write(str(dspeed) + '\n')
	avgSpeed = tests / speeds
	print(f'\x1b[Kdownload speed is {avgSpeed} mb/s')
	p.join()
	dups = packetParse(dirname, 'pshark.pcap')
	os.remove('pshark.pcap')
	df = pd.read_json('heat_map_data.json')
	data = [[dups, avgSpeed, addresses, coords]]
	df2 = pd.DataFrame({'dups':dups,'speed':avgSpeed,'addrs':addresses,'coords':[coords]})
	df = pd.concat([df, df2])
	df.reset_index(inplace=True, drop=True)
	print(df)
	df.to_json('heat_map_data.json')
	








