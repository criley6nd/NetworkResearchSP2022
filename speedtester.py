import os
import sys
import speedtest
from datetime import datetime
from multiprocessing import Process
from getDeviceData import getDeviceData
import subprocess
from packetParse import packetParse
import pandas as pd

#function to be run in parallel with main
#runs a packet capture while speedtests are being run
def f():
	results = subprocess.check_output(['tshark', '-w', 'pshark.pcap', '-a', 'duration:20','-i','Wi-Fi','-F','pcap']).decode()
	
	

if __name__ == '__main__':
	#gets date and time to be used as a directory name
	dt = str(datetime.now()).split()
	#creates directory with the date as the title
	path = os.getcwd()
	date = dt[0] 
	#creates a directory with the date if one doesn't exist and a subdirectory 
	#with the inputted name
	dirname = path + '\\' + date + '\\' + sys.argv[1]
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	#calls the getDeviceData function which returns the number of visable
	#addresses and the current lat and long coordinates
	addresses, coords = getDeviceData(dt, dirname)

	#starts up process to run packet capture
	p = Process(target=f, args=())
	p.start()

	#runs speeds number of speedtests, writes the results to
	#a file in the created directory 
	speeds = 5
	tests = 0
	f = open(dirname+'\\speeds.txt', 'w')
	for i in range(0,speeds):
		print(f'doing speedtest {i + 1}', end='\r')
		#creates a new speedtest object and tests for download speed
		st = speedtest.Speedtest()
		dspeed = int(st.download()/1000000)
		#keeps track of data to find an average and writes each result
		#to the file
		tests += dspeed
		f.write(str(dspeed) + '\n')
	f.close()

	#calculates average speed to print out and send to heat map data
	avgSpeed = tests / speeds
	print(f'\x1b[Kdownload speed is {avgSpeed} mb/s')
	#joins the second process
	p.join()

	#runs the packetParse function on the created packet capture
	#gets back the average percentage of duplicate acks over the capture
	#deletes file when it is done parsing as it is usually a very large file 
	dups = packetParse(dirname, 'pshark.pcap')
	os.remove('pshark.pcap')

	#Reads in data from json file containing the dataframe with previous results
	#
	#	to use a different file for heat map data change the name here
	#
	df = pd.read_json('heat_map_data.json')

	#creates a new row with the new data to be added to the dataframe
	#then uses concat and reindex functions to combine the new dataframe to the
	#read in dataframe
	data = [[dups, avgSpeed, addresses, coords]]
	df2 = pd.DataFrame({'dups':dups,'speed':avgSpeed,'addrs':addresses,'coords':[coords]})
	df = pd.concat([df, df2])
	df.reset_index(inplace=True, drop=True)

	#writes dataframe to json file to be read in for the next test or used to make a heatmap
	#
	#	to use a different file for heat map data also change the name here
	#
	df.to_json('heat_map_data.json')
	