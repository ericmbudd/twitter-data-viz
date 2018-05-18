import tweepy
import yaml
import fileinput
import time
import sys
import time
import copy
import os
import logging
try:
    import ujson as json
except ImportError:
    import json

# get the profile you're gonna use to pull data
account = os.listdir("creds")[0].split(".")[0]
# store them in a dictionary of api handles
user_keys = yaml.load(open("creds/" + account + ".creds"))
authenticating_user = user_keys["username"]
auth = tweepy.OAuthHandler(user_keys["consumer_key"], user_keys["consumer_secret"])
auth.set_access_token(user_keys["token"], user_keys["secret"])
api_handle = tweepy.API(auth, retry_delay = 5)

# get the users we care about
influencers = []
for line in fileinput.FileInput("influencers.txt"):
    influencers.append(line.strip())

# set up our logging
# we want to be able to restart these API calls whenever we get cutoff,
# so log the state carefully
def setup_logger(logger_name, log_file, formatter):
    l = logging.getLogger(logger_name)
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    l.setLevel(logging.INFO)
    l.addHandler(fileHandler)

# log info
# setup a debugging/progress bar logger
log_messages_formatter = logging.Formatter('%(asctime)s | %(message)s')
setup_logger("general_info", "progress/setup_logging.txt", log_messages_formatter)
general_logger = logging.getLogger("general_info")

# write out one file of influencer handles per authenticating user that we have
influencer_handles = {}
for authenticating_user_creds in os.listdir("creds"):
    authenticating_user = authenticating_user_creds.split(".")[0]
    setup_logger("influencers_" + authenticating_user, "influencers/" + authenticating_user + ".txt", logging.Formatter('%(message)s'))
    influencer_handles[authenticating_user] = logging.getLogger("influencers_" + authenticating_user)

# now split the influencers into as many chunks as we have apps 
# chunck the influencers up into groups with roughly equal follower counts
# don't have more than a couple hundred or thousand influencers, please
influencers_followers_counts = []
for i in range(0,len(influencers),100):
    influencers_info = api_handle.lookup_users(screen_names = influencers[i:i+100])
    for influencer in influencers_info:
        influencers_followers_counts.append((influencer.screen_name, influencer.id_str, influencer.friends_count))

general_logger.info("You've got {} influencers with {} followers total".format(
    len(influencers),sum([x[2] for x in influencers_followers_counts])))

api_handles_to_influencers = {}
for creds in os.listdir("creds"):
    api_handles_to_influencers[creds.split(".")[0]] = {"influencers": [], "total_followers": 0}
for influencer in influencers_followers_counts:
    lowest_count = min(api_handles_to_influencers.items(), key = lambda x:x[1]["total_followers"])
    api_handles_to_influencers[lowest_count[0]]["influencers"].append(influencer[0])
    api_handles_to_influencers[lowest_count[0]]["total_followers"] += influencer[2]
    influencer_handles[lowest_count[0]].info(influencer[0])

for item in api_handles_to_influencers.items():
    general_logger.info(item)

