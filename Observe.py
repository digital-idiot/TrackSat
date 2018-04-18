import sqlite3
import math
from skyfield.api import EarthSatellite, Topos, load
import pandas
from matplotlib import pyplot


class ObserverLocation:
    def __init__(self, lat='30.34817 N', lon='78.047752 E', temp_c=0.0, press_mbar=1013.25, verbose=False):
        try:
            if (not isinstance(lat, str)) or not (isinstance(lon, str)):
                raise ValueError("Expected <str>, <str> as 'lat', 'lon'")
        except ValueError as val_err:
            if verbose:
                print(val_err)
            lat, lon = '30.34817 N', '78.047752 E'
        try:
            if not isinstance(temp_c, float):
                raise ValueError("Expected 'temp_c' as <float>")
        except ValueError as val1_err:
            if verbose:
                print(val1_err)
            temp_c = 0.0
        try:
            if not isinstance(press_mbar, float):
                raise ValueError("Expected 'press_mbar' as <float>")
        except ValueError as val2_err:
            if verbose:
                print(val2_err)
            press_mbar = 1013.25
        self.__lat, self.__lon = lat, lon
        self.__temperature = temp_c
        self.__pressure = press_mbar

    def location(self):
        return self.__lat, self.__lon

    def temperature(self):
        return self.__temperature

    def pressure(self):
        return self.__pressure


class Observe:

    def __init__(self, db_path='Sat_Repo.db', table_name='Sat_Info', tle_attr='RAW_TLE',
                 observer_location=ObserverLocation(), condition=None, verbose=False):
        '''
        try:
            db_uri = (db_path + '?mode=rw').format(pathname2url(db_path))
            conn = sqlite3.connect(db_uri)
        except sqlite3.OperationalError:
            if verbose:
                print("Database does not exist")
            conn = None
        '''
        conn = sqlite3.connect(db_path)
        if conn:
            with conn:
                db_pointer = conn.cursor()
                if condition:
                    select_query = 'SELECT ' + tle_attr + ' FROM ' + table_name + ' WHERE ' + condition + ';'
                else:
                    select_query = 'SELECT ' + tle_attr + ' FROM ' + table_name + ';'
                db_pointer.execute(select_query)
                self.__tle_list = db_pointer.fetchall()
            try:
                if isinstance(observer_location, ObserverLocation):
                    self.__observer_location = observer_location
                else:
                    raise ValueError("Expected <ObserverLocation> as observer_location")
            except ValueError as val_err:
                if verbose:
                    print(val_err)
                self.__observer_location = ObserverLocation()

    @staticmethod
    def locate(tle, observer_location, time=load.timescale().now(), verbose=False):
        try:
            if isinstance(observer_location, ObserverLocation):
                line0, line1, line2 = tle[0].strip().split('\n')
                satellite = EarthSatellite(line1, line2, name=line0)
                location = satellite - Topos((observer_location.location())[0], (observer_location.location())[1])
                app = location.at(time)
                flag = True
                for val in app.position.km:
                    if math.isnan(val):
                        flag = False
                        break
                if flag:
                    temperature = observer_location.temperature()
                    pressure = observer_location.pressure()
                    return line0.strip() + " : " + line1[2:7], app.altaz(temperature_C=temperature, pressure_mbar=pressure)
            else:
                raise ValueError("Expected <ObserverLocation> as observer_location")
        except ValueError as val_err:
            if verbose:
                print(val_err)
            return None

    def observe_sky(self, verbose=False):
        color = ['r', 'g', 'b', 'y', 'm', 'k', 'tab:purple', 'tab:brown']
        observed = pandas.DataFrame(columns=['s', 'r', 't'])
        i = 0
        pyplot.tight_layout()
        ax = pyplot.subplot(111, projection='polar')
        ax.set_yticklabels([])
        ax.set_theta_zero_location("N")
        ax.set_rmax(1)
        ax.grid(True)
        #pyplot.title("Observable Satellites", va='top', ha='center')
        for tle in self.__tle_list:
            data = Observe.locate(tle, self.__observer_location, verbose=verbose)
            if data:
                sat = data[0]
                position = data[1]
                if position and position[0].degrees >= 0.0:
                    r = math.cos(position[0].degrees)
                    t = position[1].degrees
                    observed.loc[i] = sat, r, t
                    ax.plot(t, r, color[i % len(color)] + 'o', label=sat)
                    i += 1
        pyplot.legend(bbox_to_anchor=(1, 0), loc="lower right", bbox_transform=pyplot.gcf().transFigure)
        pyplot.show()


ob = Observe(verbose=True)
ob.observe_sky(verbose=True)
