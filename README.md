# PyStaffo
*PyStaffo* is a Python wrapper library for the Staffomatic/Easypep API that simplifies many common tasks.

## Installation
Either from PyPi:

```
$ pip install PyStaffo
```

Or from GitHub:

```
$ pip install git+https://github.com/perrydunn/PyStaffo
```

## Requirements
* Python 3 except 3.2 (untested on Python 2)
* You need a Staffomatic account! A Staffomatic account includes a sub-domain name, and login details as a username and password.

## Basic Use
```
from pystaffo import StaffoAccount

subdomain = '<subdomain>'
username = '<username>'
password = '<password>'

account = StaffoAccount(subdomain=subdomain, username=username, password=password)

# The locations and departments are cached as attributes of the class instance.
# Return dictionary of {'department_name': department_id, ...}:
account.locations

# Return the information of a particular location:
account.get_location('Westway')
```

## Nuts and Bolts
A ```StaffoAccount()``` instance has various ```GET```, ```PUT``` and ```POST``` API calls expressed as methods: these will be added to. So far there are no ```DELETE``` calls.

Please refer to the ```staffo.py``` for the methods currently available, and feel free to add some more!

### Timezone Handling
PyStaffo handles timezones for you, using the timezone detailed in your account. If there are timezone issues you may need to look "under the hood". Please suggest improvements/alternatives.

### Contributing
If you would like to see features added or tweaked, please fork, make your changes and open a PR. Feel free to get in touch too.

### Aknowledgements
- [**Staffomatic API Documentation**](https://github.com/staffomatic/staffomatic-api-documentation)


