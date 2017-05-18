# WhoseRep
The [@WhoseRep](https://twitter.com/WhoseRep "WhoseRep Twitter page") Twitter bot pulls campaign finance data from [OpenSecrets.org](https://www.opensecrets.org/resources/create/ "OpenSecrets API page") and US congressional member data from [ProPublica.org](https://www.propublica.org/datastore/apis "ProPublica APIs page") to tweet small insights into government representatives.

## How it works
For each tweet, a legislator and one of their top campaign contributors are chosen randomly, along with some additional information, such as a committee on which the legislator serves.

**Example:** "Rep John K Delaney (D-MD) accepted $13,250 from Nasdaq Inc. He serves in the Joint Economic Committee."

## Make it work

### Dependencies
```python
pip install tweepy
pip install python-congress
```

### Configure it
You will need to create a [Twitter account](https://support.twitter.com/articles/100990 "Twitter account sign up") and [app](https://apps.twitter.com/ "Twitter apps page") for your bot.

You'll also need a [Center for Responsive Politics API key](https://www.opensecrets.org/api/admin/index.php?function=signup "OpenSecrets API key request") and a [ProPublica API key](https://www.propublica.org/datastore/api/propublica-congress-api "ProPublica API key request").

You may either rename *sample.config.py* as *config.py* and enter your keys there, or include them as environment variables.

```
'TWITTER_ACCESS_TOKEN' : '',
'TWITTER_ACCESS_TOKEN_SECRET' : '',
'TWITTER_CONSUMER_KEY' : '',
'TWITTER_CONSUMER_SECRET' : '',
'OPENSECRETS_API_KEY' : '',
'PROPUBLICA_API_KEY' : ''
```

### Run it
```python
python bot.py
```

## Make your own
There's a lot of interesting, publicly available data about US government representatives. How about extending this bot to tweet about voting records when a legislator is [mentioned in the news](https://developer.nytimes.com/ "New York Times Developer Network")?

