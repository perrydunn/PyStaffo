import requests
import json

PER_PAGE = 300

def get(auth=None, url=None, extras=None):
    """
    Paginated GET
    """
    page = 1
    params = {'page': page, 'per_page': PER_PAGE}
    if extras: params.update(extras)
    r = requests.get(url=url, auth=auth, params=params)
    data = json.loads(r.content.decode('utf-8'))
    keep_going = True
    while keep_going:
        page += 1
        params.update({'page': page})
        r = requests.get(url=url, auth=auth, params=params)
        response = json.loads(r.content.decode('utf-8'))
        if (not response) or ('Page' not in r.headers):
            keep_going = False
        else:
            data += response
    return data
