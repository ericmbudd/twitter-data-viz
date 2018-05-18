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

# get the users we care about
influencers = []
for line in fileinput.FileInput("influencers/" + account + ".txt"):
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
log_messages_formatter = logging.Formatter('%(asctime)s | {} | %(message)s'.format(authenticating_user))
setup_logger("general_info", "progress/{}.txt".format(authenticating_user), log_messages_formatter)
general_logger = logging.getLogger("general_info")

# log every next token we get, so that we can always pickup where we left off
setup_logger("next_tokens_" + authenticating_user, "next_tokens/" + authenticating_user + ".txt", log_messages_formatter)
next_token_logger = logging.getLogger("next_tokens_" + authenticating_user)

# log every graph edge we pull down *in the order that we pull them down*
# one file of followers per influencer
followers_ids_formatter = logging.Formatter('[ %(asctime)s ]\n%(message)s')
followers_ids_loggers = {}
for influencer in influencers:
    setup_logger("followers_" + influencer, "followers/" + influencer + ".txt", followers_ids_formatter)
    followers_ids_loggers[influencer] = logging.getLogger("followers_" + influencer)

# and finally, a file of user information per follower 
# (because we want to check how many followers these people have)
data_formatter = logging.Formatter('%(message)s')
followers_info_loggers = {}
for influencer in influencers:
    setup_logger("followers_userinfo_" + influencer, "followers_userinfo/" + influencer + ".txt", data_formatter)
    followers_info_loggers[influencer] = logging.getLogger("followers_userinfo_" + influencer)

# method to take a list of stringified user ids and turn them into a list of lists of >=100 ids
def chunk_ids(ids_list):
    strings = []
    for i in range(0, len(ids_list), 100):
        strings.append(ids_list[i:i + 100])
    return strings

# write some logging
general_logger.info("About to pull follower data for followers of {} influencer accounts.".format(len(influencers)))
general_logger.info("Influencers: {}".format(",".join(influencers)))

# start at the place we left off at--check the next_tokens file to get the appropriate influencer
# and the right next token
# get the last line of the appropriate next_tokens file
# (actually, let's backup one and get the second to last line. we'll probably write out some dupes, but that's okay)
second_to_last_line = ""
last_line = ""
for line in fileinput.FileInput("next_tokens/" + authenticating_user + ".txt"):
    second_to_last_line = last_line
    last_line = line
if second_to_last_line != "":
    last_next_token = second_to_last_line.split("|")[-1].split(",")[0].strip()
    last_influencer = second_to_last_line.split("|")[-1].split(",")[1].strip()
    index_last_influencer = influencers.index(last_influencer)
    general_logger.info("About to pull follower information for the remaining users")
    general_logger.info("The remaining {} users are: {}".format(len(influencers[index_last_influencer:]),
        influencers[index_last_influencer:]))
else:
    last_next_token = -1
    index_last_influencer = 0
if last_next_token == 0:
    last_next_token = -1

# write out followers of the handle
for influencer in influencers[index_last_influencer:]:
    next_cursor = last_next_token
    last_next_token = -1
    while next_cursor != 0:
        try:
            # get the followers
            general_logger.info("Getting followers, next token is {}".format(next_cursor))
            friend_list = api_handle.friends_ids(
                    influencer, 
                    cursor = next_cursor, 
                    count = 5000, 
                    stringify_ids = True
                )
            next_cursor = friend_list[1][1]
            next_token_logger.info("{}, {}".format(next_cursor, influencer))
            followers_ids_loggers[influencer].info("\n".join(friend_list[0]))
            
            general_logger.info("Got {} followers of {}".format(len(friend_list[0]), influencer))
            
            api_status = api_handle.rate_limit_status()
            user_lookup_status = api_status["resources"]["users"]["/users/lookup"]
            user_lookups_remaining = user_lookup_status["remaining"]
            
            general_logger.info(api_status["resources"]["followers"]["/followers/ids"])
            general_logger.info(user_lookup_status)

            if user_lookups_remaining <= int(len(friend_list[0])/100) + 1:
                sleep_time = max(0,int(user_lookup_status["reset"] - time.time())) + 60
                general_logger.info("We don't have enough user lookups left, so we're gonna sleep for {} min".format(sleep_time/60))
                time.sleep(sleep_time)
                api_status = api_handle.rate_limit_status()
                general_logger.info("Took a nap. New status is {}".format(api_status["resources"]["followers"]["/followers/ids"]))
                general_logger.info("Took a nap. New status is {}".format(api_status["resources"]["users"]["/users/lookup"]))

            general_logger.info("Now getting user information for {} users".format(len(friend_list[0])))
            for user_id_group in chunk_ids(friend_list[0]):
                # get the user information for each of these followers
                # I'm allowed make 900 requests per window and 100 users per request,
                # so this step shouldn't really be the limiting factor
                # (that's why I decided not to dedupe the followers first)
                user_information = api_handle.lookup_users(user_ids = user_id_group)
                for user in user_information:
                    #user_info_dict = {"bio": user.description,
                    #    "followers": user.followers_count,
                    #    "following": user.friends_count,
                    #    "tweets_count": user.statuses_count,
                    #    "id": user.id_str,
                    #    "name": user.name,
                    #    "screen_name": user.screen_name,
                    #    "created_at": user.created_at}
                    # add the user-entered location
                    followers_info_loggers[influencer].info(json.dumps(user._json))#json.dumps(user_info_dict))
        
        except tweepy.error.RateLimitError:
            # I want to check how much time we spend sleeping
            api_status = api_handle.rate_limit_status()
            general_logger.info("Ran into a rate limit at the token {}".format(next_cursor))
            general_logger.info("Follower endpoint status is {}".format(api_status["resources"]["followers"]["/followers/ids"]))
            general_logger.info("User lookup endpoint status is {}".format(api_status["resources"]["users"]["/users/lookup"]))
            reset_time = api_status["resources"]["followers"]["/followers/ids"]["reset"]
            sleep_time = max(0,int(reset_time - time.time())) + 61 # add an extra min to prevent errors
            general_logger.info("Sleeping for {} minutes".format(sleep_time/60))
            time.sleep(sleep_time)
        except tweepy.error.TweepError:
            general_logger.info("Can't get the followers of this account {}".format(influencer))
            next_cursor = 0

general_logger.info("Finished successfully!! WOOOHOOOOOOOOO!!!!!")
