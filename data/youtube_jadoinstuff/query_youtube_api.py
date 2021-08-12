import json
import requests
from numpy import random
from time import sleep
import os

class YTstats:

    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel_statistics = None
        self.video_data = None

    def extract_all(self):
        self.get_channel_statistics()
        self.get_channel_video_data()

    def get_channel_statistics(self):
        """Extract the channel statistics"""
        print('get channel statistics...')
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'
        
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        try:
            data = data['items'][0]['statistics']
        except KeyError:
            print('Could not get channel statistics')
            data = {}

        self.channel_statistics = data
        return data

    def get_channel_video_data(self):
        global s
        s = requests.Session()
        "Extract all video information of the channel"
        print('get video data...')
        channel_videos, channel_playlists = self._get_channel_content(limit=50)

        parts=["snippet", "statistics","contentDetails", "topicDetails"]
        print(len(channel_videos))
        ii = 0
       
        for video_id in channel_videos:
            ii += 1
            print(ii/len(channel_videos))
            for part in parts:
                data = self._get_single_video_data(video_id, part)
                channel_videos[video_id].update(data)


        self.video_data = channel_videos
        return channel_videos

    def _get_single_video_data(self, video_id, part):
        """
        Extract further information for a single video
        parts can be: 'snippet', 'statistics', 'contentDetails', 'topicDetails'
        """
        sleep(random.uniform(1, 3)/2)
        url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}"
        json_url = s.get(url)
        data = json.loads(json_url.text)
        print(url)
    
        try:
            data = data['items'][0][part]
        except KeyError as e:
            print(f'Error! Could not get {part} part of data: \n{data}')
            data = dict()
        return data

    def _get_channel_content(self, limit=None, check_all_pages=True):
        """
        Extract all videos and playlists, can check all available search pages
        channel_videos = videoId: title, publishedAt
        channel_playlists = playlistId: title, publishedAt
        return channel_videos, channel_playlists
        """
        url = f"https://www.googleapis.com/youtube/v3/search?key={self.api_key}&channelId={self.channel_id}&part=snippet,id&order=date"
        if limit is not None and isinstance(limit, int):
            url += "&maxResults=" + str(limit)

        vid, pl, npt = self._get_channel_content_per_page(url)
        idx = 0
        
        while(check_all_pages and npt is not None and idx < 50 and num_pages < 2):
            nexturl = url + "&pageToken=" + npt
            next_vid, next_pl, npt = self._get_channel_content_per_page(nexturl)
            vid.update(next_vid)
            pl.update(next_pl)
            idx += 1
            print(check_all_pages, idx, npt)

        return vid, pl

    def _get_channel_content_per_page(self, url):
        """
        Extract all videos and playlists per page
        return channel_videos, channel_playlists, nextPageToken
        """
        sleep(random.uniform(1, 3))
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        channel_videos = dict()
        channel_playlists = dict()
        if 'items' not in data:
            print('Error! Could not get correct channel data!\n', data)
            return channel_videos, channel_playlists, None
        global num_pages
        num_pages+=1
        nextPageToken = data.get("nextPageToken", None)

        item_data = data['items']
        for item in item_data:
            try:
                kind = item['id']['kind']
                published_at = item['snippet']['publishedAt']
                title = item['snippet']['title']
                if kind == 'youtube#video':
                    video_id = item['id']['videoId']
                    channel_videos[video_id] = {'publishedAt': published_at, 'title': title}
                elif kind == 'youtube#playlist':
                    playlist_id = item['id']['playlistId']
                    channel_playlists[playlist_id] = {'publishedAt': published_at, 'title': title}
            except KeyError as e:
                print('Error! Could not extract data from item:\n', item)

        return channel_videos, channel_playlists, nextPageToken

    def dump(self):
        """Dumps channel statistics and video data in a single json file"""
        if self.channel_statistics is None or self.video_data is None:
            print('data is missing!\nCall get_channel_statistics() and get_channel_video_data() first!')
            return

        fused_data = {self.channel_id: {"channel_statistics": self.channel_statistics,
                              "video_data": self.video_data}}

        channel_title = self.video_data.popitem()[1].get('channelTitle', self.channel_id)
        channel_title = channel_title.replace(" ", "_").lower()
        filename = channel_title + '.json'
        with open(filename, 'w') as f:
            json.dump(fused_data, f, indent=4)
        
        print('file dumped to', filename)


