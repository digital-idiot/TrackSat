from datetime import datetime, timedelta
from lib.TLE_Parser import TwoLineElement
from lib.TLE_Parser import InvalidArgumentError
from orbit_predictor.sources import MemoryTLESource
import pytz


class Satellite:

    def __init__(self, tle, verbose=False):
        if isinstance(tle, TwoLineElement):
            self.__tle_lines = tle.get_lines()
            self.__tle_dict = tle.get_tle_dict()
        elif isinstance(tle, str):
            try:
                tle_lines = (TwoLineElement(tle)).get_lines()
                tle_dict = (TwoLineElement(tle)).get_tle_dict()
            except ValueError as val_err:
                tle_lines = None
                tle_dict = None
                if verbose:
                    print(val_err)
            if tle_lines:
                self.__tle_lines = tle_lines
                self.__tle_dict = tle_dict
        else:
            raise InvalidArgumentError('Invalid Argument')

    def get_epoch_date(self):
        year = self.__tle_dict['EPOCH_YEAR']
        days = self.__tle_dict['EPOCH_DAY']
        epoch_date = datetime(year, 1, 1) + timedelta(days=(days - 1))
        return epoch_date

    def get_position(self, utc_datetime=datetime.utcnow()):
        source = MemoryTLESource()
        source.add_tle(sate_id=self.__tle_lines[0],
                       tle=(self.__tle_lines[1], self.__tle_lines[2]),
                       epoch=self.get_epoch_date()
                       )
        predictor = source.get_predictor(self.__tle_lines[0], precise=True)
        return predictor.get_position(utc_datetime).position_llh
