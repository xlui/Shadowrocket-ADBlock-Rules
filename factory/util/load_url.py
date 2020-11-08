import sys
import time

import requests


def load_url(url):
    success = False
    try_times = 0
    r = None
    while try_times < 5 and not success:
        r = requests.get(url)
        if r.status_code != 200:
            time.sleep(1)
            try_times = try_times + 1
        else:
            success = True
            break

    if not success:
        sys.exit('error in request %s\n\treturn code: %d' % (rule_url, r.status_code))
    return r.text