#brian hull UCiNeUoUWfBLC8mJuMzI6hvw
#Black Gryphon UCvzWGXYFDiiJ338KIJPhbhQ 
#Brock Baker  UCLzdMXE3R2xXIklfIO9HCcQ
# Ori  UCra3g9Qvmgux0NyY2Pdj4Lw
# Scheiffer Bates   UCcBacTJIf67LSU_-yeJwDvg
#Azerrz  UCiwIAU4SNlrcv47504JrJeQ
#Danny padilla & mason sperling  UCfhK8MfxO-9RCypkLDyW1rw
# Brizzy UC7lObFRyZgoZcMYHHqxi9lg
# Redfireball UC88CnZTYFz5ugp-JtDEQ3-g
# Sounds like pizza  UCh6OfzCefcCGFfihPbe_Y4g
#joshiiwuh  UCxRGk49YNiW3Cq8s7MGknqw
# simau UCkXvCWJjAqNcFwxF7hW_ZRQ
#Knep UCy7gv-FM-dMvw6dMtj8Qfgg
# charlie hopkinson  UCewLMcro9tNP97XQ1rxtLXQ
#Uss JA doin  UCqPYUMNbVeEhyTBIZCDO_VQ
# Shanieology  UCR93YdwZ4UKEUwf1gA-ZusA
# BigShade  UC7Wt6Nukmt83Bph3us5s5Aw
# Best in Class  UClQhFMEVUxJAwMW-KdZ0SvQ
# Daniel Ferguson  UCXFzOJmXVaP1tMLiww4aQzg
# Mikey Boltz  UC0gXT2T6KtmV0IHNNNvruAQ
# Maxamili  UC-0WjH-efG2qvNlZUBlX70Q




api_key= os.environ.get('YT_API')

# channel_ids= ['UCiNeUoUWfBLC8mJuMzI6hvw','UCvzWGXYFDiiJ338KIJPhbhQ','UCLzdMXE3R2xXIklfIO9HCcQ','UCra3g9Qvmgux0NyY2Pdj4Lw','UCcBacTJIf67LSU_-yeJwDvg',
# 'UCiwIAU4SNlrcv47504JrJeQ','UCfhK8MfxO-9RCypkLDyW1rw','UC7lObFRyZgoZcMYHHqxi9lg','UC88CnZTYFz5ugp-JtDEQ3-g','UCh6OfzCefcCGFfihPbe_Y4g',
# 'UCxRGk49YNiW3Cq8s7MGknqw','UCkXvCWJjAqNcFwxF7hW_ZRQ','UCy7gv-FM-dMvw6dMtj8Qfgg','UCewLMcro9tNP97XQ1rxtLXQ','UCqPYUMNbVeEhyTBIZCDO_VQ',
# 'UCR93YdwZ4UKEUwf1gA-ZusA','UC7Wt6Nukmt83Bph3us5s5Aw','UClQhFMEVUxJAwMW-KdZ0SvQ','UCXFzOJmXVaP1tMLiww4aQzg','UC0gXT2T6KtmV0IHNNNvruAQ',
# 'UC-0WjH-efG2qvNlZUBlX70Q']

channel_ids= ['UC-0WjH-efG2qvNlZUBlX70Q','UClQhFMEVUxJAwMW-KdZ0SvQ']

for channel_id in channel_ids:
    global num_pages
    num_pages = 0
    yt = YTstats(api_key,channel_id)
    yt.get_channel_statistics()
    yt.get_channel_video_data()
    yt.dump()
