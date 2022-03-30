import sys
import os
import subprocess


shellScript = '''
Add-Type -AssemblyName System.Device #Required to access System.Device.Location namespace
$GeoWatcher = New-Object System.Device.Location.GeoCoordinateWatcher #Create the required object
$GeoWatcher.Start() #Begin resolving current locaton

while (($GeoWatcher.Status -ne 'Ready') -and ($GeoWatcher.Permission -ne 'Denied')) {
    Start-Sleep -Milliseconds 100 #Wait for discovery.
}  

if ($GeoWatcher.Permission -eq 'Denied'){
    Write-Error 'Access Denied for Location Information'
} else {
    $GeoWatcher.Position.Location | Select Latitude,Longitude #Select the relevent results.
}
'''



#os.system('netsh wlan show interfaces >> interface.txt')
#fp = open('interface.txt')
results = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode()

output = results.split('\n')
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
    
for key in data:
    print(f'{key}:', data[key])

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
    if line[:5] == 'BSSID':
        bid = line.split(':')
        bid = ':'.join(bid[1:]).strip()
        ssids[currid][bid] = {} #dictionary of attributes for each BSSID
        processbid = True
        continue
    if not processbid:
        continue
    if line[:6] == 'Signal':
        signal = line.split(':')[1].strip()[:-1]
        signal = int(signal)
        rssi = (signal/2) - 100
        ssids[currid][bid]['RSSI'] = rssi
    if line[:4] == 'Band':
        band = line.split(':')[1].strip()
        ssids[currid][bid]['Band'] = band
        
    

print(ssids)

if len(sys.argv) != 2:
    print('Enter directory name')
    quit(1)
path = os.getcwd()
if not os.path.exists(path + sys.argv[1]):
    os.makedirs(path + sys.argv[1])


results = subprocess.check_output(['C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe','C:\\Users\\riley\\Coding\\NetworkResearchSP2022\\coords.ps1'],).decode()

output = results.split('\n')
for thing in output:
    if int(thing[0]):
        print(1)
print(output)


#fp.close()
#os.remove('interface.txt')
    