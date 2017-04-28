import tweepy
from auth import *
from wr_crpapi import CRP, CRPApiError

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
CRP.apikey = OPENSECRETS_API_KEY

