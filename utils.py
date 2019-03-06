from django.conf import settings
import rest_framework.pagination as pagination
from cryptography.fernet import Fernet
from django.utils.crypto import get_random_string
import datetime
from decimal import *
from distutils.util import strtobool
from dateutil.parser import parse
import logging


logger = logging.getLogger(__name__)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def listfetchall(cursor):
    "Return all rows from a cursor as a list - used for queries that return only 1 field"
    return [row[0] for row in cursor.fetchall()]


# allow for later re-implementation with adjustable rounding
def currency_round(amount):
    return round(amount, 2)


def accounting_format(amount, currency_code=''):
    if currency_code != '':
        currency_code = currency_code + ' '
    if amount >= 0:
        return currency_code + '{:,.2f}'.format(amount).replace(",", " ")       # Hack to get past pythons inability
                                                                                # to format spaces into numbers?
    else:
        return currency_code + '({:,.2f})'.format(-amount).replace(",", " ")    # Hack to get past pythons inability to
                                                                                # format spaces into numbers?


# allow for later re-implementation with adjustable rounding
def quantity_round(amount,):
    return round(amount, 2)


class KendoUILimitOffSetPagination(pagination.LimitOffsetPagination):
    limit_query_param = 'take'
    offset_query_param = 'skip'
    max_limit = 100


def encrypt(input_value):
    if type(input_value) != bytes:
        input_value = bytes(input_value, 'UTF-8')

    key = getattr(settings, 'ENCRYPTION_KEY')
    f = Fernet(key)
    token = f.encrypt(input_value)
    return token.decode('UTF-8')


def decrypt(input_value):
    if type(input_value) != bytes:
        input_value = bytes(input_value, 'UTF-8')

    key = getattr(settings, 'ENCRYPTION_KEY')
    f = Fernet(key)
    token = f.decrypt(input_value)
    return token.decode('UTF-8')


def concat_fields(*args, **kwargs):
    result = ''
    for a in args:
        a = str(a)
        if a != 'nan' and a.strip != '':
            result = result + a + "\r\n"
    return result.strip()


def non_zero(amount, minval=0):
    if amount is not None and abs(round(amount, 2)) > minval:
        return True
    else:
        return False


def get_id_string():
    # TODO decide if this is a good enough solution
    return get_random_string(length=7, allowed_chars='ABCDEFGHIJKLMNPQRSTVWXYZ123456789')


def to_decimal(input_val, digits=2):
    if type(input_val) is Decimal:
        return input_val
    if input_val is None:
        return Decimal(0)
    elif type(input_val) == str:
        if len(input_val.strip()) > 0:
            return Decimal(input_val)
        else:
            return Decimal(0)
    elif type(input_val) == float or type(input_val) == int:
        return round(Decimal(input_val), 2)
    else:
        raise ValueError(f'''Could not convert {input_val} to decimal''')


def to_boolean(input_val, default=False):
    if type(input_val) == bool:
        return input_val
    elif type(input_val) == int:
        try:
            return bool(input_val)
        except ValueError:
            return default
    elif type(input_val) == str:
        input_val = input_val.strip()
        if len(input_val.strip()) > 0:
            return bool(strtobool(input_val))
        else:
            return default


def to_int(input_val, default=0):
    if type(input_val) == str:
        if len(input_val.strip()) > 0:
            try:
                tmp = int(input_val)
                return tmp
            except ValueError:
                return default
        else:
            return default
    elif type(input_val) == float or type(input_val) == int:
        return int(input_val)
    elif input_val is None:
        return default
    else:
        raise ValueError(f'''Could not convert {input_val} to integer''')


def to_date(input_val, default=None):
    if type(input_val) == datetime.datetime:
        return input_val.date()
    if type(input_val) == datetime.date:
        return input_val
    if type(input_val) == str:
        if len(input_val.strip()) > 7:
            return parse(input_val).date()
        else:
            return default
    elif type(input_val) == float or type(input_val) == int:
        return datetime.datetime.utcfromtimestamp(input_val).date()
    elif input_val is None:
        return default
    else:
        raise ValueError(f'''Could not convert {input_val} to date''')


def debug_sql():
    from django.db import connection
    import re
    for i, query in enumerate(connection.queries):
        sql = re.split(r'(SELECT|FROM|WHERE|GROUP BY|ORDER BY|INNER JOIN|LIMIT)', query['sql'])
        if not sql[0]: sql = sql[1:]
        sql = [(' ' if i % 2 else '') + x for i, x in enumerate(sql)]
        print('\n### {} ({} seconds)\n\n{};\n'.format(i, query['time'], '\n'.join(sql)))


def last_day_of_month(any_day):
    any_day = to_date(any_day)
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)
