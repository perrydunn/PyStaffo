import requests
import json

per_page = 300


def get(auth=None, url=None, extras=None):
    params = {'page': 1, 'per_page': per_page}
    if extras:
        params.update(extras)
    r = requests.get(url=url, auth=auth, params=params)
    data = json.loads(r.content.decode('utf-8'))
    try:
        pages = int(r.headers['Pages'])
        if pages > 1:
            for page in range(2, pages + 1):
                params.update({'page': page})
                r = requests.get(url=url, auth=auth, params=params)
                data += json.loads(r.content.decode('utf-8'))
    except KeyError:
        pass
    return data


def put(auth=None, url=None, data=None):
    r = requests.put(auth=auth, url=url, data=data)
    return r.status_code


def post(auth=None, url=None, data=None):
    r = requests.post(auth=auth, url=url, data=data)
    return r.status_code
