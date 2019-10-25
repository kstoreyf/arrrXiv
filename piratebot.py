import time
import numpy as np
from os import environ

import feedparser
import urllib
import tweepy
import re

import translatorrr

local = False
tweet_now = True


def get_api():
	if local:
		import credentials
		consumer_key = credentials.CONSUMER_KEY
		consumer_secret = credentials.CONSUMER_SECRET
		access_token = credentials.ACCESS_TOKEN
		access_secret = credentials.ACCESS_SECRET
	else:
		consumer_key = environ['CONSUMER_KEY']
		consumer_secret = environ['CONSUMER_SECRET']
		access_token = environ['ACCESS_TOKEN']
		access_secret = environ['ACCESS_SECRET']

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
	return api


def search_arXiv(search_query, start=0):

	# Base api query url
	base_url = 'http://export.arxiv.org/api/query?';

	# Search parameters
	#start					   # retreive the first 5 results
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
	title = translatorrr.translate_title(entry.title)
	for link in entry.links:
		if link.rel == 'alternate':
			mylink = link.href
	return title, mylink

#p = pirate_title('astro-ph', start=40000)
#print(p)

def tweet_title():
	print("Tweeting random title")
	rand = np.random.randint(10000) #max ive gotten to work
	print(rand)
	pt, pl = pirate_title("cat:astro-ph&sortBy=lastUpdatedDate&sortOrder=descending", start=rand)
	mytweet = pt + '\n' + pl
	print(mytweet)
	if tweet_now:
		api.update_status(mytweet)


def check_mentions(api, keywords, since_id):
	print("Retrieving mentions")

	new_since_id = since_id
	for tweet in tweepy.Cursor(api.mentions_timeline,
		since_id=since_id).items():
		new_since_id = max(tweet.id, new_since_id)
		pattern_new = re.compile("[0-9]{4}.[0-9]{5}")
		pattern_old = re.compile("astro-ph/[0-9]{7}")
		
		found = False
		paperidx = None
		for word in tweet.text.split():
			if pattern_new.match(word):
				paperidx = word[:10]
			elif pattern_old.match(word):
				paperidx = word[:16]
			if paperidx:
				try:
					pt, pl = pirate_title(paperidx)
					mytweet = pt + '\n' + pl
					found = True
					break
				except IndexError:
					pass
		
		handle = tweet.user.screen_name
		piratename = translatorrr.pirate_person()
		#if not quote:
		if tweet_now:
			if not found:
				status = f"@{handle} Aarrrgh! I couldn't find that swashbuckling paperrr."
				print(status)
				api.update_status(
					status=status,
					in_reply_to_status_id=tweet.id,
				)
			else:
				status = f"Paperrr for the landlubber @{handle}: {mytweet} \n https://twitter.com/{handle}/status/{tweet.id}"
				print(status)
				api.update_status(
					status=status
				)
		np.savetxt('since_id.dat', new_since_id)
	return new_since_id



def main():
	
	interval = 30 # seconds

	api = get_api()
	since_id = int(np.loadtxt('since_id.dat'))
	prev = time.time()
	while True:
		since_id = check_mentions(api, ["arrr"], since_id)
		
		now = time.time()
		if (prev - now > interval):
			tweet_title()
			prev = now
		
		print("Waiting...")
		time.sleep(10)

		

if __name__ == "__main__":
	main()

