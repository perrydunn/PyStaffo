"""
A StaffoAccount instance is created for a given account, and its methods make calls to the Staffomatic API.
Caching is used to avoid repeat calls for the location name-id mappings and department name-id mappings.
"""

from datetime import datetime
from .requestors import get, put, post
from .cached import get_timezone, get_locations, get_departments


class StaffoAccount:
    def __init__(self, subdomain=None, username=None, password=None):
        self.auth = (username, password)
        self.base_url = 'https://api.staffomaticapp.com/v3/{subdomain}/'.format(subdomain=subdomain)
        self.timezone = get_timezone(self.auth, self.base_url)
        self.locations = get_locations(self.auth, self.base_url)
        self.departments = get_departments(self.auth, self.base_url)

    def get_location(self, loc_name):
        """
        Gets the information for a specified location, specified by its name.
        """
        location_id = self.locations[loc_name]
        location = get(auth=self.auth, url=self.base_url + 'locations/{id}.json'.format(id=location_id))
        return location

    def get_department(self, loc_name, dep_name):
        """
        Gets the information for a specified department, specified by its location and department names.
        """
        location_id = self.locations[loc_name]
        department_id = self.departments[loc_name][dep_name]
        department = get(auth=self.auth, url=self.base_url + 'locations/{loc_id}/departments/{dep_id}.json'.
                         format(loc_id=location_id, dep_id=department_id))
        return department

    def get_all_users(self, state=None):
        """
        Gets the information of all users. The caller filter by state of the users.
        """
        extension = 'users.json'
        if not state:
            return get(auth=self.auth, url=self.base_url + extension)
        else:
            return get(auth=self.auth, url=self.base_url + extension, extras={'state': state})

    def get_loc_users(self, loc_name, dep_name=None):
        """
        Gets the information of the users in a location specified by name. If dep_name is provided then the users are
        further filtered by the department name provided.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{id}/users.json'.format(id=location_id)
        if not dep_name:
            return get(auth=self.auth, url=self.base_url + extension)
        else:
            department_id = self.departments[loc_name][dep_name]
            return get(auth=self.auth, url=self.base_url + extension, extras={'department_ids[]': department_id})

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

    def get_loc_schedules(self, loc_name, schedule_id=None, start_date=None, end_date=None):
        """
        Gets the schedules for a given location. If the schedule id is specified then only that schedule is returned;
        if the start and end dates are specified then all schedules within those dates are returned: if no end date
        is provided then all schedules since the start date until now are returned.
        Input dates expected to be date strings in yyyy-mm-dd format.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/schedules'.format(loc_id=location_id)
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

    def get_shifts(self, loc_name=None, dep_name=None, schedule_id=None, start_date=None, end_date=None):
        """
        Gets the shifts for either a specified schedule (id number) or for a specified location where they may also be
        filtered for a date range or department.
        Input dates expected to be date strings in yyyy-mm-dd format.
        """
        if schedule_id:
            extension = 'schedules/{sch_id}/shifts.json'.format(sch_id=schedule_id)
            return get(auth=self.auth, url=self.base_url + extension)
        params = {}
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/shifts.json'.format(loc_id=location_id)
        if dep_name:
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

    def add_users(self, loc_name=None, dep_name=None, users=[], remove=False):
        """
        Add/Remove a list of user ids to/from a department in a location.
        """
        location_id = self.locations[loc_name]
        department_id = self.departments[loc_name][dep_name]
        if remove:
            extension = 'locations/{loc_id}/departments/{dep_id}/remove_users.json'.format(loc_id=location_id,
                                                                                           dep_id=department_id)
        else:
            extension = 'locations/{loc_id}/departments/{dep_id}/add_users.json'.format(loc_id=location_id,
                                                                                        dep_id=department_id)
        params = {'user_ids': users}
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def update_location(self, loc_name=None, **kwargs):
        """
        Update a location's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}.json'.format(loc_id=location_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def update_department(self, loc_name=None, dep_name=None, **kwargs):
        """
        Update a department's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered.
        """
        location_id = self.locations[loc_name]
        department_id = self.departments[loc_name][dep_name]
        extension = 'locations/{loc_id}/departments/{dep_id}.json'.format(loc_id=location_id, dep_id=department_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def update_schedule(self, loc_name=None, schedule_id=None, **kwargs):
        """
        Update a schedule's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered. Excludes publishing the schedule which is covered below.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/schedules/{sch_id}.json'.format(loc_id=location_id, sch_id=schedule_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def publish_schedule(self, loc_name=None, schedule_id=None):
        """
        Publish a schedule by the location name and schedule id.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/schedules/{sch_id}.json'.format(loc_id=location_id, sch_id=schedule_id)
        params = {'do': 'publish', 'message': 'A new schedule is available!', 'deliver_emails': True}
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def update_user(self, loc_name=None, user_id=None, **kwargs):
        """
        Update a user's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered. Excludes locking/unlocking the user's account which is covered below.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/users/{usr_id}.json'.format(loc_id=location_id, usr_id=user_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def lock_user(self, loc_name=None, user_id=None, unlock=False):
        """
        Lock/Unlock a user's account. Must provide the location name and the user id.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/users/{usr_id}.json'.format(loc_id=location_id, usr_id=user_id)
        if not unlock:
            params = {'do': 'lock'}
        else:
            params = {'do': 'unlock'}
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def update_shift(self, schedule_id=None, shift_id=None, **kwargs):
        """
        Update a shift's details. Refer to Staffomatic's own API documentation for the parameters that can be
        altered.
        """
        extension = 'schedules/{sch_id}/shifts/{shf_id}.json'.format(sch_id=schedule_id, shf_id=shift_id)
        params = {}
        for key in kwargs:
            params.update({key: kwargs[key]})
        return put(auth=self.auth, url=self.base_url + extension, data=params)

    def create_location(self, loc_name=None, allow_self_assign=True, applications_visible=False,
                        assignments_visible=True, first_day_of_week=0, swap_shifts=True, users_sort_by='alphabetical'):
        """
        Create a new location.
        """
        params = {'name': loc_name, 'allow_self_assign': allow_self_assign,
                  'applications_visible': applications_visible, 'assignments_visible': assignments_visible,
                  'first_day_of_week': first_day_of_week, 'swap_shifts': swap_shifts, 'users_sort_by': users_sort_by}
        return post(auth=self.auth, url=self.base_url + 'locations.json', data=params)

    def create_department(self, loc_name=None, dep_name=None, visibility='staff', color='4286f4', user_selectable=True,
                          include_weekends=True, position=1):
        """
        Create a new department within a named location.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/departments.json'.format(loc_id=location_id)
        params = {'visibility': visibility, 'name': dep_name, 'color': color, 'user_selectable': user_selectable,
                  'include_weekends': include_weekends, 'position': position}
        return post(auth=self.auth, url=self.base_url + extension, data=params)

    def create_schedule(self, loc_name=None, bop=None, eop=None, deadline=None, first_day_of_week=1, slot_minutes=30,
                        min_time=0, max_time=24, default_event_minutes=240, show_event_header=False,
                        applications_visible=False, assignments_visible=True, swap_shifts=True, notes_visible=False,
                        allow_self_assign=True):
        """
        Create a new schedule within a named location.
        """
        location_id = self.locations[loc_name]
        params = {'bop': bop, 'eop': eop, 'deadline': deadline, 'first_day_of_week': first_day_of_week,
                  'slot_minutes': slot_minutes, 'min_time': min_time, 'max_time': max_time,
                  'default_event_minutes': default_event_minutes, 'show_event_header': show_event_header,
                  'applications_visible': applications_visible, 'assignments_visible': assignments_visible,
                  'swap_shifts': swap_shifts, 'notes_visible': notes_visible, 'allow_self_assign': allow_self_assign}
        extension = 'locations/{loc_id}/schedules.json'.format(loc_id=location_id)
        return post(auth=self.auth, url=self.base_url + extension, data=params)

    def invite_user(self, loc_name=None, email=None, department_ids=[]):
        """
        Invite a new user to join a Staffomatic location, joining given departments given as a list of department ids.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/users.json'.format(loc_id=location_id)
        params = {'email': email, 'department_ids': department_ids, 'do': 'send_invitation'}
        return post(auth=self.auth, url=self.base_url + extension, data=params)

    def create_user(self, loc_name=None, first_name=None, last_name=None, department_ids=[]):
        """
        Create a new user within a Staffomatic location, joining given departments given as a list of department ids.
        """
        location_id = self.locations[loc_name]
        extension = 'locations/{loc_id}/users.json'.format(loc_id=location_id)
        params = {'first_name': first_name, 'last_name': last_name, 'department_ids': department_ids}
        return post(auth=self.auth, url=self.base_url + extension, data=params)

    def create_shift(self, loc_name=None, dep_name=None, schedule_id=None, starts_at=None, ends_at=None,
                     desired_coverage=1, note=''):
        """
        Create a new shift within a Staffomatic location and for a particular department.
        The input datetimes are expected to be in the format yyyy-mm-dd HH:MM:SS as strings.
        """
        start_tz = self.timezone.localize(datetime.strptime(starts_at, '%Y-%m-%d %H:%M:%S'))
        start_tz = datetime.strftime(start_tz, '%z')
        start_tz = start_tz[:3] + ':' + start_tz[3:]
        starts_at = starts_at[:10] + 'T' + starts_at[11:] + start_tz
        end_tz = self.timezone.localize(datetime.strptime(ends_at, '%Y-%m-%d %H:%M:%S'))
        end_tz = datetime.strftime(end_tz, '%z')
        end_tz = end_tz[:3] + ':' + end_tz[3:]
        ends_at = ends_at[:10] + 'T' + ends_at[11:] + end_tz
        location_id = self.locations[loc_name]
        department_id = self.departments[loc_name][dep_name]
        extension = 'schedules/{sch_id}/shifts.json'.format(sch_id=schedule_id)
        params = {'starts_at': starts_at, 'ends_at': ends_at, 'location_id': location_id,
                  'department_id': department_id, 'desired_coverage': desired_coverage, 'note': note}
        return post(auth=self.auth, url=self.base_url + extension, data=params)
