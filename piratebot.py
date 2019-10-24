import time
import numpy as np

import arrr
import feedparser
import urllib
import tweepy

import credentials


consumer_key = credentials.CONSUMER_KEY
consumer_secret = credentials.CONSUMER_SECRET
access_token = credentials.ACCESS_TOKEN
access_secret = credentials.ACCESS_SECRET


def search_arXiv(search_query, start=0):

    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?';

    # Search parameters
    #start                     # retreive the first 5 results
    max_results = 1

    query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                         start,
                                                         max_results)

    # Opensearch metadata such as totalResults, startIndex, 
    # and itemsPerPage live in the opensearch namespase.
    # Some entry metadata lives in the arXiv namespace.
    # This is a hack to expose both of these namespaces in
    # feedparser v4.1
    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
    # perform a GET request using the base_url and query
    response = urllib.request.urlopen(base_url+query).read()

    # parse the response using feedparser
    feed = feedparser.parse(response)
    
    return feed


def pirate_title(search_query, start=0):
    feed = search_arXiv(search_query, start=start)
    entry = feed.entries[0]
    title = arrr.translate_title(entry.title)
    return title

#p = pirate_title('astro-ph', start=40000)
#print(p)

def tweet_title():

	interval = 30 #seconds, for testing

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)    
	auth.set_access_token(access_token, access_secret)
	api = tweepy.API(auth)

	while True:
		rand = np.random.randint(1000) #max ive gotten to work
		print(rand)
		pt = pirate_title("astro-ph", start=rand)
		print(pt)
		api.update_status(pt)
		time.sleep(interval)

if __name__ == "__main__":
    tweet_title()

