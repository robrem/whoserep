import os
import tweepy
from time import gmtime, strftime
from tweettext import TweetText
try: 
    from config import *
except ImportError:
    secrets = {
        "TWITTER_ACCESS_TOKEN"        : os.environ['TWITTER_ACCESS_TOKEN'],
        "TWITTER_ACCESS_TOKEN_SECRET" : os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
        "TWITTER_CONSUMER_KEY"        : os.environ['TWITTER_CONSUMER_KEY'],
        "TWITTER_CONSUMER_SECRET"     : os.environ['TWITTER_CONSUMER_SECRET']
    }
    config_vars = { 'LOG_LOCAL' : False }


# ========= Bot configuration =========
bot_name = "WhoseRep"
logfile_name = bot_name + ".log"
# =====================================


def create_tweet():
    """Create the tweet text"""
    try:
        TT = TweetText()
    except TweetTextError:
        return None

    return TT.get()


def tweet(text):
    """Tweet the text from the bot account"""
    # Twitter auth
    auth = tweepy.OAuthHandler(secrets['TWITTER_CONSUMER_KEY'], secrets['TWITTER_CONSUMER_SECRET'])
    auth.set_access_token(secrets['TWITTER_ACCESS_TOKEN'], secrets['TWITTER_ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)

    try:
        api.update_status(text)
    except tweepy.TweepError as e:
        log(e.message)
    else:
        log("Tweeted: " + text)


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

    if tweet_text:
        tweet(tweet_text)
