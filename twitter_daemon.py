"""
Continuously iterates over existing database and pulls in tweets for each paper.
"""

import time
import json
import urllib

import twitter # pip install python-twitter

from run import write_json

# -----------------------------------------------------------------------------

def get_api_keys():
    lines = open('twitter.txt', 'r').read().splitlines()
    return lines

def process_tweet(r):
    tweet = {}
    tweet['id'] = str(r.id)
    tweet['name'] = r.user.screen_name
    tweet['image_url'] = r.user.profile_image_url
    tweet['followers'] = r.user.followers_count
    tweet['verified'] = r.user.verified
    tweet['text'] = r.full_text
    return tweet

def get_tweets(j):

    # note: we're assuming v1, which is kinda sketchy and slightly wrong...
    q = f"https://www.{j['rel_site']}.org/content/{j['rel_doi']}v1"
    q = urllib.parse.quote(q, safe='')
    exclude_replies = '%20-filter%3Areplies'
    exclude_retweets = '%20-filter%3Aretweets'
    suffix = exclude_replies + exclude_retweets
    results = api.GetSearch(raw_query="q=%s%s&result_type=recent&count=100" % (q, suffix)) # rate limit: 1 per 5 seconds

    # extract just what we need from tweets and not much more
    jtweets = [process_tweet(r) for r in results]

    # ban a few simple aggregator accounts
    banned = ['medrxivpreprint', 'biorxivpreprint', 'glycopreprint']
    jtweets = [t for t in jtweets if t['name'] not in banned]

    return jtweets

# -----------------------------------------------------------------------------

if __name__ == '__main__':

    keys = get_api_keys()
    api = twitter.Api(consumer_key=keys[0],
                      consumer_secret=keys[1],
                      access_token_key=keys[2],
                      access_token_secret=keys[3],
                      tweet_mode='extended')

    # run forever
    while True:

        # open the latest state of database
        with open('jall.json', 'r') as f:
            jall = json.load(f)

        # get all tweets for all papers
        tweets = {}
        for i, j in enumerate(jall['rels']):
            jtweets = get_tweets(j)
            tweets[j['rel_doi']] = jtweets
            print('%d/%d: found %d tweets for %s' % (i+1, len(jall['rels']), len(jtweets), j['rel_link']))
            # rate limit is 180 calls per 5 minutes, or 1 call per 5 seconds. so sleep 7
            time.sleep(10)

        # save to file when done
        write_json(tweets, 'tweets.json')
        print('-'*80)

