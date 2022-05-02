import sys
import os
import subprocess
import json
from datetime import datetime

def getDeviceData(dt, dirname):   
    #os.system('netsh wlan show interfaces >> interface.txt')
    #fp = open('interface.txt')
    results = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode()

    output = results.split('\n')
    currConnection = {}
    data = {}

    for line in output:
        line = line.strip()
        key = line.split(':')
        key[0] = key[0].strip()
        if key[0] == 'BSSID':
            tempkey = key[1:]
            tempkey = ':'.join(tempkey)
            key = ['BSSID', tempkey]
        elif key[0] == 'Physical address':
            tempkey = key[1:]
            tempkey = ':'.join(tempkey)
            key = ['Physical address', tempkey.strip()]
        elif key[0] == 'Signal':
            signal = key[1][1:-1]
            signal = int(signal)
            rssi = (signal/2) - 100
            data['RSSI'] = rssi
            continue
        if len(key[0]):
            if len(key[1]):
                key[1] = key[1].strip()
                data[key[0]] = key[1]



    results = subprocess.check_output(['netsh', 'wlan', 'show', 'networks', 'mode=bssid']).decode()

    output = results.split('\n')

    linenum = 0
    currid = ''
    processbid = False
    ssids = {}
    for line in output:
        if line[:4] == 'SSID':
            currid = line.split(':')[1].strip()
            ssids[currid] = {} #dictionary of BSSIDs for each SSID
            processbid = False
            continue
        if not len(ssids):
            continue
        line = line.strip()
        if 'BSSID' in line:
            bid = line.split(':')
            bid = ':'.join(bid[1:]).strip()
            ssids[currid][bid] = {} #dictionary of attributes for each BSSID
            processbid = True
            continue
        if not processbid:
            continue
        if 'Signal' in line:
            signal = line.split(':')[1].strip()[:-1]
            signal = int(signal)
            rssi = (signal/2) - 100
            ssids[currid][bid]['RSSI'] = rssi
            ssids[currid][bid]['Signal'] = signal
        if 'Band'in line:
            band = line.split(':')[1].strip()
            ssids[currid][bid]['Band'] = band
        if 'Channel' in line and 'Utilization' not in line:
            channel = line.split(':')[1].strip()
            ssids[currid][bid]['Channel'] = channel
        elif 'Channel' in line:
            channel = line.split(':')[1].strip()
            ssids[currid][bid]['Utilization'] = channel


    currConnection = ssids[data['SSID']][data['BSSID']]
    currConnection['SSID'] = data['SSID']
    currConnection['BSSID'] = data['BSSID']
    currConnection['Receive rate (Mbps)'] = data['Receive rate (Mbps)']
    currConnection['Transmit rate (Mbps)'] = data['Transmit rate (Mbps)']         

    jsonDump = {'Current Connection': currConnection, 'All Connections': ssids}


    


    #gets coordinates
    results = subprocess.check_output(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe','C:\\Users\\riley\\Coding\\speedtests\\coords.ps1'],).decode()

    output = results.split('\n')
    for thing in output:
        if len(thing) > 0:
            if thing[0].isnumeric():
                latlng = thing.strip()
                lat, lng = latlng.split()

    jsonDump['coords'] = {'Lat': float(lat), 'Lng': float(lng)}
    print('Available connections:')
    heatCount = 0
    for key in jsonDump['All Connections']:
        count = 0
        for addr in ssids[key]:
            count += 1
            if key == currConnection['SSID']:
                heatCount+=1
        print(' ',key,' has ', count, ' physical addresses visable')
    
    print('\nYou are connected to ',currConnection['SSID'])
    print(' Physical address is ',currConnection['BSSID'])
    print(' Signal strength is ', currConnection['Signal'],'%\n')

    time = dt[1][:5]
    time = time.split(':')
    time = '_'.join(time)
    title = '\\' + time + '.json'
    with open(dirname+title, 'w') as f:
        f.write(json.dumps(jsonDump, sort_keys=False, indent=4))
    
    return heatCount, [float(lat), float(lng)]


