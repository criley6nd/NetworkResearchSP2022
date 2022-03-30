import os
import sys
import speedtest

st = 10

os.system("tshark -w pshark.pcap -a duration:20 -i Wi-Fi")

for i in range(0,10):
	print(int(st.download()/1000000), "mb/s")