import os
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


    def __init__(self):
        CRP.apikey = secrets['OPENSECRETS_API_KEY']
        self.congress = Congress(secrets['PROPUBLICA_API_KEY'])
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

        spprt_text = self._get_support_text()

        text = text + " " + spprt_text

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
            'lastname'  : cand['@attributes']['lastname'],
            'gender'    : cand['@attributes']['gender'],
            'pronoun'   : self._get_gender_pronoun(cand['@attributes']['gender']),
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


    def _get_support_text(self):
        """
            Returns randomly selected support text containing additional
            information about the candidate, such as committee membership or 
            voting percentage.
        """
        funcs = [self._get_committee_text, self._get_vote_pct_text]

        return random.choice(funcs)()


    def _get_committee_text(self):
        """
            Returns text containing a candidate's commitee, formatted to tweet.

            Ex: "She serves in the Committee on Agriculture"
        """
        text_format = '%s serves in the %s.'
        committee = self._get_committee()

        return text_format % (self.candidate['pronoun'], committee)


    def _get_vote_pct_text(self):
        """
            Returns text containing a candidate's tendency to vote with 
            her/his party as a percentage, formatted to tweet.

            Ex: "She votes with own party 97% of the time."
        """
        text_format = '%s votes with own party %s%% of the time.'
        pct = self._get_votes_with_party_pct()

        return text_format % (self.candidate['pronoun'], pct)


    def _get_committee(self):
        """
            Returns the name of a random committee on which the candidate serves
        """
        cand = json.dumps(self.congress.members.get(self.candidate['bio_id']))
        c_dict = json.loads(cand)
        committee = random.choice(c_dict['roles'][0]['committees'])

        return committee['name']


    def _get_votes_with_party_pct(self):
        """
            Returns the percentage which the candidate votes with their party.
        """
        cand = json.dumps(self.congress.members.get(self.candidate['bio_id']))
        c_dict = json.loads(cand)

        return c_dict['roles'][0]['votes_with_party_pct']  


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


    def _get_gender_pronoun(self, gender_id):
        """
            Return a gender pronoun based on candidate's stated gender,
            or the candidate's last name if gender not listed.
        """
        if (gender_id=='F'):
            return "She"
        elif (gender_id=='M'):
            return "He"
        else:
            return self.candidate['lastname']