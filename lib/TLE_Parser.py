import re
import magic
# import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.request import pathname2url
import ntpath


class InvalidArgumentError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LengthError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ChecksumError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class IntegrityError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FileTypeError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FatalError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TwoLineElement:

    schema = {
        'SATELLITE_NAME': (str, 'NOT NULL'), 'SATELLITE_NUMBER': (int, 'PRIMARY KEY'),
        'CLASSIFICATION': (str, 'NOT NULL'), 'LAUNCH_YEAR': (int, 'NOT NULL'), 'LAUNCH_NUMBER': (int, 'NOT NULL'),
        'PIECE_OF_LAUNCH': (str, 'NOT NULL'), 'EPOCH_YEAR': (int, 'NOT NULL'), 'EPOCH_DAY': (float, 'NOT NULL'),
        'FIRST_TIME_DERIVATIVE': (float, 'NOT NULL'), 'SECOND_TIME_DERIVATIVE': (float, 'NOT NULL'),
        'BSTAR_DRAG': (float, 'NOT NULL'), 'EPHEMERIS_TYPE': (int, 'NOT NULL'), 'ELEMENT_SET_NUMBER': (int, 'NOT NULL'),
        'INCLINATION': (float, 'NOT NULL'), 'RIGHT_ASCENSION': (float, 'NOT NULL'), 'ECCENTRICITY': (float, 'NOT NULL'),
        'ARGUMENT_OF_PERIGEE': (float, 'NOT NULL'), 'MEAN_ANOMALY': (float, 'NOT NULL'),
        'MEAN_MOTION': (float, 'NOT NULL'), 'REVOLUTION_AT_EPOCH': (int, 'NOT NULL'), 'STATUS': (str,),
        'CELESTRAK_CLASS': (str,), 'RAW_TLE': (str, 'NOT NULL')
    }

    type_map = {
        str: 'TEXT', int: 'INTEGER', float: 'REAL'
    }

    status_map = {
        '[+]': 'Operational',
        '[-]': 'Non-operational',
        '[P]': 'Partially Operational',
        '[B]': 'Standby',
        '[S]': 'Spare',
        '[X]': 'Extended Mission'
    }

    @staticmethod
    def valid_tle_line(tle_line, verbose=False):
        if not isinstance(verbose, bool):
            verbose = False
        try:
            if isinstance(tle_line, str):
                if len(tle_line) == 69:
                    return not bool(re.compile(r'[^a-zA-Z0-9.+\- ]').search(tle_line))
                else:
                    raise LengthError(r"Length Mismatch")
            else:
                raise InvalidArgumentError(r"Expected 'tle_line' to be of <str> type")
        except LengthError as length_error:
            if verbose:
                print(length_error)
            return False
        except InvalidArgumentError as arg_error:
            if verbose:
                print(arg_error)
            return False

    @staticmethod
    def verify_line_checksum(line, verbose=False):
        if not isinstance(verbose, bool):
            verbose = False
        try:
            if TwoLineElement.valid_tle_line(line):
                clean_line = line[:-1].strip()
                check_sum = 0
                for c in clean_line:
                    if c == '-':
                        check_sum = check_sum + 1
                    elif c.isdigit():
                        check_sum = check_sum + int(c)
                check_sum %= 10
                if str(check_sum) == line[-1]:
                    return True
                else:
                    return False
            else:
                raise InvalidArgumentError("Not a valid TLE line")
        except InvalidArgumentError as arg_err:
            if verbose:
                print(arg_err)
            return None

    def get_lines(self):
        out = [self.__tle_line0, self.__tle_line1, self.__tle_line2]
        if all(element is not None for element in out):
            return out
        else:
            return None

    @staticmethod
    def parse_title(title, verbose=True):
        try:
            if title and isinstance(title, str):
                status_pattern = re.compile(r"\[[PBSX+\-]\]")
                match = status_pattern.search(title)
                span = None
                if match:
                    span = match.span()
                if span:
                    name = (title[:span[0]]).strip()
                    status = TwoLineElement.status_map[title[span[0]:span[1]]]
                    return name, status
                else:
                    name = title.strip()
                    status = str()
                    return name, status
            else:
                raise ValueError("Expected not 'None' <str> as argument")
        except ValueError as val_err:
            if verbose:
                print(val_err)
            return None

    @staticmethod
    def parse_tle(tle_string, verbose=True):
        try:
            tle_dict = dict()
            if isinstance(tle_string, str):
                tle_lines = (tle_string.strip()).split('\n')
                if len(tle_lines) == 3:
                    if (len(tle_lines[0]) <= 24) and (len(tle_lines[1]) == 69) and (len(tle_lines[2]) == 69):
                        title = tle_lines[0]
                        name_status = TwoLineElement.parse_title(title)
                        if name_status:
                            tle_dict['SATELLITE_NAME'] = name_status[0]
                            tle_dict['STATUS'] = name_status[1]
                        else:
                            raise IntegrityError("parse_tle: Invalid TLE title")
                        if tle_lines[1][0] == '1':
                            if TwoLineElement.verify_line_checksum(tle_lines[1]):
                                try:
                                    tle_dict['SATELLITE_NUMBER'] = int(tle_lines[1][2:7])
                                    tle_dict['CLASSIFICATION'] = tle_lines[1][7]
                                    if int(tle_lines[1][9:11]) < 57:
                                        tle_dict['LAUNCH_YEAR'] = int('20' + tle_lines[1][9:11])
                                    else:
                                        tle_dict['LAUNCH_YEAR'] = int('19' + tle_lines[1][9:11])
                                    tle_dict['LAUNCH_NUMBER'] = int(tle_lines[1][11:14])
                                    tle_dict['PIECE_OF_LAUNCH'] = (tle_lines[1][14:17]).strip()
                                    if int(tle_lines[1][18:20]) < 57:
                                        tle_dict['EPOCH_YEAR'] = int('20' + tle_lines[1][18:20])
                                    else:
                                        tle_dict['EPOCH_YEAR'] = int('19' + tle_lines[1][18:20])
                                    tle_dict['EPOCH_DAY'] = float(tle_lines[1][20:32])
                                    tle_dict['FIRST_TIME_DERIVATIVE'] = 2.0 * float(tle_lines[1][33:43])
                                    std = (tle_lines[1][44:52]).strip()
                                    if not bool(re.compile(r'[^0-9+\-]').search(std)):
                                        index = 0
                                        for i in reversed(range(len(std))):
                                            if std[i] == '-' or std[i] == '+':
                                                index = i
                                                break
                                        if (std[0]).isdigit():
                                            tle_dict['SECOND_TIME_DERIVATIVE'] = 6.0 * float(
                                                '0.' + std[0:index] + 'E' + std[index:]
                                            )
                                        else:
                                            tle_dict['SECOND_TIME_DERIVATIVE'] = 6.0 * float(
                                                std[0] + '0.' + std[1:index] + 'E' + std[index:]
                                            )
                                    drag = (tle_lines[1][53:61]).strip()
                                    if not bool(re.compile(r'[^0-9+\-]').search(drag)):
                                        index = 0
                                        for i in reversed(range(len(drag))):
                                            if drag[i] == '-' or drag[i] == '+':
                                                index = i
                                                break
                                        if (drag[0]).isdigit():
                                            tle_dict['BSTAR_DRAG'] = float(
                                                '0.' + drag[0:index] + 'E' + drag[index:]
                                            )
                                        else:
                                            tle_dict['BSTAR_DRAG'] = float(
                                                drag[0] + '0.' + drag[1:index] + 'E' + drag[index:]
                                            )
                                    else:
                                        raise IntegrityError('Possible Corruption of TLE Data')
                                    tle_dict['EPHEMERIS_TYPE'] = int(tle_lines[1][62])
                                    tle_dict['ELEMENT_SET_NUMBER'] = int(tle_lines[1][64:68])
                                    tle_dict['RAW_TLE'] = tle_string.strip()
                                except ValueError as val_err:
                                    if verbose:
                                        print(val_err, "\nparse_tle: Invalid TLE Data")
                                    return None
                            else:
                                raise ChecksumError("parse_tle: Checksum Mismatch")
                        if tle_lines[2][0] == '2':
                            if TwoLineElement.verify_line_checksum(tle_lines[2]):
                                if tle_lines[2][2:7] == tle_lines[1][2:7]:
                                    try:
                                        tle_dict['INCLINATION'] = float(tle_lines[2][8:16])
                                        tle_dict['RIGHT_ASCENSION'] = float(tle_lines[2][17:25])
                                        tle_dict['ECCENTRICITY'] = float("0." + tle_lines[2][26:33])
                                        tle_dict['ARGUMENT_OF_PERIGEE'] = float(tle_lines[2][34:42])
                                        tle_dict['MEAN_ANOMALY'] = float(tle_lines[2][43:51])
                                        tle_dict['MEAN_MOTION'] = float(tle_lines[2][52:63])
                                        tle_dict['REVOLUTION_AT_EPOCH'] = int(tle_lines[2][63:68])
                                    except ValueError:
                                        if verbose:
                                            print("parse_tle: Invalid TLE Data")
                                        return None
                                else:
                                    raise IntegrityError("parse_tle: Possibly Corrupted / Wrong Satellite ID")
                            else:
                                raise ChecksumError("parse_tle: Checksum Mismatch")
                        else:
                            raise IntegrityError("parse_tle: Invalid Line Number")
                    else:
                        raise LengthError("parse_tle: Invalid Line Length")
                else:
                    raise IntegrityError("parse_tle: Invalid or Corrupted TLE Data")
            else:
                raise InvalidArgumentError("parse_tle: Expected 'tle_string' as <str>")
            return tle_dict
        except ChecksumError as checksum_err:
            if verbose:
                print(checksum_err)
            return None
        except IntegrityError as integrity_err:
            if verbose:
                print(integrity_err)
            return None
        except LengthError as length_err:
            if verbose:
                print(length_err)
            return None
        except InvalidArgumentError as arg_err:
            if verbose:
                print(arg_err)
            return None

    def __init__(self, input_string, verbose=False):
        self.__tle_line0 = None
        self.__tle_line1 = None
        self.__tle_line2 = None
        self.__tle_dict = None
        if isinstance(input_string, str):
            tle_dict = TwoLineElement.parse_tle(input_string, verbose=verbose)
            lines = (input_string.strip()).split('\n')
            self.__tle_line0, _ = TwoLineElement.parse_title(lines[0])
            self.__tle_line1 = lines[1]
            self.__tle_line2 = lines[2]
            if tle_dict:
                self.__tle_data = tle_dict
            else:
                raise ValueError("Invalid <input_string>")
        else:
            raise InvalidArgumentError("expected <str> as argument")

    def get_international_designator(self):
        launch_number = str(self.__tle_data['LAUNCH_NUMBER'])
        while len(launch_number) < 3:
            launch_number = "0" + launch_number
        return str(self.__tle_data['LAUNCH_YEAR']) + '-' + launch_number + str(self.__tle_data['PIECE_OF_LAUNCH'])

    def get_tle_dict(self):
        return self.__tle_data


