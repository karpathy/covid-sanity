"""
Continuously iterates over existing database and pulls in tweets for each paper.
Intended to be run in a screen session forver alongside the flask server, which
will pull in its results every time it gets reset for updates.
"""

import os
import sys
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

    try:
        results = api.GetSearch(raw_query="q=%s%s&result_type=recent&count=100" % (q, suffix))
    except: # catches everything for now, may want to handle surgigcal cases later
        e = sys.exc_info()[0]
        print("Oh oh, trouble getting tweets for a paper from the API:")
        print(e)
        return None

    # extract just what we need from tweets and not much more
    jtweets = [process_tweet(r) for r in results]
    # process the ban list
    jtweets = [t for t in jtweets if t['name'] not in banned]

    return jtweets

# -----------------------------------------------------------------------------

if __name__ == '__main__':

    # init tweets, attempt to warm start from existing data if any
    tweets = {}
    if os.path.isfile('tweets.json'):
        with open('tweets.json', 'r') as f:
            tweets = json.load(f)
        print(f"warm starting from existing tweets.json, found tweets for {len(tweets)} papers.")

    # init twitter api
    keys = get_api_keys()
    api = twitter.Api(consumer_key=keys[0],
                      consumer_secret=keys[1],
                      access_token_key=keys[2],
                      access_token_secret=keys[3],
                      tweet_mode='extended')

    # load a list of banned accounts
    banned = []
    if os.path.isfile('banned.txt'):
        with open('banned.txt', 'r') as f:
            banned = f.read().splitlines()

    def update(i, j):
        """ update the tweets for paper index i and json dict j """
        jtweets = get_tweets(j)
        if jtweets is not None:
            tweets[j['rel_doi']] = jtweets
            # update the database
            write_json(tweets, 'tweets.tmp.json')
            os.rename('tweets.tmp.json', 'tweets.json')
            print('processed index %d, found %d tweets for %s' % (i, len(jtweets), j['rel_link']))
        # rate limit is 180 calls per 5 minutes, or 1 call per 5 seconds. so sleep 10 for safety
        time.sleep(10)

    # run forever
    while True:

        # open the latest state of database
        with open('jall.json', 'r') as f:
            jall = json.load(f)

        """
        we want to update all papers in the database but we want to also prioritize
        the recent papers because they probably experience the most chatter and updates.
        so we work in chunks of e.g. 100 and iteratively fetch tweets for the next 100 old
        papers and then again 100 of the new papers, etc. This way we keep updating the new
        papers relatively frequently.
        """
        chunk_size = 100
        assert chunk_size < len(jall['rels'])
        for i1, j1 in enumerate(jall['rels']):
            if i1 > chunk_size and i1 % chunk_size == 0:
                for i2, j2 in enumerate(jall['rels'][:chunk_size]):
                    update(i2, j2)
            update(i1, j1)

        time.sleep(0.5) # safety pin
