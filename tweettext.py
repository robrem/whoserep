import os
import json
import random
import HTMLParser
from wr_crpapi import CRP, CRPApiError
from congress import Congress, CongressError
try:
    from config import secrets
except ImportError:
    secrets = {
        "OPENSECRETS_API_KEY" : os.environ['OPENSECRETS_API_KEY'],
        "PROPUBLICA_API_KEY"  : os.environ['PROPUBLICA_API_KEY']
    }

# The max char length for a tweet
MAX_TWEET_LEN = 140

# The most recent year that personal finance disclosure agreements
# (PFD) were submitted by congress.
PFD_YEAR = 2014


class TweetTextError(Exception):
    """
        Exception for general TweetText errors.
    """


class TweetText(object):
    """
        The text to be tweeted.

        Tweet text is assembled from the results of querying
        OpenSecrets.org and ProPublica.org data.
    """


    def __init__(self, cid=None):
        # APIs
        CRP.apikey = secrets['OPENSECRETS_API_KEY']
        self.congress = Congress(secrets['PROPUBLICA_API_KEY'])

        # The government member we'll tweet about
        self.candidate = self._get_candidate(cid)


    def get(self):
        """
            Returns the prepared tweet text.
        """
        if self.candidate is None:
            raise TweetTextError('Failed to get a candidate')

        contrib = self._get_contribution()

        if not contrib:
            raise TweetTextError('Failed to get contribution')

        text_format = 'Rep %s (%s-%s) accepted $%s from %s.'

        main_text = text_format % \
                   (self.candidate['firstlast'],
                    self.candidate['party'],
                    self.candidate['state'],
                    contrib['amount'],
                    contrib['name']
                    )

        spprt_text = self._get_support_text()
        final_text = main_text + " " + spprt_text

        # Let's try different support text if the tweet is too long
        # or the support text is empty
        tries = 3
        while ((len(final_text) > MAX_TWEET_LEN \
                or not spprt_text) \
                and tries > 0):
            spprt_text = self._get_support_text()
            final_text = main_text + " " + spprt_text
            tries -= tries

        if (tries==0):
            return main_text

        return final_text


    def _get_candidate(self, cid):
        """
            Chooses a random candidate from a random US state. If a 
            specific cid is given, choose that candidate instead.

            Returns a dict containing the candidate's information.
        """

        try:
            if cid:
                c = json.dumps(CRP.getLegislators.get(id=cid))
            else:
                state = self._get_us_state()
                c = json.dumps(CRP.getLegislators.get(id=state))
        except CRPApiError:
            return None

        cands = json.loads(c)
        cands_len = len(cands)
        
        if cands_len > 1:
            cand = random.choice(cands)
        elif cands_len == 1:
            cand = cands
        else:
            return None

        cand_dict = {
            'cid'       : cand['@attributes']['cid'],
            'firstlast' : cand['@attributes']['firstlast'],
            'lastname'  : cand['@attributes']['lastname'].lower().title(),
            'gender'    : cand['@attributes']['gender'],
            'pronoun'   : self._get_gender_pronoun(cand['@attributes']['gender']),
            'party'     : cand['@attributes']['party'],
            'state'     : cand['@attributes']['office'][:2],
            'bio_id'    : cand['@attributes']['bioguide_id']
        }

        return cand_dict


    def _get_contribution(self):
        """
            Choose a random contributor to the candidate.

            Returns a dict containing contributor information.
        """
        try:
            c = json.dumps(CRP.candContrib.get(cid=self.candidate['cid']))
        except CRPApiError:
            return None

        contribs = json.loads(c)
        contribs_len = len(contribs)

        if contribs_len > 1:
            contrib = random.choice(contribs)
        elif contribs_len == 1:
            contrib = contribs
        else:
            return None

        amount = int(contrib['@attributes']['total'])

        contrib_dict = {
            'name'   : contrib['@attributes']['org_name'],
            'amount' : format(amount, ",d")
        }

        return contrib_dict


    def _get_support_text(self):
        """
            Returns randomly selected support text containing additional
            information about the candidate, such as committee membership or 
            voting percentage.
        """
        funcs = [self._get_committee_text, self._get_vote_pct_text, self._get_net_worth_text]
        return random.choice(funcs)()


    def _get_committee_text(self):
        """
            Returns text containing a candidate's commitee, formatted to tweet.

            Ex: "She serves in the Committee on Agriculture"
        """
        committee = self._get_committee()

        if not committee:
            return ''
        
        text_format = '%s serves in the %s.'

        if self.candidate['pronoun']:
            return text_format % (self.candidate['pronoun'][0], committee)

        return text_format % (self.candidate['lastname'], committee)


    def _get_vote_pct_text(self):
        """
            Returns text containing a candidate's tendency to vote with 
            her/his party as a percentage, formatted to tweet.

            Ex: "She votes with her party 97% of the time."
        """
        pct = self._get_votes_with_party_pct()

        if not pct:
            return ''

        if self.candidate['pronoun']:
            return '%s votes with %s party %s%% of the time.' % \
                   (self.candidate['pronoun'][0], \
                    self.candidate['pronoun'][1].lower(), \
                    pct
                   )

        # There are no pronouns, indicating that gender
        # was not specified. Use last name instead.
        return '%s votes along party lines %s%% of the time.' % \
                (self.candidate['lastname'], \
                 pct
                )


    def _get_net_worth_text(self):
        """
            Returns text containing the candidate's estimated net worth,
            formatted to tweet.

            Ex: "Her estimated net worth in 2014 was $101,273,023."
        """
        net_worth = self._get_net_worth()

        if not net_worth:
            return ''

        if self.candidate['pronoun']:
            return "%s estimated net worth in %s was $%s." % \
                    (self.candidate['pronoun'][1], \
                     PFD_YEAR, \
                     net_worth
                    )

        # There are no pronouns, indicating that gender
        # was not specified. Use last name instead.
        return "%s's estimated net worth in %s was $%s." % \
                (self.candidate['lastname'], \
                 PFD_YEAR, \
                 net_worth
                )


    def _get_committee(self):
        """
            Returns the name of a random committee on which the candidate serves.
        """
        try:
            cand = json.dumps(self.congress.members.get(self.candidate['bio_id']))
        except CongressError:
            return None

        c = json.loads(cand)
        
        if 'committees' in c['roles'][0] and len(c['roles'][0]['committees']) > 0:
            committees = c['roles'][0]['committees']
            committee = random.choice(committees)
            h = HTMLParser.HTMLParser()

            return h.unescape(committee['name'])

        else:
            return None


    def _get_votes_with_party_pct(self):
        """
            Returns the percentage which the candidate votes with their party.
        """
        try:
            cand = json.dumps(self.congress.members.get(self.candidate['bio_id']))
        except CongressError:
            return None

        c_dict = json.loads(cand)

        
        if 'votes_with_party_pct' in c_dict['roles'][0]:
            pct = c_dict['roles'][0]['votes_with_party_pct']
        else:
            return None

        return pct


    def _get_net_worth(self):
        """
            Returns a candidate's estimated net worth based on the most
            recent personal finance disclosure (PFD).
        """
        try:
            pfd = json.dumps(CRP.memPFDprofile.get(cid=self.candidate['cid'], year=PFD_YEAR))
        except CRPApiError:
            return None

        pfd_dict = json.loads(pfd)

        if 'net_high' in pfd_dict['@attributes'] and \
           'net_low' in pfd_dict['@attributes']:

            net_high = int(pfd_dict['@attributes']['net_high'])
            net_low = int(pfd_dict['@attributes']['net_low'])
        else:
            return None

        net_worth = (net_high + net_low) / 2

        return format(net_worth, ",d")


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
            Returns third person pronouns based on candidate's stated gender as 
            a tuple (pronoun, possessive_pronoun). If gender not listed, 
            'None' is returned.

            Exs: ("She", "her")
        """
        if (gender_id=='F'):
            return ("She", "Her")
        elif (gender_id=='M'):
            return ("He", "His")
        else:
            return None
