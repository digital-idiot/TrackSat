from lib.TLE_Parser import TwoLineElement
from lib import Satellite
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import random

class Tracker:
    def __init__(self, sat):
        if isinstance(sat, Satellite.Satellite):
            self.__satellite = sat
            self.__epoch = sat.get_epoch_date()
        else:
            raise ValueError("Expected <Satellite> as argument")

    def plot_position(self, utc_datetime=datetime.utcnow()):
        position = self.__satellite.get_position(utc_datetime)
        plt.figure(figsize=(15, 25))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        plt.plot(position[1], position[0], '-ro', transform=ccrs.Geodetic(), )
        plt.show()

    def show_footprint(self, delay=5):
        plt.figure(figsize=(15, 25))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        while True:
            position = self.__satellite.get_position()
            plt.scatter(position[0], position[1], transform=ccrs.Geodetic(), )
            plt.pause(delay)

s = '''GSAT-6A                 
1 43241U 18027A   18107.55692972 -.00000081  00000-0  00000+0 0  9993
2 43241   3.2778 292.6250 1382993 184.9815  78.9666  1.19301672   259'''

s = '''WORLDVIEW-2 (WV-2)      
1 35946U 09055A   18106.18982368 -.00000099  00000-0 -18378-4 0  9998
2 35946  98.4729 183.8200 0001770 165.0632 195.0663 14.37587360447041'''

s = '''ISS (ZARYA)             
1 25544U 98067A   18107.44763100  .00001858  00000-0  35119-4 0  9997
2 25544  51.6430 321.5086 0002048   0.7561  69.2289 15.54271367109073'''

xtle = TwoLineElement(s)
msat = Satellite.Satellite(xtle)
#t = Tracker(msat)
#t.plot_position()
#t.plot_position(datetime.strptime('May 22 2018  12:20AM', '%b %d %Y %I:%M%p'))
#t.show_footprint()


plt.figure(figsize=(15, 25))
plt.axes(projection=ccrs.PlateCarree()).stock_img()
fig = plt.gcf()
fig.show()
fig.canvas.draw()
flag = True
color = ['r','g','b','y','m']
i = 0
t = datetime.utcnow()
while flag:
    pos = msat.get_position(t)
    plt.plot(pos[1], pos[0], 'ro', transform=ccrs.Geodetic())
    t += timedelta(minutes=1)
    plt.pause(1)
    i = (i+1)%len(color)
    break
plt.show()


