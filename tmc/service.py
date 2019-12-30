import os
import requests
from dateutil.relativedelta import relativedelta

from .exceptions import TMCError, TMCWarning
from .helpers import parse_amount, parse_days, parse_date

BASE_URL = 'https://api.sbif.cl'
DAY_OF_CHANGE = 15
API_KEY = os.getenv('SBIF_API_KEY')
DEFAULT_TMC = 0

class TMC:
    def __init__(self, *, tmc):
        self.tmc = tmc

    @classmethod
    def get_tmc_from_api(cls, *, amount, days, query_date):
        parsed_amount = parse_amount(amount)
        parsed_days = parse_days(days)
        parsed_query_date = parse_date(query_date)

        period = cls.calc_period(parsed_query_date)
        tmcs = cls.get_tmcs(period)
        tmc_type = cls.get_tmc_type(parsed_amount, parsed_days)
        tmcs_selected = list(filter(lambda tmc: tmc['Tipo'] == tmc_type, tmcs))
        if not tmcs_selected:
            instance = cls(tmc=DEFAULT_TMC)
            raise TMCWarning(instance, 'Default TMC assigned')
        tmc = tmcs_selected[0]['Valor']
        return cls(tmc=tmc)

    @staticmethod
    def get_tmcs(period):
        params = {
            'apikey': API_KEY,
            'formato': 'json',
        }
        path = '/api-sbifv3/recursos_api/tmc/%d/%d' % period
        response = requests.get(BASE_URL + path, params=params)
        data = response.json()
        if data.get('TMCs', None) is None:
            if data.get('Mensaje') is None:
                raise TMCError('SBIF API Error')
            raise TMCError(data['Mensaje'])
        return data['TMCs']

    @staticmethod
    def calc_period(query_date):
        if query_date.day < DAY_OF_CHANGE:
            prev_date = query_date + relativedelta(months=-1)
            return prev_date.year, prev_date.month
        else:
            return query_date.year, query_date.month

    @staticmethod
    def get_tmc_type(amount, days):
        '''
        Según https://api.sbif.cl/documentacion/TMC.html y considerando
        los valores que entrega la API.

        Código 25 si: < 90 días & > 5000 UF
        Código 26 si: < 90 días & <= 5000 UF

        Código 45 si: >= 90 días & <= 50 UF
        Código 44 si: >= 90 días & <= 200 UF & > 50 UF
        Código 35 si: >= 90 días & > 200 UF & <= 5000 UF
        Código 34 si: >= 90 días & > 5000 UF

        Código 22 si: >= 1 año & > 2000 UF
        Código 24 si: >= 1 año & <= 2000 UF
        '''
        if days < 90:
            return '26' if amount <= 5000 else '25'
        elif days >= 365:
            return '24' if amount <= 2000 else '22'
        else:
            if amount <= 50:
                return '45'
            elif 50 < amount <= 200:
                return '44'
            elif 200 < amount <= 5000:
                return '35'
            else:
                return '34'
