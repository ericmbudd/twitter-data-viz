import tweepy
import yaml
import fileinput
import time
import sys
import time
import logging
try:
    import ujson as json
except ImportError:
    import json

# the account that we're using to pull this data is
account = sys.argv[1]

# get your creds for each profile you're gonna use to pull data
# store them in a dictionary of api handles
user_keys = yaml.load(open("creds/" + account + ".creds"))
authenticating_user = user_keys["username"]
auth = tweepy.OAuthHandler(user_keys["consumer_key"], user_keys["consumer_secret"])
auth.set_access_token(user_keys["token"], user_keys["secret"])
api_handle = tweepy.API(auth, retry_delay = 5)

# get our "influencer"
influencer = "ericmbudd"

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
log_messages_formatter = logging.Formatter('%(asctime)s | {} | %(message)s'.format(authenticating_user))
setup_logger("general_info", "progress/get_erics_friends.txt".format(authenticating_user), log_messages_formatter)
general_logger = logging.getLogger("general_info")

# log every graph edge we pull down *in the order that we pull them down*
# one file of friends per influencer
friends_ids_formatter = logging.Formatter('[ %(asctime)s ]\n%(message)s')
setup_logger("friends_" + influencer, "friends/" + influencer + ".txt", friends_ids_formatter)
friends_logger = logging.getLogger("friends_" + influencer)

# write some logging
general_logger.info("About to pull data for friends of {} influencer accounts.".format(influencer))


# write out friends of the handle
next_cursor = -1
while next_cursor != 0:
    try:
        # get the friends
        general_logger.info("Getting friends, next token is {}".format(next_cursor))
        friend_list = api_handle.friends_ids(
                influencer, 
                cursor = next_cursor, 
                count = 5000, 
                stringify_ids = True
            )
        next_cursor = friend_list[1][1]
        friends_logger.info("\n".join(friend_list[0]))
        
        general_logger.info("Got {} friends of {}".format(len(friend_list[0]), influencer))
        
    except tweepy.error.RateLimitError:
        general_logger.info("Ran into a rate limit at the token {}".format(next_cursor))
        general_logger.info("Sleeping for 15 minutes")
        time.sleep(15*60)

general_logger.info("Finished successfully!! WOOOHOOOOOOOOO!!!!!")
