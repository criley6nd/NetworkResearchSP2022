import staticmap
from staticmap.staticmap import CircleMarker
import pandas as pd
import matplotlib.pyplot as plt

def genMap(pts):
    m = staticmap.StaticMap(300, 400, 10)
        
    for point in pts:
        circle = CircleMarker((point[0][1], point[0][0]), point[1], 5)
        m.add_marker(circle)
    image = m.render()
    return image

printlist = []
lat = 0
lng = 0

df = pd.read_json('heat_map_data.json')
for item in df['coords']:
    printlist.append([item])
    lat+=item[0]
    lng+=item[1]
count = 0
for item in df['speed']:
    if item < 80:
        printlist[count].append('blue')
    else:
        printlist[count].append('red')
 
    count+=1


lat /= count
lng /= count
title = f'Speeds around campus'
image = genMap(printlist)
plt.imshow(image, extent=([lng-.25, lng+.25, lat-.25, lat+.25]))
plt.title(title)
plt.show()