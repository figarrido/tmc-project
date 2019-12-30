from datetime import datetime, date

from .exceptions import TMCError

def query_param_required_error(param):
    raise TMCError(f'Query parameter `{param}` is required')

def parse_amount(raw_amount):
    if not raw_amount:
        query_param_required_error('amount')

    try:
        amount = float(raw_amount)
    except ValueError as e:
        raise TMCError(
            'Query parameter `amount` has to be a decimal ' +
            'separated by dots (ex: 1.54)'
        )

    if amount < 0:
        raise TMCError(
            'Query parameter `amount` has to be a positive value'
        )

    return amount

def parse_days(raw_days):
    if not raw_days:
        return query_param_required_error('days')

    if not raw_days.isdigit():
        raise TMCError(
            'Query parameter `days` has to be ' +
            'a positive integer (ex: 54)'
        )

    days = int(raw_days)
    return days

def parse_date(raw_date):
    if not raw_date:
        return query_param_required_error('date')

    try:
        query_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
    except ValueError:
        raise TMCError(
            'Query parameter `date` has ' +
            'to have format yyyy-mm-dd (ex: 2019-10-23)'
        )

    return query_date
