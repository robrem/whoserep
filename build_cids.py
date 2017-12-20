"""
Retrieves the OpenSecrets.org CIDs (Candidate IDs) for every US legislator and
write them to data/cids.txt.

The cids.txt file is used by TweetText to select a random legislator for each
tweet.
"""

import os
import json
from crpapi import CRP

try:
    from config import secrets
except ImportError:
    secrets = {
        "OPENSECRETS_API_KEY" : os.environ['OPENSECRETS_API_KEY']
    }


crp = CRP(secrets['OPENSECRETS_API_KEY'])

states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

def progress_bar(count, total, bar_len, status=''):
    """
        Prints a progress bar to the console.
        :param count: the current item iteration
        :param total: the total number of items to iterate
        :param bar_len: the length of the progress bar
        :param status: optional message regarding progress bar status
    """
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    progress = '=' * filled_len + '-' * (bar_len - filled_len)

    print('[%s] %s%s ...%s\r' % (progress, percents, '%', status))

def build_cids():
    """
        Retrieve all CIDs for current congressional members and
        write the list to data/cids.txt, replacing the previous file.
    """
    cids = []
    i = 0
    progress_bar(i, len(states), 50, 'Starting...')

    for state in states:
        i += 1
        cands = crp.candidates.get(state)
        if len(cands) > 1:
            for cand in cands:
                cids.append(cand['@attributes']['cid'])
        else:
            cids.append(cands['@attributes']['cid'])
        progress_bar(i, len(states), 50, 'Retrieving legislators from %s' % state)

    f = open('data/cids.txt', 'wb')
    json.dump(cids, f)
    f.close()

    result = 'Retrieved {num} CIDs from OpenSecrets.org.'.format(num=len(cids))
    print(result)


if __name__ == "__main__":
    build_cids()
