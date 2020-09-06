import os
import re
from collections import namedtuple
from datetime import date

from flask import Flask, request, make_response

BASE_DIR = os.path.dirname(__file__)
app = Flask(__name__)
Region = namedtuple('Region', field_names=('revision', 'code', 'name'))


class InvalidIdCard(ValueError):
    pass


class BirthdayInvalid(InvalidIdCard):
    pass


def load_regions():
    _regions_path = f'{BASE_DIR}/data'
    _region_files = os.listdir(_regions_path)
    _region_files.sort()
    _regions = {}
    for file in _region_files:
        with open(f'{_regions_path}/{file}') as f:
            for line in f.readlines()[1:]:
                region = Region(*line.strip().split(','))
                _regions[region.code] = region
    return _regions


class IDCard(object):
    _check_rules = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    _check_codes = '10X98765432'
    _regions = load_regions()

    def __init__(self, identity):
        if re.match(r'^[0-9]{15}$', identity) is not None:
            identity = f'{identity[:6]}19{identity[6:]}'
            check_code = self._check_identity(identity)
            self.identity = f'{identity}{check_code}'
        elif re.match(r'^[0-9]{17}.$', identity) is not None:
            self.identity = identity
        else:
            raise InvalidIdCard

    @classmethod
    def _check_identity(cls, identity):
        _sum = sum([int(identity[index]) * rule for index, rule in enumerate(cls._check_rules)])
        return cls._check_codes[_sum % 11]

    def json(self):
        result = {
            'id': self.identity,
            'birthday': self.birthday,
            'gender': self.gender,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'region_code': self.identity[:6],
        }
        if self.identity[-1] != self.check_code:
            result['id2'] = f'{self.identity[:-1]}{self.check_code}'
        return result

    @property
    def birthday(self):
        try:
            year, month, day = self.identity[6:10], self.identity[10:12], self.identity[12:14]
            return date(int(year), int(month), int(day)).strftime('%Y/%m/%d')
        except ValueError as e:
            raise BirthdayInvalid from e

    @property
    def gender(self):
        return 'F' if int(self.identity[-2]) % 2 == 0 else 'M'

    @property
    def region_code(self):
        return self.identity[:6]

    @property
    def province(self):
        region = self._regions.get(f'{self.region_code[:2]}0000')
        return region.name if region is not None else ''

    @property
    def city(self):
        region = self._regions.get(f'{self.region_code[:4]}00')
        return region.name if region is not None else ''

    @property
    def district(self):
        region = self._regions.get(self.region_code)
        return region.name if region is not None else ''

    @property
    def check_code(self):
        return self._check_identity(self.identity)


@app.route('/search', methods=['GET'])
def search():
    identity = request.args.get('id', '')
    try:
        return IDCard(identity).json()
    except BirthdayInvalid:
        return make_response({
            'message': '',
            'errors': [{'field': 'birthday', 'code': 'invalid'}]
        }, 422)
    except InvalidIdCard:
        return make_response({
            'message': '',
            'errors': [{'field': 'id', 'code': 'missing_field' if identity == '' else 'invalid'}]
        }, 422)
