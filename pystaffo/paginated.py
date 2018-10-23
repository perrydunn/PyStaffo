import requests
import json

per_page = 300


def get(auth=None, url=None, extras=None):
    """
    Paginated GET
    """
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
