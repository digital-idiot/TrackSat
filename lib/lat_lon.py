import matplotlib.pyplot as plt

import cartopy.crs as ccrs

import pandas as pd

from orbit_predictor.sources import EtcTLESource
from orbit_predictor.predictors import TLEPredictor

source = EtcTLESource(filename=r'e:/resource.txt')
#source = EtcTLESource(filename=r'd:/visual.txt')
predictor = TLEPredictor("WORLDVIEW-2 (WV-2)      ", source)
#predictor = TLEPredictor('ATLAS CENTAUR 2         ', source)

dates = pd.date_range(start="2018-04-01 00:00", periods=1000, freq="30S")

latlon = pd.DataFrame(index=dates, columns=["lat", "lon"])

for date in dates:
    lat, lon, _ = predictor.get_position(date).position_llh
    latlon.loc[date] = (lat, lon)

latlon.plot()

plt.figure(figsize=(15, 25))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.stock_img()

plt.plot(latlon["lon"], latlon["lat"], 'red', transform=ccrs.Geodetic(), linestyle=":", )
plt.show()

