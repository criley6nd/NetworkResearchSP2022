import speedtest

st = speedtest.Speedtest()

for i in range(0,10):
	print(int(st.download()/1000000), "mb/s")
