import json
import random
from wr_crpapi import CRP, CRPApiError
from congress import Congress
try:
    from config import secrets
except ImportError:
    secrets = {
        "TWITTER_ACCESS_TOKEN"        : os.environ['TWITTER_ACCESS_TOKEN'],
        "TWITTER_ACCESS_TOKEN_SECRET" : os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
        "TWITTER_CONSUMER_KEY"        : os.environ['TWITTER_CONSUMER_KEY'],
        "TWITTER_CONSUMER_SECRET"     : os.environ['TWITTER_CONSUMER_SECRET'],
        "OPENSECRETS_API_KEY"         : os.environ['OPENSECRETS_API_KEY'],
        "PROPUBLICA_API_KEY"          : os.environ['PROPUBLICA_API_KEY']
    }


class TweetText(object):
    """
        The text to be tweeted.

        Tweet text is assembled from the results of querying
        OpenSecrets.org and ProPublica.org data.
    """

    CRP.apikey = secrets['OPENSECRETS_API_KEY']
    congress_api = Congress(secrets['PROPUBLICA_API_KEY'])

    def __init__(self):
        self.candidate = self._get_candidate()


    def get(self):
        """
            Returns the prepared tweet text.
        """
        text_format = 'Rep %s (%s-%s) accepted $%s from %s.'

        contrib = self._get_contribution()

        text = text_format % \
               (self.candidate['firstlast'],
                self.candidate['party'],
                self.candidate['state'],
                contrib['amount'],
                contrib['name']
                )

        # TODO: get support text
        #       check and adjust text len

        return text


    def _get_candidate(self):
        """
            Choose a random candidate from a random US state.

            Returns a dict containing candidate information.
        """
        state = self._get_us_state()
        candidates = json.dumps(CRP.getLegislators.get(id=state))

        # Select a random candidate
        # TODO: error checking
        cands_dict = json.loads(candidates)
        cand = random.choice(cands_dict)

        cand_dict = {
            'cid'       : cand['@attributes']['cid'],
            'firstlast' : cand['@attributes']['firstlast'],
            'gender'    : cand['@attributes']['gender'],
            'party'     : cand['@attributes']['party'],
            'state'     : state,
            'bio_id'    : cand['@attributes']['bioguide_id']
        }

        return cand_dict


    def _get_contribution(self):
        """
            Choose a random contributor to the candidate.

            Returns a dict containing contributor information.
        """
        contributors = json.dumps(CRP.candContrib.get(cid=self.candidate['cid']))
        contribs_dict = json.loads(contributors)
        contrib = random.choice(contribs_dict)

        contrib_dict = {
            'name'   : contrib['@attributes']['org_name'],
            'amount' : contrib['@attributes']['total']
        }

        return contrib_dict


    def _get_committee(self):
        """
            Returns the name of a random committee on which the candidate serves
        """
        candidate = congress_api.members.get(self.candidate['bio_id'])
        committee = random.select(candidate['roles'][0]['committees'])
        return committee['name']


    def _get_votes_with_party_pct(self):
        """
            Returns the percentage which the candidate votes with their party.
        """
        candidate = congress_api.members.get(self.candidate['bio_id'])
        return candidate['roles'][0]['votes_with_party_pct']  


    def _get_us_state(self):
        """
            Returns a randomly selected US state code.
        """
        states = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]

        return random.choice(states)