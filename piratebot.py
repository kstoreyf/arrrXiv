import time
import numpy as np
from os import environ

import feedparser
import urllib
import tweepy
import re
import schedule

import translatorrr

local = False
tweet_now = True
#local = True
#tweet_now = False

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

def tweet_title(api):
	print("Time: {}, Tweeting random title".format(time.ctime()))
	mytweet = None
	for i in range(5):
		rand = np.random.randint(10000) #max ive gotten to work
		print(rand)
		try:
			pt, pl = pirate_title("cat:astro-ph&sortBy=lastUpdatedDate&sortOrder=descending", start=rand)
			mytweet = pt + '\n' + pl
			print(mytweet)
			break
		except IndexError:
			pass
	if not mytweet:
		raise ValueError("Scallywags! Bad paper search!")
	
	if tweet_now:
		api.update_status(mytweet)


def check_mentions(api, since_id):
	print("Retrieving mentions")
	print(since_id)
	new_since_id = since_id
	#print(tweepy.Cursor(api.mentions_timeline,
    #    since_id=since_id))

	for tweet in tweepy.Cursor(api.mentions_timeline,
		since_id=since_id).items():
		print('tweetid:',tweet.id)
		print('sinceid:',since_id)
		print('---')
		new_since_id = max(tweet.id, new_since_id)
		print('new:',new_since_id)
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

		
		print('reply:', tweet.in_reply_to_status_id )
		reply = True
		if tweet.in_reply_to_status_id is not None:
			print('dont reply')
			reply = False 
		
		handle = tweet.user.screen_name
		piratename = translatorrr.pirate_person()
		#if not quote:
		if not found and reply:
			status = f"@{handle} Aarrrgh! I couldn't find that swashbuckling paperrr."
			print(status)
			if tweet_now:
				api.update_status(
					status=status,
					in_reply_to_status_id=tweet.id,
				)
		if found and reply:
			status = f"Paperrr for the {piratename} @{handle}: {mytweet} \n https://twitter.com/{handle}/status/{tweet.id}"
			print(status)
			if tweet_now:
				api.update_status(
					status=status
				)
		new_since_id += 1
		#np.savetxt('since_id.dat', [int(new_since_id)], fmt='%d')
		#print('file:',int(np.loadtxt('since_id.dat')))
	return new_since_id


def get_since_id(api):
	tweets = api.user_timeline()
	ids = [tweet.id for tweet in tweets]
	since_id = max(ids)+1
	return since_id

def main():
	
	interval = 60*60*6 # seconds

	api = get_api()
	#since_id = int(np.loadtxt('since_id.dat', dtype=int))
	since_id = get_since_id(api)
	print("most recent id", since_id)
	prev = time.time()

	# schedule jobs
	tweet_times = ['01:03']	
	for tt in tweet_times:
		schedule.every().day.at(tt).do(tweet_title, api)
	# start off with a title
	#tweet_title(api)
	
	print(interval)
	while True:
		since_id = check_mentions(api, since_id)
		print("times")
		print(prev)
		now = time.time()
		print(now)
		print(now-prev)
		#if (now - prev > interval):
	    #	tweet_title(api)
		#	prev = now
		
		schedule.run_pending()
		print("Waiting...")
		time.sleep(10)

		

if __name__ == "__main__":
	main()

