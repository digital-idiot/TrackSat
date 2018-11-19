import urllib.request
import sys
import os
import lib.TLE_Parser as tp
from pathlib import Path

master_url = "https://www.celestrak.com/NORAD/elements/"

file_names = [
    "visual",
    "active",
    "amateur",
    "analyst",
    "argos",
    "beidou",
    "2012-044",
    "cosmos-2251-debris",
    "cubesat",
    "dmc",
    "resource",
    "education",
    "engineering",
    "x-comm",
    "1999-025",
    "galileo",
    "geodetic",
    "geo",
    "globalstar",
    "glo-ops",
    "goes",
    "gorizont",
    "gps-ops",
    "intelsat",
    "iridium",
    "iridium-33-debris",
    "iridium-NEXT",
    "tle-new",
    "military",
    "molniya",
    "nnss",
    "noaa",
    "orbcomm",
    "other",
    "other-comm",
    "planet",
    "radar",
    "raduga",
    "musson",
    "sbas",
    "sarsat",
    "ses",
    "science",
    "stations",
    "spire",
    "tdrss",
    "weather"
]

tle_dump = None
for f in file_names:
    fname = f + ".txt"
    url = master_url + fname
    base_path = os.getcwd()
    out_file = base_path + "/data/" + fname
    path = Path(out_file)
    if not path.is_file():
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            text = data.decode('utf-8')
            with open(out_file, "w+") as fl:
                fl.write(text)
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Line No: ", exc_tb.tb_lineno, "\nError: ", exc)
            print(url)

    try:
        tle_obj = tp.TwoLineElements.from_file(file_path=out_file, celestrak=True, ignore=False, verbose=True)
    except Exception:
        continue
    if tle_dump is None:
        tle_dump = tle_obj
    else:
        tle_dump = tle_dump + tle_obj

tle_dump.gen_db()
