import ujson as json
import pandas as pd
import os
import fileinput

followers_df = pd.DataFrame(columns = ["user"])
for followers_file in os.listdir("followers"):
    influencer = followers_file.split(".")[0]
    followers_list = []
    for line in fileinput.FileInput("followers/" + followers_file):
        if "_" not in line:
            followers_list.append(line.strip())
    df = pd.DataFrame(list(set(followers_list)),columns = ["user"])
    df[influencer] = 1
    followers_df = followers_df.merge(df,how = "outer",on = "user").fillna(0)

friends_list = []
for line in fileinput.FileInput("friends/ericmbudd.txt"):
    friends_list.append(line.strip())
friends_df = pd.DataFrame(list(set(friends_list)),columns = ["user"])
friends_df["ericmbudd_follows"] = 1

followers_df = followers_df.merge(friends_df,how = "outer",on = "user").fillna(0)

def get_relevant_fields(follower_string):
    follower = json.loads(follower_string)
    relevant = {}
    relevant["id"] = follower["id_str"] 
    relevant["screen_name"] = follower["screen_name"]
    relevant["location"] = follower["location"] 
    try:
        relevant["time_of_last_tweet"] = follower["status"]["created_at"]
    except KeyError:
        pass
    relevant["display_name"] = follower["name"].replace("\n"," ").replace("\t"," ").replace(","," ")
    relevant["bio"] = follower["description"].replace("\n"," ").replace("\t"," ").replace(","," ")
    relevant["account_created_at"] = follower["created_at"]
    relevant["number_of_followers"] = follower["followers_count"] 
    relevant["number_following"] = follower["friends_count"]
    relevant["is_egg"] = follower["default_profile_image"]
    relevant["number_of_tweets"] = follower["statuses_count"]
    return relevant

is_first = True
for followers_file in os.listdir("followers_userinfo/"):
    influencer = followers_file.split(".")[0]
    list_of_followers = []
    for line in fileinput.FileInput("followers_userinfo/" + followers_file):
        list_of_followers.append(get_relevant_fields(line))
    # make it all a dataframe
    df = pd.DataFrame(list_of_followers)
    if df.shape != (0,0):
        df = df.drop_duplicates(subset = ["id"])
        if is_first:
            followers_info_df = df
            is_first = False
        else:
            followers_info_df = followers_info_df.append(df)
            followers_info_df = followers_info_df.drop_duplicates(subset = ["id"])

giant_followers_df = followers_df.merge(followers_info_df, left_on = "user", right_on = "id", how = "left")
giant_followers_df.to_csv("giant_csv_of_followers.csv", index = False)
