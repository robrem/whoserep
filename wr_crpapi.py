""" 
  Python library for interacting with the CRP API based on James Turks'
  Python CRP API (https://code.google.com/archive/p/python-crpapi/downloads)

  The CRP API (http://www.opensecrets.org/action/api_doc.php) provides campaign 
  finance and other data from the Center for Responsive Politics.

  Example usage:
  >>> print CRP.candSummary.get(cid='N00007360',cycle='2016')
  {u'origin': u'Center for Responsive Politics', u'next_election': u'2016', u'debt': u'0', 
  u'last_updated': u'12/31/2016', u'cand_name': u'Pelosi, Nancy', u'cid': u'N00007360', 
  u'spent': u'3478460.87', u'chamber': u'H', u'state': u'CA', u'first_elected': u'1987', 
  u'source': u'http://www.opensecrets.org/politicians/summary.php?cid=N00007360&cycle=2016', 
  u'party': u'D', u'total': u'4318118.79', u'cash_on_hand': u'1820817.85', u'cycle': u'2016'}
"""

import urllib, urllib2
import json

class CRPApiError(Exception):
    """ Exception for CRP API errors """

# results #
class CRPApiObject(object):
    def __init__(self, d):
        self.__dict__ = d

# namespaces #
class CRP(object):

    apikey = None

    @staticmethod
    def _apicall(func, params):
        if CRP.apikey is None:
            raise CRPApiError('Missing CRP apikey')

        url = 'https://www.opensecrets.org/api/?method=%s&output=json&apikey=%s&%s' % \
              (func, CRP.apikey, urllib.urlencode(params))
        headers = { 'User-Agent' : 'Mozilla/5.0' }

        try:
            request = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(request).read()
            return json.loads(response)['response']
        except urllib2.HTTPError, e:
            raise CRPApiError(e.read())
        except (ValueError, KeyError), e:
            raise CRPApiError('Invalid Response')

    class candSummary(object):
        @staticmethod
        def get(**kwargs):
            result = CRP._apicall('candSummary', kwargs)['summary']
            return result['@attributes']

    class candContrib(object):
        @staticmethod
        def get(**kwargs):
            results = CRP._apicall('candContrib', kwargs)['contributors']['contributor']
            return results

    class candIndustry(object):
        @staticmethod
        def get(**kwargs):
            results = CRP._apicall('candIndustry', kwargs)['industries']['industry']
            return results

    class candSector(object):
        @staticmethod
        def get(**kwargs):
            results = CRP._apicall('candSector', kwargs)['sectors']['sector']
            return results

    class candIndByInd(object):
        @staticmethod
        def get(**kwargs):
            result = CRP._apicall('CandIndByInd', kwargs)['candIndus']
            return result['@attributes']

    class memTravelTrips(object):
        @staticmethod
        def get(**kwargs):
            results = CRP._apicall('memTravelTrips', kwargs)['trips']['trip']
            return results