from scapy import *
import os
import sys

file_name = "cap1.pcap"

count = 0
for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
    count += 1

print('{} contains {} packets'.format(file_name, count))