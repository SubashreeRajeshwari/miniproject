from flask import Flask, request
from flask_cors import CORS
import requests
import json

from webbrowser import Chrome
from instagramy import InstagramUser, InstagramPost
import instascrape as ins
from instagramy.plugins.analysis import analyze_users_popularity
import pandas as pd
import string as str
import numpy as np
import os
from datetime import datetime, date

app = Flask(__name__)
CORS(app)

@app.route("/search", methods=['POST'])
def get():
    links = request.json
    links = list(links.values())
    insta_links = links[0]
    print(insta_links)
    c = instascrape(insta_links)
    result = analysis(c)
    return result

def instascrape (URL):
    webdriver = Chrome("path/to/chromedriver.exe")

    session_id = "5537012007%3A90DDzSinjCOTzn%3A0"

    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    name = []
    fb_page = []
    follower_count = []
    following_count = []
    post_count = []
    bus_acc = []
    reel ,ur= [],[]
    like1, comment1, date1 = [], [], []
    like2, comment2, date2 = [], [], []
    like3, comment3, date3 = [], [], []
    like4, comment4, date4 = [], [], []
    like5, comment5, date5 = [], [], []

    webdriver = Chrome("path/to/chromedriver.exe")
    #URL = ["https://www.instagram.com/marvelstudios/", "https://www.instagram.com/pinkvilla/","https://www.instagram.com/virat.kohli/","https://www.instagram.com/kareenakapoorkhan", "https://www.instagram.com/mkstalin"]

    for u in URL:
        result = requests.get(u)
        ur.append(u)
        user_stripleft = remove_prefix(u, "https://www.instagram.com/")
        user_name = user_stripleft.strip('/')
        print(user_name)
        name.append(user_name)

        user = InstagramUser(user_name, sessionid=session_id)
        '''hd = user.posts[0][12]
        hd.'''

        fb_page.append(user.connected_fb_page)
        follower_count.append(user.number_of_followers)
        following_count.append(user.number_of_followings)
        post_count.append(user.number_of_posts)
        bus = user.other_info
        like1.append(user.posts[0][0])
        like2.append(user.posts[1][0])
        like3.append(user.posts[2][0])
        like4.append(user.posts[3][0])
        like5.append(user.posts[4][0])

        date1.append(user.posts[0].taken_at_timestamp)
        date2.append(user.posts[1].taken_at_timestamp)
        date3.append(user.posts[2].taken_at_timestamp)
        date4.append(user.posts[3].taken_at_timestamp)
        date5.append(user.posts[4].taken_at_timestamp)

        comment1.append(user.posts[0][1])
        comment2.append(user.posts[1][1])
        comment3.append(user.posts[2][1])
        comment4.append(user.posts[3][1])
        comment5.append(user.posts[4][1])

        bus_acc.append(bus["is_business_account"])
        reel.append(bus["highlight_reel_count"])

    df = pd.DataFrame({
        "Account_name": name,
        'FB_page': fb_page,
        "Followers": follower_count,
        "Following": following_count,
        "Posts": post_count,
        "Like1": like1,
        "Like2": like2,
        "Like3": like3,
        "Like4": like4,
        "Like5": like5,
        "Date1": date1,
        "Date2": date2,
        "Date3": date3,
        "Date4": date4,
        "Date5": date5,
        "Comment1": comment1,
        "Comment2": comment2,
        "Comment3": comment3,
        "Comment4": comment4,
        "Comment5": comment5,
        "Business account": bus_acc,
        "Reel Count": reel,
        "Profile URL": ur,

    })
    df.to_csv('insta_2.csv')
    c = "/Users/Dell/insta_2.csv"
    return c

