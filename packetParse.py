import dpkt
import sys
import pandas as pd
import matplotlib.pyplot as plt
import socket

def packetParse(dir, pcapname):
    #gets local IP to use when counting appearence of IPs
    h_name = socket.gethostname()
    myIP = socket.gethostbyname(h_name)

    #Opens the file and reads it in using the dpkt pcap reader
    f = open(pcapname, 'rb')
    pcap = dpkt.pcap.Reader(f)

    #dictionary to keep track of which ack numbers have appeared
    acks = {}

    #dictionary to keep track of the percentage of duplicate acks
    #per second to be put into a dataframe
    ackarr = {}

    #dictionary to keep track of sequence numbers that have appeared
    #only counts packets with a payload to track retransmissions
    retrans = {}

    #dictionary to keep track of persentage of retransmissions per
    #second
    retransarr = {}

    #dictionary to keep track of which ips appear when finding
    #the ip that the speedtest is using to run the test
    ips = {}

    #counts number of packets that have been parsed
    count = 1

    #bool used to get initial timestamp
    first = True
    #bool used to put the tester into a mode to find the IP
    #at the beginning, is made false after first 150 packets
    findIp = True

    #used to count time between graph points
    time0 = 0
    #is set to the initial time
    startime = 0
    #time between graph points, counts dup acks/window in seconds
    window = 1
    #tracks the ip that appears the most when finding the speedtest ip
    max = 0
    #used to store the speedtest ip
    testip = ''

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

        #finds time since last graph point, increases packet count
        vectime = timestamp - time0
        count += 1
        
        #uses first 150 packets to find the speedtest's ip
        if findIp:
            #tracks the appearence of source ips
            if dat.src in ips:
                ips[dat.src] += 1
            else:
                ips[dat.src] = 1
            
            #tracks the appearence of destination ips
            if dat.dst in ips:
                ips[dat.dst] += 1
            else:
                ips[dat.dst] = 1
            
            #stops counting ip appearence after 150 packets
            #then finds which ip appears the most and isn't the 
            #current device's ip
            if count > 150:
                findIp = False
                for ip in ips:  
                    if ips[ip] > max and socket.inet_ntoa(ip) != myIP:
                        max = ips[ip]
                        testip = ip
            continue


        #only counts packets sent to or from speedtest 
        #if the packet is coming from or going to the speedtest,
        #parse and check for a dup ack, else skip the packet 
        if dat.dst != testip and dat.src != testip:
            continue

        #parses ack flag to make sure the ack number is valid
        #skips packet if it is not 
        flags = dat.tcp.flags
        aflag = flags >> 4
        if aflag % 2 == 0: 
            continue

        #continues if FIN ack flag is set because it will
        #always register as a dup ack even though it isn't
        if flags % 2 == 1:
            continue
        



        #gets ack and sequence number and payload
        #packet will now be added to the data
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
        

        #checks if packet is within time window, if it isn't it will add
        #the data for that window to the final dictionaries
        if vectime > window:
            #goes through dictionary to find dup acks in the time frame
            ackcount = 0
            for key in acks:
                if acks[key] > 1:
                    ackcount += acks[key]
            
            #resets acks dictionary
            acks = {}
            
            #gets number of retransmits in the time frame
            seqcount = 0
            for key in retrans:
                if retrans[key] > 1:
                    seqcount += retrans[key]

            #resets retransmition dictionary
            retrans = {}

            #gets the time since start time to use on the graph
            currtime = timestamp - startime
            ackarr[int(currtime)] = float(ackcount) /count
            retransarr[int(currtime)] = float(seqcount) /count

            #resets time since graph point and packet count
            time0 = timestamp
            count = 0


    #splits ackarr into times and data, which can be more easily graphed
    ackdatarr = []
    times = []
    for i in range(1,int(currtime)):
        if i in ackarr:
            if ackarr[i] != 0:
                ackdatarr.append(ackarr[i])
                times.append(i)

    #formats and graphs the data into times and data then prints graph
    #saves the dataframe as a json file that can be read in to recreate the graph
    #in a different program
    d = {'time':times, 'dup ack %':ackdatarr}
    df = pd.DataFrame(d)

    df.plot(x='time', y = 'dup ack %', kind='scatter')
    plt.title('dup ack percentage')
    plt.show()
    df.to_json(path_or_buf=(dir+'\\dupAcks.json'))
    f.close()
