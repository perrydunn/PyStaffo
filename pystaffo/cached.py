import pytz
from .requestors import get


def get_timezone(auth, base_url):
    """
    Gets the account information which includes the timezone, and returns this timezone as a pytz.timezone object.
    :param auth:
    :param base_url:
    :return:
    """
    data = get(auth=auth, url=base_url + 'account.json')
    return pytz.timezone(data['time_zone'])


def get_locations(auth, base_url):
    """
    Gets the locations from Staffomatic and returns a dictionary with the location names as the keys and the
    location id numbers as the values.
    :param auth:
    :param base_url:
    :return:
    """
    details = get(auth=auth, url=base_url + 'locations.json')
    keys, values = [], []
    for i in range(len(details)):
        keys += [details[i]['name']]
        values += [details[i]['id']]
    return dict(zip(keys, values))


def get_departments(auth, base_url):
    """
    Gets the departments from Staffomatic for a location specified by name and returns a dictionary with the
    department names as the keys and the department id numbers as the values.
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
