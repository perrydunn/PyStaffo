import requests
import json

per_page = 300

def get(auth=None, url=None, extras=None):
    """
    Paginated GET
    """
    data = []
    keep_going = True
    page = 1 # start with page = 1. thats the first page
    params = {'page': page, 'per_page': per_page}
    if extras:
        params.update(extras)
    try:
        while keep_going: # keep iterating over pages until `keep_going == false`
            params.update({'page': page}) # first request with page=1
            # API request
            r = requests.get(url=url, auth=auth, params=params, )
            response = json.loads(r.content.decode('utf-8'))
            # if the API returns an empty array. we know we dont have any data left
            # so we can safely abort
            if len(response) == 0:
                keep_going = False
            if (not 'Page' in r.headers):
                data += response
                keep_going = False
            else:
                data += response
                page += 1
    except KeyError:
        pass
    return data
