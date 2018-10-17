"""
Cached does what it says on the tin.
"""
import requests
import json
import pytz
from .requestors import get


def get_timezone(auth, base_url):
    """
    Gets the account information which includes the timezone, and returns this timezone as a pytz.timezone object.
    """
    r = requests.get(url=base_url + 'account.json', auth=auth)
    if r.status_code is not 200:
        raise requests.exceptions.HTTPError('Invalid Authentication')
    data = json.loads(r.content.decode('utf-8'))
    return pytz.timezone(data['time_zone'])


def get_locations(auth, base_url):
    """
    Gets the locations on a Staffomatic account and returns a dictionary with the location names as the keys and the
    location id numbers as the values.
    """
    details = get(auth=auth, url=base_url + 'locations.json')
    keys, values = [], []
    for i in range(len(details)):
        keys += [details[i]['name']]
        values += [details[i]['id']]
    return dict(zip(keys, values))


def get_departments(auth, base_url):
    """
    Gets the departments on a Staffomatic account and returns a dictionary of dictionaries withh the location names
    as the keys and the department names as the keys within, with the department ids as the values.
    """
    locations = get_locations(auth, base_url)
    departments = {}
    for key, value in locations.items():
        details = get(auth, base_url + 'locations/{loc_id}/departments.json'.format(loc_id=value))
        keys, values = [], []
        for i in range(len(details)):
            keys += [details[i]['name']]
            values += [details[i]['id']]
        loc_departments = dict(zip(keys, values))
        departments.update({key: loc_departments})
    return departments
