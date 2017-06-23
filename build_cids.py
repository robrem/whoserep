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


def build_cids():
    """
        Retrieve all CIDs for current congressional members and 
        write the list to data/cids.txt, replacing the previous file.
    """
    cids = []

    for state in states:
        cands = crp.candidates.get(state)
        if len(cands) > 1:
            for cand in cands:
                cids.append(cand['@attributes']['cid'])
        else:
                cids.append(cands['@attributes']['cid'])

    f = open('data/cids.txt','wb')
    json.dump(cids, f)
    f.close()

    result = 'Retrieved {num} CIDs from OpenSecrets.org.'.format(num=len(cids))
    print(result)


if __name__ == "__main__":
    build_cids()