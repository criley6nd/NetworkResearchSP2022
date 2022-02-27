import dpkt
import sys
import pandas as pd
import matplotlib.pyplot as plt

#CorbettinClass.pcap

f = open(sys.argv[1], 'rb')
pcap = dpkt.pcap.Reader(f)

acks = {}
ackarr = {}

retrans = {}
retransarr = {}

count = 1
timecount = 0
first = True
time0 = 0
startime = 0
window = 5

for timestamp, buf in pcap:
    #gets initial time stamp
    if first:
        time0 = timestamp
        startime = time0
        first = False

    #parses data out of packets
    eth1 = dpkt.ethernet.Ethernet(buf)
    dat = eth1.data
    
    #checks if data in tcp format
    try:
        dat.tcp.ack
        #find ack flag
    except:
        continue

    #parses ack flag
    flags = dat.tcp.flags
    aflag = flags >> 4
    if aflag % 2 == 0: 
        continue

    #gets time since reset time
    vectime = timestamp - time0
    count += 1
    
    #continues if FIN ack because ack num repeated


    #throw fin acks in its own category
    if flags % 2 == 1:
        continue
    #else:
        #continue

    #pulls ack and sequence number and payload
    acknum = dat.tcp.ack
    seqnum = dat.tcp.seq
    payload = dat.tcp.data

    #if payload is empty, it's an ack
    isack = False
    if len(payload) == 0:
        isack = True

    #adds acknum to dictionary and checks how many times
    #it's repeated, does the same thing with sequence numbers
    #when there is a payload
    if acknum in acks and isack:
        acks[acknum] += 1
    elif isack:
        acks[acknum] = 1
    elif seqnum in retrans:
        retrans[seqnum] += 1
    else:
        retrans[seqnum] = 1
    

    #checks if packet is within time window
    if vectime > window:
        #goes through dictionaries to find dup acks and
        #retransmits
        ackcount = 0
        for key in acks:
            if acks[key] > 1:
                ackcount += acks[key]
        
        acks = {}
        ackdf = pd.DataFrame.from_dict(acks) 
        
        seqcount = 0
        for key in retrans:
            if retrans[key] > 1:
                seqcount += retrans[key]
        retrans = {}

        currtime = timestamp - startime
        ackarr[int(currtime)] = float(ackcount) /count
        #print(currtime, float(ackcount), count)
        retransarr[int(currtime)] = float(seqcount) /count

        time0 = timestamp
        count = 0


ackdatarr = []
times = []
for i in range(1,int(currtime)):
    if i in ackarr:
        if ackarr[i] != 0:
            ackdatarr.append(ackarr[i])
            times.append(i)

d = {'time':times, 'dup ack %':ackdatarr}
df = pd.DataFrame(d)

df.plot(x='time', y = 'dup ack %', kind='scatter')
plt.title(f'{sys.argv[1]} dup ack percentage')
plt.show()


    

