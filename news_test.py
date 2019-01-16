import os
import sys
import time
import requests
import subprocess

def get_regional_news():
    kwargs = {}
    api_url = "https://tehiku.nz/api/te-reo/nga-take/latest"
    response = requests.get(api_url, **kwargs)
    response_dict = response.json()
    media = response_dict['media'][0]
    media_link = media['media_file']
    media_len = media['duration'] / 100
    print("News is {} seconds long".format(media_len))
    print("Latest news link is {}".format(media_link))
    return media_link, media_len

def play_media(media_link, media_len):
    subprocess.run(["mplayer", media_link])

def play_me_the_news():
    media_link, media_len = get_regional_news()
    play_media(media_link, media_len)


if __name__ == "__main__":
    play_me_the_news()
