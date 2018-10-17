"""
A StaffoAccount instance is created for a given account, and its methods make calls to the Staffomatic API.
Caching is used to avoid repeat calls for the location name-id mappings and department name-id mappings.
"""

import requests
import json
from datetime import datetime
from .requestors import get
from .cached import get_timezone, get_locations, get_departments


class StaffoAccount:
    def __init__(self, subdomain=None, username=None, password=None):
        self.auth = (username, password)
        self.base_url = 'https://api.staffomaticapp.com/v3/{subdomain}/'.format(subdomain=subdomain)
        self.timezone = get_timezone(self.auth, self.base_url)
        self.locations = get_locations(self.auth, self.base_url)
        self.departments = get_departments(self.auth, self.base_url)

    def get_location(self, location_id=None, loc_name=None):
        """
        Gets the information for a specified location, specified by its id or name.
        """
        if location_id:
            return get(auth=self.auth, url=self.base_url + 'locations/{id}.json'.format(id=location_id))
        else:
            location_id = self.locations[loc_name]
            return get(auth=self.auth, url=self.base_url + 'locations/{id}.json'.format(id=location_id))

    def get_department(self, department_id=None, loc_name=None, dep_name=None):
        """
        Gets the information for a specified department, specified by its id or by its location and department names.
        """
        if department_id:
            return get(auth=self.auth, url=self.base_url + 'departments/{dep_id}.json'.format(dep_id=department_id))
        else:
            department_id = self.departments[loc_name][dep_name]
            return get(auth=self.auth, url=self.base_url + 'departments/{dep_id}.json'.format(dep_id=department_id))

    def get_all_users(self, state=None):
        """
        Gets the information of all users, filterable by state of the users.
        """
        extension = 'users.json'
        if not state:
            return get(auth=self.auth, url=self.base_url + extension)
        else:
            return get(auth=self.auth, url=self.base_url + extension, extras={'state': state})

    def get_loc_users(self, location_id=None, loc_name=None, dep_name=None):
        """
        Gets the information of the users in a location specified by id or name. If dep_name is provided then the users
        are further filtered by the department name provided.
        """
        if not location_id:
            location_id = self.locations[loc_name]
        extension = 'locations/{id}/users.json'.format(id=location_id)
        if not dep_name:
            return get(auth=self.auth, url=self.base_url + extension)
        else:
            department_id = self.departments[loc_name][dep_name]
            return get(auth=self.auth, url=self.base_url + extension, extras={'department_ids': department_id})

    def get_schedules(self, schedule_id=None, start_date=None, end_date=None):
        """
        Gets the schedules (for all locations). If the schedule id is specified then only that schedule is returned;
        if the start and end dates are specified then all schedules within those dates are returned: if no end date
        is provided then all schedules since the start date until now are returned.
        Input dates expected to be date strings in yyyy-mm-dd format.
        """
        extension = 'schedules'
        if schedule_id:
            extension += '/{id}.json'.format(id=schedule_id)
            return get(auth=self.auth, url=self.base_url + extension)
        elif start_date:
            extension += '.json'
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
            return get(auth=self.auth, url=self.base_url + extension, extras=params)

    def get_loc_schedules(self, location_id=None, loc_name=None, start_date=None, end_date=None):
        """
        Gets the schedules for a given location.
        All schedules within between the start and end dates are returned: if no end date
        is provided then all schedules since the start date until now are returned.
        Input dates expected to be date strings in yyyy-mm-dd format.
        """
        if not location_id:
            location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/schedules.json'.format(loc_id=location_id)
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
        return get(auth=self.auth, url=self.base_url + extension, extras=params)

    def get_shifts(self, location_id=None, loc_name=None, department_id=None, dep_name=None, schedule_id=None,
                   start_date=None, end_date=None):
        """
        Gets the shifts for either a specified schedule (id number) or for a specified location where they may also be
        filtered for a date range or department.
        For filtering by location and department it is expected that the user is either using names or IDs but not a
        mixture of the two.
        In a later version it will be possible to filter for multiple departments.
        Input dates expected to be date strings in yyyy-mm-dd format.
        """
        if schedule_id:
            extension = 'schedules/{sch_id}/shifts.json'.format(sch_id=schedule_id)
            return get(auth=self.auth, url=self.base_url + extension)
        params = {}
        if location_id or loc_name:
            if not location_id:
                location_id = self.locations[loc_name]
            extension = 'locations/{loc_id}/shifts.json'.format(loc_id=location_id)
        else:
            extension = 'shifts.json'
        if department_id or dep_name:
            if not department_id:
                department_id = self.departments[loc_name][dep_name]
            params.update({'department_ids[]': department_id})
        if start_date:
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
        return get(auth=self.auth, url=self.base_url + extension, extras=params)

    def add_users(self, department_id=None, loc_name=None, dep_name=None, users=None, remove=False):
        """
        Add/Remove a list of user ids to/from a department identified either by its ID or by its location and
        department names.
        """
        if not department_id:
            department_id = self.departments[loc_name][dep_name]
        extension = 'departments/{dep_id}/'.format(dep_id=department_id)
        if remove:
            extension += 'remove_users.json'
        else:
            extension += 'add_users.json'
        params = {'user_ids': users}
        return requests.put(auth=self.auth, url=self.base_url + extension, json=params)

    def update_location(self, location_id=None, loc_name=None, **kwargs):
        """
        Update a location's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered.
        """
        if not location_id:
            location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}.json'.format(loc_id=location_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        response = requests.put(auth=self.auth, url=self.base_url + extension, json=params)
        if response.status_code is 200 and 'name' in kwargs.keys():
            data = json.loads(response.content.decode('utf-8'))
            locations = {self.locations[key]: key for key in self.locations.keys()}
            old_name = locations[data['id']]
            self.departments[data['name']] = self.departments.pop(old_name)
            locations.update({data['id']: data['name']})
            self.locations = {locations[key]: key for key in locations}
        return response

    def update_department(self, department_id=None, loc_name=None, dep_name=None, **kwargs):
        """
        Update a department's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered.
        """
        if not department_id:
            department_id = self.departments[loc_name][dep_name]
        extension = 'departments/{dep_id}.json'.format(dep_id=department_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        response = requests.put(auth=self.auth, url=self.base_url + extension, json=params)
        if response.status_code is 200 and 'name' in kwargs.keys():
            data = json.loads(response.content.decode('utf-8'))
            for key in self.departments:
                location_departments = self.departments[key]
                location_departments = {location_departments[k]: k for k in location_departments}
                if data['id'] in location_departments:
                    location_departments.update({data['id']: data['name']})
                    location_departments = {location_departments[k]: k for k in location_departments}
                    self.departments[key] = location_departments
                    break
        return response

    def update_schedule(self, schedule_id=None, **kwargs):
        """
        Update a schedule's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered. Excludes publishing the schedule which is covered below.
        """
        extension = 'schedules/{sch_id}.json'.format(sch_id=schedule_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return requests.put(auth=self.auth, url=self.base_url + extension, json=params)

    def publish_schedule(self, schedule_id=None, deliver_emails=True):
        """
        Publish a schedule by the location name and schedule id.
        """
        extension = 'schedules/{sch_id}.json'.format(sch_id=schedule_id)
        params = {'do': 'publish', 'message': 'A new schedule is available!', 'deliver_emails': deliver_emails}
        return requests.put(auth=self.auth, url=self.base_url + extension, json=params)

    def update_user(self, user_id=None, **kwargs):
        """
        Update a user's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered. Excludes locking/unlocking the user's account which is covered below.
        """
        extension = 'users/{usr_id}.json'.format(usr_id=user_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return requests.put(auth=self.auth, url=self.base_url + extension, json=params)

    def lock_user(self, user_id=None, unlock=False):
        """
        Lock/Unlock a user's account. Must provide the location name and the user id.
        """
        extension = 'users/{usr_id}.json'.format(usr_id=user_id)
        if not unlock:
            params = {'do': 'lock'}
        else:
            params = {'do': 'unlock'}
        return requests.put(auth=self.auth, url=self.base_url + extension, json=params)

    def update_shift(self, shift_id=None, **kwargs):
        """
        Update a shift's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered.
        """
        extension = 'shifts/{shf_id}.json'.format(shf_id=shift_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return requests.put(auth=self.auth, url=self.base_url + extension, json=params)

    def create_location(self, loc_name=None, allow_self_assign=True, applications_visible=False,
                        assignments_visible=True, first_day_of_week=0, swap_shifts=True, users_sort_by='alphabetical',
                        allow_self_remove=False, **kwargs):
        """
        Create a new location.
        """
        params = {'name': loc_name, 'allow_self_assign': allow_self_assign,
                  'applications_visible': applications_visible, 'assignments_visible': assignments_visible,
                  'first_day_of_week': first_day_of_week, 'swap_shifts': swap_shifts, 'users_sort_by': users_sort_by,
                  'allow_self_remove': allow_self_remove}
        for key in kwargs:
            params.update({key: kwargs[key]})
        response = requests.post(auth=self.auth, url=self.base_url + 'locations.json', json=params)
        if response.status_code is 200:
            data = json.loads(response.content.decode('utf-8'))
            self.locations.update({data['name']: data['id']})
            self.departments.update({data['name']: {}})
        return response

    def create_department(self, location_id=None, loc_name=None, dep_name=None, visibility='staff', color='4286f4',
                          user_selectable=True, include_weekends=True, position=1, **kwargs):
        """
        Create a new department within a location identified either by id or by name.
        """
        if not location_id:
            location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/departments.json'.format(loc_id=location_id)
        params = {'visibility': visibility, 'name': dep_name, 'color': color, 'user_selectable': user_selectable,
                  'include_weekends': include_weekends, 'position': position}
        for key in kwargs:
            params.update({key: kwargs[key]})
        response = requests.post(auth=self.auth, url=self.base_url + extension, json=params)
        if response.status_code is 200:
            data = json.loads(response.content.decode('utf-8'))
            if not loc_name:
                locations = {self.locations[key]: key for key in self.locations}
                loc_name = locations[location_id]
            self.departments[loc_name].update({data['name']: data['id']})
        return response

    def create_schedule(self, location_id=None, loc_name=None, bop=None, eop=None, deadline=None, first_day_of_week=1,
                        slot_minutes=30, min_time=0, max_time=24, default_event_minutes=240, show_event_header=False,
                        applications_visible=True, assignments_visible=True, swap_shifts=True, notes_visible=False,
                        allow_self_assign=True, allow_overlapping_assignments=False, allow_self_remove=False, **kwargs):
        """
        Create a new schedule within a location identified by ID or name.
        """
        if not location_id:
            location_id = self.locations[loc_name]
        params = {'bop': bop, 'eop': eop, 'deadline': deadline, 'first_day_of_week': first_day_of_week,
                  'slot_minutes': slot_minutes, 'min_time': min_time, 'max_time': max_time,
                  'default_event_minutes': default_event_minutes, 'show_event_header': show_event_header,
                  'applications_visible': applications_visible, 'assignments_visible': assignments_visible,
                  'swap_shifts': swap_shifts, 'notes_visible': notes_visible, 'allow_self_assign': allow_self_assign,
                  'allow_overlapping_assignments': allow_overlapping_assignments,
                  'allow_self_remove': allow_self_remove}
        for key in kwargs:
            params.update({key: kwargs[key]})
        extension = 'locations/{loc_id}/schedules.json'.format(loc_id=location_id)
        return requests.post(auth=self.auth, url=self.base_url + extension, json=params)

    def invite_user(self, location_id=None, loc_name=None, email=None, department_ids=None, dep_names=None, **kwargs):
        """
        Invite a new user to join a Staffomatic location, joining given departments given as a list of department ids,
        or a list of department names within a named location.
        """
        if not location_id:
            location_id = self.locations[loc_name]
            if not department_ids:
                department_ids = [self.departments[loc_name][dep_name] for dep_name in dep_names]
        extension = 'locations/{loc_id}/users.json'.format(loc_id=location_id)
        params = {'email': email, 'department_ids': department_ids, 'do': 'send_invitation'}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return requests.post(auth=self.auth, url=self.base_url + extension, json=params)

    def create_user(self, location_id=None, loc_name=None, first_name=None, last_name=None, department_ids=None):
        """
        Create a new user within a Staffomatic location, joining given departments given as a list of department ids.
        """
        if not location_id:
            location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/users.json'.format(loc_id=location_id)
        params = {'first_name': first_name, 'last_name': last_name, 'department_ids': department_ids}
        return requests.post(auth=self.auth, url=self.base_url + extension, json=params)

    def create_shift(self, location_id=None, loc_name=None, department_id=None, dep_name=None, schedule_id=None,
                     starts_at=None, ends_at=None, desired_coverage=1, note=None, **kwargs):
        """
        Create a new shift within a Staffomatic location and for a particular department.
        The input datetimes are expected to be in the format yyyy-mm-dd HH:MM:SS as strings.
        The schedule id must be specified.
        In the next version this will be simplified.
        """
        start_tz = self.timezone.localize(datetime.strptime(starts_at, '%Y-%m-%d %H:%M:%S'))
        start_tz = datetime.strftime(start_tz, '%z')
        start_tz = start_tz[:3] + ':' + start_tz[3:]
        starts_at = starts_at[:10] + 'T' + starts_at[11:] + start_tz
        end_tz = self.timezone.localize(datetime.strptime(ends_at, '%Y-%m-%d %H:%M:%S'))
        end_tz = datetime.strftime(end_tz, '%z')
        end_tz = end_tz[:3] + ':' + end_tz[3:]
        ends_at = ends_at[:10] + 'T' + ends_at[11:] + end_tz
        if not location_id:
            location_id = self.locations[loc_name]
            department_id = self.departments[loc_name][dep_name]
        extension = 'schedules/{sch_id}/shifts.json'.format(sch_id=schedule_id)
        params = {'starts_at': starts_at, 'ends_at': ends_at, 'location_id': location_id,
                  'department_id': department_id, 'desired_coverage': desired_coverage, 'note': note}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return requests.post(auth=self.auth, url=self.base_url + extension, json=params)

    def assign_user_to_shift(self, shift_id=None, user_id=None):
        """
        Assigns user_id to shift_id. No bulk method available yet.
        """
        extension = 'shifts/{shft_id}/assign.json'.format(shft_id=shift_id)
        params = {'user_id': user_id}
        return requests.put(auth=self.auth, url=self.base_url + extension, json=params)

    def get_events(self, start_date=None, end_date=None):
        """
        Collects the events...
        """
        extension = 'events.json'
        if start_date:
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
            params = {
                'from': '{st_date}T00:00:00{st_tz}'.format(st_date=start_date, st_tz=start_tz),
                'until': '{en_date}T23:59:59{en_tz}'.format(en_date=end_date, en_tz=end_tz)
            }
            return get(auth=self.auth, url=self.base_url + extension, extras=params)
        return get(auth=self.auth, url=self.base_url + extension)
