# Copyright (c) 2014 Brendan McCarthy

import os
import webapp2
import ConfigParser
import jinja2
import string
import tweepy
import logging
import urllib
import re

from tweepy import *

JINJA_ENVIRONMENT = jinja2.Environment(
	loader     = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = False)

def tweet(status):
	config = ConfigParser.RawConfigParser()
	config.read('settings.cfg')
	
	# http://dev.twitter.com/apps/myappid
	CONSUMER_KEY = config.get('API Information', 'CONSUMER_KEY')
	CONSUMER_SECRET = config.get('API Information', 'CONSUMER_SECRET')
	# http://dev.twitter.com/apps/myappid/my_token
	ACCESS_TOKEN_KEY = config.get('API Information', 'ACCESS_TOKEN_KEY')
	ACCESS_TOKEN_SECRET = config.get('API Information', 'ACCESS_TOKEN_SECRET')

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)
	result = api.update_status(status)

class MainHandler(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render())

class sendTweet(webapp2.RequestHandler):
	def post(self):
		site_ = urllib.urlopen("http://www.quotecorn.com/")
		site = site_.read()
		site_.close()

		price = re.findall(r"<strong>.+<\/strong>", site)
		updated = re.findall(r"<span class=\"style15\">Corn Quote Updated.+<\/span>", site)

		price = price[0]
		updated = updated[0]

		price = string.split(price, " ")[1]
		updated = string.lstrip(updated, "<span class=\"style15\">Corn Quote Updated ")
		updated = string.rstrip(updated, "</span>")

		logging.info(price)
		logging.info(updated)

		try:
			tweet(price + " cents as of " + updated)
		except TweepError as te:
			logging.info(te)

		self.redirect("/")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/tweet', sendTweet),
], debug=True)