def analysis(csvlink):
        # reading the csv file
        # creating a tuple by calulating the values
        print("Scrapping done")
        data = pd.read_csv("C:/Users/Dell/insta_2.csv",
                           parse_dates=['Date1', 'Date2', 'Date3', 'Date4', 'Date5'])
        selected_columns = data["Account_name"], (data["Followers"]) * 0.416422, ((data["Comment1"] / data["Like1"] +
                                                                                   data["Comment2"] / data["Like2"] +
                                                                                   data["Comment3"] / data["Like3"] +
                                                                                   data["Comment4"] / data["Like4"] +
                                                                                   data["Comment5"] / data[
                                                                                       "Like5"]) * 20) * 0.033085, data[
                               "Like1"], data["Like2"], data["Like3"], data["Like4"], data["Like5"], (100 - ((abs(
            data["Like1"] - data["Like2"]) / data[["Like1", "Like2"]].mean(axis=1) + abs(
            data["Like2"] - data["Like3"]) / data[["Like2", "Like3"]].mean(axis=1) + abs(
            data["Like3"] - data["Like4"]) / data[["Like3", "Like4"]].mean(axis=1) + abs(
            data["Like4"] - data["Like5"]) / data[["Like4", "Like5"]].mean(axis=1)) / 4)) * 0.138016, data["Date1"], \
                           data["Date2"], data["Date3"], data["Date4"], data["Date5"], (((abs(
            data["Date1"] - data["Date2"]) + abs(data["Date2"] - data["Date3"]) + abs(
            data["Date3"] - data["Date4"]) + abs(data["Date4"] - data["Date5"])) / 4).dt.days.astype(
            'int16')) * 0.008955, (((
                    data["Comment1"] + data["Like1"] + data["Comment2"] + data["Like2"] + data["Comment3"] + data[
                "Like3"] + data["Comment4"] + data["Like4"] + data["Comment5"] + data["Like5"])) / (
                                               5 / 100 * data["Followers"] * data["Posts"])) * 0.073074, (
                                       100 - (data["Following"] / data["Followers"]) * 100) * 0.032678
        # creating a transpose of the tuple and copying the tuple into a new dataframe called df
        df = pd.DataFrame(selected_columns).transpose()
        # Naming the columns of the dataframe
        df.columns = ['Account_name', 'Followers', 'LCratio', 'Like1', 'Like2', 'Like3', 'Like4', 'Like5', 'LikeSpread',
                      'Date1', 'Date2', 'Date3', 'Date4', 'Date5', 'PostingFrequency', 'EngagementRatio',
                      'Authenticity']
        # converting the required column in dataframe to numeric values
        df[['Followers', 'LCratio', 'Like1', 'Like2', 'Like3', 'Like4', 'Like5', 'LikeSpread', 'PostingFrequency',
            'EngagementRatio', 'Authenticity']] = df[
            ['Followers', 'LCratio', 'Like1', 'Like2', 'Like3', 'Like4', 'Like5', 'LikeSpread', 'PostingFrequency',
             'EngagementRatio', 'Authenticity']].apply(pd.to_numeric)
        # converting the dates in dataframe to datetime
        df[['Date1', 'Date2', 'Date3', 'Date4', 'Date5']] = df[['Date1', 'Date2', 'Date3', 'Date4', 'Date5']].apply(
            pd.to_datetime)
        # converting the dates in dataframe to date
        df['Date1'] = df['Date1'].dt.date
        df['Date2'] = df['Date2'].dt.date
        df['Date3'] = df['Date3'].dt.date
        df['Date4'] = df['Date4'].dt.date
        df['Date5'] = df['Date5'].dt.date
        # Calcuating overall points and creating a rank column for the df
        df[
            'Overall_points'] = df.Followers + df.LCratio + df.LikeSpread - df.PostingFrequency + df.EngagementRatio + df.Authenticity
        df['rank'] = df['Overall_points'].rank(ascending=0)
        # Creating attributes for json return value
        sts = 'Success'
        best_profile = df[df["rank"] == 1].Account_name
        # Converting single values to dictonary
        tf = len(df.index)
        status = {}
        status = {1: sts}

        best_profile = best_profile.to_dict()
        total_profiles = {}
        total_profiles = {1: tf}

        # setting account name as index
        df = df.set_index("Account_name")

        # Creating attributes for graph values
        followers_count = df[["Followers"]]
        engagement_ratio = df[["EngagementRatio"]]
        overall_points = df[["Overall_points"]]

        # Converting dataframes to dictonary
        followers_count = followers_count.to_dict()
        engagement_ratio = engagement_ratio.to_dict()
        overall_points = overall_points.to_dict()

        # Converting datatime  to strings
        df[['Date1', 'Date2', 'Date3', 'Date4', 'Date5']] = df[['Date1', 'Date2', 'Date3', 'Date4', 'Date5']].astype(
            str)

        # Transposing dataframe to copy remaining three graph values
        df = df.transpose()
        like_spread = df.loc[['Like1', 'Like2', 'Like3', 'Like4', 'Like5']]
        post_frequency = df.loc[['Date1', 'Date2', 'Date3', 'Date4', 'Date5']]
        key_points = df.loc[
            ['Followers', 'LCratio', 'LikeSpread', 'PostingFrequency', 'EngagementRatio', 'Authenticity']]

        # Converting dataframes to dictonary
        like_spread = like_spread.to_dict()
        post_frequency = post_frequency.to_dict()
        key_points = key_points.to_dict()

        # Adding all the values to be returned in a list
        OutList = []
        OutList.extend(
            [{'status': status}, {'best_profile': best_profile}, {'total_profiles': total_profiles}, followers_count,
             engagement_ratio, overall_points, {'like_spread': like_spread}, {'post_frequency': post_frequency},
             {'key_points': key_points}])

        # Converting list to dictonary
        di = {}
        for i in OutList:
            di.update(i)

        # returning the necessary json for graph
        return json.dumps(di, indent=120)


#URL = ["https://www.instagram.com/marvelstudios/", "https://www.instagram.com/pinkvilla/","https://www.instagram.com/theguindytimes/","https://www.instagram.com/drrenitarajan/","https://www.instagram.com/suitcase_full_of_sparks/"]

if __name__ == '__main__':
    app.run()