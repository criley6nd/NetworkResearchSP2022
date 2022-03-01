# import speedtest

# st = speedtest.Speedtest()

# for i in range(0,10):
# 	print(int(st.download()/1000000), "mb/s")


import os
import sys
import speedtest
from multiprocessing import Process

def f(name):
	print('hello', name)
	os.system("tshark -w pshark.pcap -a duration:20 -i Wi-Fi -F pcap")
	

if __name__ == '__main__':
	p = Process(target=f, args=('bob',))
	p.start()
	st = speedtest.Speedtest()
	print(int(st.download()/1000000), "mb/s")
	arr = st.get_config()
	for key in arr:
		print(key, arr[key])
	p.join()
	os.system("python packetParse.py pshark.pcap")



#




