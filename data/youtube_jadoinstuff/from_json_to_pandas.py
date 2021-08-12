import json
from os import replace
import pandas as pd
import re
from datetime import datetime, timedelta
import cv2
import urllib
import numpy as np
from skimage import io
import matplotlib.pyplot as plt

#C:/Users/merre/Desktop/data projects/
files= ["shanieology.json","simau.json","soundslikepizza.json","azerrz.json","BigShade.json","black_gryph0n.json"
,"brian_hull.json","brizzy_voices.json","brock_baker.json","charlie_hopkinson.json","danny_padilla_&_mason_sperling.json"
,"ja_doin_stuff.json","joshiiwuh.json","knep.json","ori.json","redfireball555.json","scheiffer_bates.json","daniel_ferguson.json",
"BigShade.json","best_in_class.json","maxamili.json","mikey_bolts.json"]

data=None
df_channel_new=None
df_channel = None

for file in files:
    with open(file,'r') as f:
        data = json.load(f)

    channel_id, stats = data.popitem()
    channel_stats=stats["channel_statistics"]
    video_stats = stats["video_data"]
    channel_views= channel_stats["viewCount"]
    channel_subs= channel_stats["subscriberCount"]
    channel_videos= channel_stats["videoCount"]
    try:
        sorted_vids = sorted(video_stats.items(), key=lambda item: int(item[1]["viewCount"]), reverse=True)
    except:
        sorted_vids = video_stats.items()
    stats = []
    for vid in sorted_vids:
        video_id = vid[0]
        title = vid[1]["title"]
        title_len = len(title)
        title_words = re.findall(r'\w+',title)
        words=0
        upper_words=0
        for word in title_words:
            words += 1
            if word.isupper():
                upper_words += 1
        upper_pct = upper_words/words
        
        emoji_count = len(re.findall(u'[\U0001f600-\U0001f650]', title))
        
        #Convert time to Mexico City Time
        upload_date_time = datetime.strptime(vid[1]["publishedAt"],'%Y-%m-%dT%H:%M:%SZ')-timedelta(hours=5)
        upload_date = upload_date_time.date()
        upload_time = upload_date_time.time()
        #0 is Monday, 6 is Sunday
        upload_day = upload_date.weekday()
        if datetime.strptime('04:00:00', '%H:%M:%S').time() <= upload_time <= datetime.strptime('10:30:00', '%H:%M:%S').time():
            upload_time_of_day = 'morning'
        elif datetime.strptime('10:30:01', '%H:%M:%S').time() <= upload_time <= datetime.strptime('18:00:00', '%H:%M:%S').time():
            upload_time_of_day = 'afternoon'
        elif datetime.strptime('18:00:01', '%H:%M:%S').time() <= upload_time <= datetime.strptime('23:00:00', '%H:%M:%S').time():
            upload_time_of_day = 'night'
        else:
            upload_time_of_day = "late_night"
        try:
            thumbnail_url = vid[1]["thumbnails"]["maxres"]["url"]
            thumbnail_h = vid[1]["thumbnails"]["maxres"]["height"]
            thumbnail_w = vid[1]["thumbnails"]["maxres"]["width"]
        except:
            try:
                thumbnail_url = vid[1]["thumbnails"]["high"]["url"]
                thumbnail_h = vid[1]["thumbnails"]["high"]["height"]
                thumbnail_w = vid[1]["thumbnails"]["high"]["width"]
            except:
                try:
                    thumbnail_url = vid[1]["thumbnails"]["default"]["url"]
                    thumbnail_h = vid[1]["thumbnails"]["default"]["height"]
                    thumbnail_w = vid[1]["thumbnails"]["default"]["width"]  
                except:
                    thumbnail_url=None
                    thumbnail_h=None
                    thumbnail_w=None                  
        try:
            channel = vid[1]["channelTitle"]
        except:
            channel=None
        try:
            tags = vid[1]["tags"]
        except:
            tag = None
        num_tags = len(tags)
        try:
            categoryId = vid[1]["categoryId"]
        except:
            categoryId=None
        try: 
            liveBroadcastContent = vid[1]["liveBroadcastContent"]
        except:
            liveBroadcastContent = None
        try:
            defaultAudioLanguage = vid[1]["defaultAudioLanguage"]
        except:
            defaultAudioLanguage = None
        try:
            viewCount = vid[1]["viewCount"]
        except:
            viewCount = None
        try:
            likeCount = vid[1]["likeCount"]
        except:
            likeCount =None
        try:
            dislikeCount = vid[1]["dislikeCount"]
        except:
            dislikeCount=None
        try:
            favoriteCount = vid[1]["favoriteCount"]
        except:
            favoriteCount = None
        try:
            commentCount = vid[1]["commentCount"]
        except:
            commentCount=None
        
        try:
            duration0 = vid[1]["duration"]
        except:
            duration0=None
        try:
            hours = int(re.findall(r'\d+H',duration0)[0].replace('H',''))
        except:
            hours = None
        try:
            mins = int(re.findall(r'\d+M',duration0)[0].replace('M',''))
        except:
            mins=None
        try:
            secs = int(re.findall(r'\d+S',duration0)[0].replace('S',''))
        except:
            secs=0
        if hours is not None and mins is not None and secs is not None:
            duration = hours*60 + mins + secs/60
        elif mins is not None and secs is not None:
            duration = mins + secs/60
        elif secs is not None:
            duration = secs/60

        try:
            definition = vid[1]["definition"]
        except:
            definition =None
        try:
            captions = vid[1]["caption"]
        except:
            captions = None
        try:    
            licensedContent = vid[1]["licensedContent"]
        except:
            licensedContent=None
        try:
            projection = vid[1]["projection"]
        except:
            projection = None
        try:
            topicCategories = vid[1]["topicCategories"]
        except:
            topicCategories = None
        try:
            desc = vid[1]["description"]
        except:
            desc = None

        video_id = vid[0]
        stats.append([video_id,title,title_len,words,upper_pct,emoji_count,upload_date,upload_time,upload_day,upload_time_of_day,viewCount,likeCount,dislikeCount,favoriteCount,
        commentCount,duration,definition,captions,licensedContent,thumbnail_url, thumbnail_w, thumbnail_h, tags,num_tags,categoryId,liveBroadcastContent,
        defaultAudioLanguage,topicCategories, channel, channel_subs, channel_views, channel_videos,desc])
    df = pd.DataFrame(stats)
    df.columns = ['video_id','title','title_len','words','upper_pct','emoji_count','upload_date','upload_time','upload_day','upload_time_of_day','viewCount','likeCount','dislikeCount',
    'favoriteCount','commentCount','duration','definition','caption','licensedContent','thumbnail_url', 'thumbnail_w', 'thumbnail_h', 'tags','num_tags',
    'categoryId','liveBroadcastContent','defaultAudioLanguage','topicCategories', 'channel', 'channel_subs', 'channel_views', 'channel_videos','desc']
    df.to_csv(file.replace('json','txt'))