class TwoLineElements:
    @staticmethod
    def parse_tle_file(tle_file_path, ignore=False, verbose=True):
        tle_collection = list()
        tle_list = list()
        flag = False
        try:
            if magic.from_file(tle_file_path, mime=True) == 'text/plain':
                with open(tle_file_path, 'rU') as file:
                    for line in file:
                        tle_list.append(line)
                        if len(tle_list) == 3:
                            tle = ''.join(tle_list)
                            tle_data = TwoLineElement.parse_tle(tle)
                            if tle_data:
                                tle_collection.append(tle_data)
                            else:
                                flag = True
                                if not ignore:
                                    raise ParseError("parse_tle_file: Could not Parse a TLE block:\n" + tle + "\n")
                            tle_list = list()
                return flag, tle_collection
            else:
                raise FileTypeError("parse_tle_file: Expected <text/plain> file")
        except ParseError as parse_err:
            if verbose:
                print(parse_err)
            return tle_collection
        except FileTypeError as file_type_err:
            if verbose:
                print(file_type_err)
            return None
        except FileNotFoundError as file_err:
            if verbose:
                print(file_err)
            return None
        except OSError as os_err:
            if verbose:
                print("parse_tle_file: Invalid File Path", " {", os_err, "}")
            return None

    @classmethod
    def from_file(cls, file_path=None, celestrak=True, ignore=False, verbose=False):
        celestrak_class = str()
        if file_path:
            try:
                parsed_tle = TwoLineElements.parse_tle_file(file_path, ignore=ignore, verbose=verbose)
                if celestrak:
                    ext_pattern = re.compile(r"\.\w+$")
                    file_name = (ntpath.basename(file_path)).strip()
                    match = ext_pattern.search(file_name)
                    if match:
                        celestrak_class = (file_name[:(match.span())[0]]).upper()
            except ValueError as val_err:
                parsed_tle = None
                if verbose:
                    print(val_err)
            if parsed_tle:
                for tle in parsed_tle[1]:
                    tle['CELESTRAK_CLASS'] = celestrak_class
                return TwoLineElements(parsed_tle[1])
            else:
                raise ValueError('Invalid TLE File: Parsing of TLE File Failed')
        else:
            return TwoLineElements(list())

    def get_all(self):
        return self.__tle_dump

    def count(self):
        return len(self.__tle_dump)

    @staticmethod
    def check_sanity(list_arg, verbose=False):
        try:
            if isinstance(list_arg, list):
                if all(isinstance(tle_dict, dict) for tle_dict in list_arg):
                    return all(all(isinstance(tle_dict[key], (TwoLineElement.schema[key])[0])
                                   for key in tle_dict.keys()) for tle_dict in list_arg)
                else:
                    raise IntegrityError('Expected all elements to be of <dict> type')
            else:
                raise InvalidArgumentError('Expected argument to be of <list> type')
        except IntegrityError as integrity_err:
            if verbose:
                print(integrity_err)
            return False
        except InvalidArgumentError as arg_err:
            if verbose:
                print(arg_err)
            return False

    def __init__(self, tle_list, verbose=False):
        if not isinstance(verbose, bool):
            verbose = False
        if TwoLineElements.check_sanity(tle_list, verbose=verbose):
            self.__tle_dump = tle_list
        else:
            raise InvalidArgumentError("TwoLineElements: Illegal Argument")

    def __add__(self, other):
        try:
            if isinstance(other, TwoLineElement):
                return TwoLineElements(self.__tle_dump + [other])
            elif isinstance(other, TwoLineElements):
                return TwoLineElements(self.__tle_dump + other.get_all())
            else:
                raise InvalidArgumentError("add: Expected <TwoLineElement / TwoLineElements> as argument")
        except InvalidArgumentError:
            return None

    @staticmethod
    def make_schema():
        schema = TwoLineElement.schema
        sql_str = '( '
        for key in schema.keys():
            if len(schema[key]) == 2:
                constraint = ' ' + (schema[key])[1] + ', '
            else:
                constraint = ', '
            sql_str += key + ' ' + TwoLineElement.type_map[(schema[key])[0]] + constraint
        sql_str = sql_str[:-2] + ' );'
        return sql_str

    def gen_db(self, db_path='data/Sat_Repo.db', table_name='Sat_Info', verbose=True):
        try:
            if isinstance(db_path, str):
                try:
                    # db_uri = (db_path + '?mode=rw').format(pathname2url(db_path))
                    # conn = psycopg2.connect(db_uri)
                    conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="postgres")
                except psycopg2.OperationalError:
                    if verbose:
                        print("Database does not exist")
                    conn = psycopg2.connect(db_path)
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                conn.autocommit = True
                with conn:
                    db_pointer = conn.cursor()
                    create_sql = 'CREATE TABLE IF NOT EXISTS ' + table_name + ' ' + TwoLineElements.make_schema()
                    db_pointer.execute(create_sql)
                    for tle_dict in self.__tle_dump:
                        insert_query = 'INSERT INTO public.' + table_name
                        attributes = list(tle_dict.keys())
                        insert_query += ' ('
                        values_string = list()
                        for attr in attributes:
                            insert_query += str(attr) + ', '
                            value = tle_dict[attr]
                            if value == str():
                                value = None
                            values_string.append(value)
                        insert_query = insert_query[:-2] + ' ) VALUES (' + '%s, '*len(attributes)
                        insert_query = insert_query[:-2] + ' );'
                        try:
                            db_pointer.execute(insert_query, values_string)
                        except psycopg2.Error as perr:
                            if verbose:
                                # print('Warning: Record Insertion Failed\n', 'Record Values: ', values_string, '\n')
                                print(perr)
                conn.close()
            else:
                raise InvalidArgumentError("gen_db: Expected <str> as argument")
        except InvalidArgumentError as arg_err:
            if verbose:
                print(arg_err)
            return None
        except psycopg2.OperationalError as sqlite_err:
            if verbose:
                print(sqlite_err)
            return None
