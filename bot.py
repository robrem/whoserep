import os
import tweepy
from time import gmtime, strftime
from tweettext import TweetText
try: 
  from config import config_vars
except ImportError:
  config_vars = {'LOG_LOCAL' : False}


# ========= Bot configuration =========
bot_name = "WhoseRep"
logfile_name = bot_name + ".log"
# =====================================


# ========= US State codes =================================================
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
# ==========================================================================


def create_tweet():
  """Create the tweet text"""
  TT = TweetText()
  return TT.get()


def tweet(text):
  """Tweet the text from the bot account"""
  # Twitter auth
  auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
  auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
  api = tweepy.API(auth)

  try:
    api.update_status(text)
  except tweepy.TweepError as e:
    log(e.message)
  else:
    log("Tweeted: " + text)


def get_rand_cand_by_state(state, crp_api):
  """Choose a random candidate from the given state"""
  cand_dict = {}
  legislators = json.dumps(crp_api.getLegislators.get(id=state))

  # Select a random legislator
  l_dict = json.loads(legislators)
  l_count = len(l_dict)

  #TODO: revisit this
  if (l_count == 0):
    log("Failed to get a legislator")
    quit()

  l_index = random.randint(0, l_count - 1)
  cand_dict = {
    'cid'       : l_dict[l_index]['@attributes']['cid'],
    'firstlast' : l_dict[l_index]['@attributes']['firstlast'],
    'gender'    : l_dict[l_index]['@attributes']['gender'],
    'party'     : l_dict[l_index]['@attributes']['party'],
    'bio_id'    : l_dict[l_index]['@attributes']['bioguide_id']
  }

  return cand_dict


def create_support_text():
  funcs = [create_committee_text, create_votes_with_party_pct_text]
  return random.choice(funcs)()


def create_committee_text():
  committee = get_rand_committee()



def get_rand_contrib_by_cand(cid, crp_api):
  """Choose a random contributor to the candidate given by cid"""
  contrib_dict = {}
  contributors = json.dumps(crp_api.candContrib.get(cid=cid))
  c_dict = json.loads(contributors)
  c_count = len(c_dict)

  #TODO: revisit this
  if (c_count == 0):
    log("Failed to get a contributor")
    quit()

  c_index = random.randint(0, c_count - 1)
  contrib_dict = {
    'name'   : c_dict[c_index]['@attributes']['org_name'],
    'amount' : c_dict[c_index]['@attributes']['total']
  }

  return contrib_dict


def get_rand_committee(member):
  """Return the name of a random committee on which the member serves"""
  count = len(member['roles'][0]['committees'])

  if (count==0):
    return ""

  index = random.randint(0, count - 1)
  return member['roles'][0]['committees'][index]['name']


def get_votes_with_party_pct(member):
  """Return the percentage which the given candidate votes with their party"""
  return member['roles']['votes_with_party_pct']


def get_gender_pronoun(gender_id):
  """Return a gender pronoun based on gender_id, or an empty string if gender not identified"""
  if (gender_id=='F'):
    return "She"
  elif (gender_id=='M'):
    return "He"
  else:
    return ""


def log(message):
  """Enter message in log file"""
  if config_vars['LOG_LOCAL']:
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)
  else:
    # Heroku prints stdout and stderr to its Logplex
    print bot_name + ": " + message


if __name__ == "__main__":
  tweet_text = create_tweet()
  print tweet_text
  # tweet(tweet_text)
