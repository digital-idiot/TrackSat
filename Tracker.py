from lib.TLE_Parser import TwoLineElement
from lib import Satellite
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

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
            print(position)
            plt.scatter(position[0], position[1], transform=ccrs.Geodetic(), )
            plt.pause(delay)


s = '''ISS (ZARYA)             
1 25544U 98067A   18106.24140593  .00002088  00000-0  38575-4 0  9994
2 25544  51.6428 327.5253 0001918 355.0324 161.2063 15.54266407108880'''
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

tim = datetime.utcnow()
for i in range(10000):
    pos = msat.get_position(tim)
    plt.plot(pos[1], pos[0], 'ro', transform=ccrs.Geodetic())
    tim += timedelta(seconds=1)
    #plt.pause(1)
    fig.canvas.draw()
#plt.show()


