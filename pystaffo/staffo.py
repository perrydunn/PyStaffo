import requests
import json
from datetime import datetime
import pytz

per_page = 300


def get_timezone(auth, url):
    """
    Gets the account information which includes the timezone, and returns this timezone as a pytz.timezone object.
    :param auth:
    :param url:
    :return:
    """
    url += 'account.json'
    r = requests.get(url=url, auth=auth, params={'page': 1, 'per_page': per_page})
    data = json.loads(r.content)
    return pytz.timezone(data['time_zone'])


class StaffoAccount:
    def __init__(self, subdomain, user, password):
        self.auth = (user, password)
        self.base_url = 'https://api.staffomaticapp.com/v3/{subdomain}/'.format(subdomain=subdomain)
        self.headers = {'Content-Type': 'application/json', }
        self.timezone = get_timezone(self.auth, self.base_url)

    def get(self, url, extras=None):
        params = {'page': 1, 'per_page': per_page}
        if extras:
            params.update(extras)
        r = requests.get(url=url, auth=self.auth, params=params)
        data = json.loads(r.content)
        try:
            pages = int(r.headers['Pages'])
            if pages > 1:
                for page in range(2, pages + 1):
                    params.update({'page': page})
                    r = requests.get(url=url, auth=self.auth, params=params)
                    data += json.loads(r.content)
        except KeyError:
            pass
        return data

    def locations(self):
        """
        Gets the locations from Staffomatic and returns a dictionary with the location names as the keys and the
        location id numbers as the values.
        :return:
        """
        details = self.get(self.base_url + 'locations.json')
        keys, values = [], []
        for i in range(len(details)):
            keys += [details[i]['name']]
            values += [details[i]['id']]
        return dict(zip(keys, values))

    def location(self, name):
        """
        Gets the information for a specified location, specified by its name.
        :param name:
        :return:
        """
        location_id = self.locations()[name]
        specific = self.get(self.base_url + 'locations/{id}.json'.format(id=location_id))
        return specific

    def departments(self, loc_name):
        """
        Gets the departments from Staffomatic for a location specified by name and returns a dictionary with the
        department names as the keys and the department id numbers as the values.
        :param loc_name:
        :return:
        """
        location_id = self.locations()[loc_name]
        details = self.get(self.base_url + 'locations/{id}/departments.json'.format(id=location_id))
        keys, values = [], []
        for i in range(len(details)):
            keys += [details[i]['name']]
            values += [details[i]['id']]
        return dict(zip(keys, values))

    def department(self, loc_name, dep_name):
        """
        Gets the information for a specified department, specified by its location and department names.
        :param loc_name:
        :param dep_name:
        :return:
        """
        location_id = self.locations()[loc_name]
        department_id = self.departments(loc_name)[dep_name]
        specific = self.get(self.base_url + 'locations/{loc_id}/departments/{dep_id}.json'.format(
            loc_id=location_id, dep_id=department_id))
        return specific

    def all_users(self, state=None):
        """
        Gets the information of all users. The caller can specify if
        :param state:
        :return:
        """
        extension = 'users.json'
        if not state:
            return self.get(self.base_url + extension)
        else:
            return self.get(self.base_url + extension, extras={'state': state})

    def loc_users(self, loc_name, dep_name=None):
        """
        Gets the information of the users in a location specified by name. If dep_name is provided then the users are
        further filtered by the department name provided.
        :param loc_name:
        :param dep_name:
        :return:
        """
        location_id = self.locations()[loc_name]
        extension = 'locations/{id}/users.json'.format(id=location_id)
        if not dep_name:
            return self.get(self.base_url + extension)
        else:
            department_id = self.departments(loc_name)[dep_name]
            return self.get(self.base_url + extension, extras={'department_ids[]': department_id})

    def loc_schedules(self, loc_name, schedule_id=None, start_date=None, end_date=None):
        """
        Gets the schedules for a given location. If the schedule id is specified then only that schedule is returned;
        if the start and end dates are specified then all schedules within those dates are returned: if no end date
        is provided then all schedules since the start date until now are returned.
        :param loc_name:
        :param schedule_id:
        :param start_date:
        :param end_date:
        :return:
        """
        location_id = self.locations()[loc_name]
        extension = 'locations/{loc_id}/schedules'.format(loc_id=location_id)
        if schedule_id:
            extension += '/{id}.json'.format(id=schedule_id)
            return self.get(self.base_url + extension)
        elif start_date:
            extension += '.json'
            # Also checks that input date is in format required.
            start_tz = self.timezone.localize(datetime.strptime(start_date, '%Y-%m-%d'))
            start_tz = datetime.strftime(start_tz, '%z')
            start_tz = start_tz[:3] + ':' + start_tz[3:]
            if not end_date:
                end_tz = datetime.now(tz=self.timezone)
            else:
                end_tz = self.timezone.localize(datetime.strptime(end_date, '%Y-%m-%d'))
            end_date = end_tz.strftime('%Y-%m-%d')
            end_tz = end_tz.strftime('%z')
            end_tz = end_tz[:3] + ':' + end_tz[3:]
            params = {'from': '{st_date}T00:00:00{st_tz}'.format(st_date=start_date, st_tz=start_tz),
                      'until': '{en_date}T23:59:59{en_tz}'.format(en_date=end_date, en_tz=end_tz)}
            return self.get(self.base_url + extension, extras=params)

    def shifts(self, loc_name=None, dep_name=None, schedule_id=None, start_date=None, end_date=None):
        """
        Gets the shifts for either a specified schedule (id number) or for a specified location where they may also be
        filtered for a date range or department.
        :param loc_name:
        :param dep_name:
        :param schedule_id:
        :param start_date:
        :param end_date:
        :return:
        """
        if schedule_id:
            extension = 'schedules/{sch_id}/shifts.json'.format(sch_id=schedule_id)
            return self.get(self.base_url + extension)
        params = {}
        location_id = self.locations()[loc_name]
        extension = 'locations/{loc_id}/shifts.json'.format(loc_id=location_id)
        if dep_name:
            department_id = self.departments(loc_name)[dep_name]
            params.update({'department_ids[]': department_id})
        if start_date:
            # Also checks that input date is in format required.
            start_tz = self.timezone.localize(datetime.strptime(start_date, '%Y-%m-%d'))
            start_tz = datetime.strftime(start_tz, '%z')
            start_tz = start_tz[:3] + ':' + start_tz[3:]
            if not end_date:
                end_tz = datetime.now(tz=self.timezone)
            else:
                end_tz = self.timezone.localize(datetime.strptime(end_date, '%Y-%m-%d'))
            end_date = end_tz.strftime('%Y-%m-%d')
            end_tz = end_tz.strftime('%z')
            end_tz = end_tz[:3] + ':' + end_tz[3:]
            params.update({'from': '{st_date}T00:00:00{st_tz}'.format(st_date=start_date, st_tz=start_tz),
                           'until': '{en_date}T23:59:59{en_tz}'.format(en_date=end_date, en_tz=end_tz)})
        return self.get(self.base_url + extension, extras=params)

    def put(self, url, data):
        r = requests.put(url=url, data=json.dumps(data), auth=self.auth)
        return r.status_code

    def post(self, url, data):
        r = requests.post(url=url, data=json.dumps(data), auth=self.auth)
        return r.status_code
