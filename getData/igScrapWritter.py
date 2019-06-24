#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import ssl
import json
from random import choice
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import functools
import operator
import re
import emoji

USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36']

class Insta_Info_Scraper:
    def __init__(self, user_agents=None):
        self.user_agents = user_agents

    def __random_agent(self):
        if self.user_agents and isinstance(self.user_agents, list):
            return choice(self.user_agents)
        return choice(USER_AGENTS)

    def __request_url(self, url):
        try:
            response = requests.get(
                        url,
                        headers={'User-Agent': self.__random_agent()})
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError('Received non-200 status code.')
        except requests.RequestException:
            raise requests.RequestException
        else:
            return response.text
    @staticmethod
    def extract_json(html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        script_tag = body.find('script')
        raw_string = script_tag.text.strip().replace('window._sharedData =', '').replace(';', '')
        return json.loads(raw_string)

    def post_metrics(self, url):
        results = []
        try:
            response = self.__request_url(url)
            json_data = self.extract_json(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        except Exception as e:
            raise e
        else:
            for node in metrics:
                node = node.get('node')
                new_dict = {}
                if node and isinstance(node,dict):
                    fullDescr = str(node.get('edge_media_to_caption').get('edges'))[20:-4]
                    descrWithHashtags = fullDescr.split('#')
                    em_split_emoji = emoji.get_emoji_regexp().split(descrWithHashtags[0])
                    em_split_whitespace = [substr.split() for substr in em_split_emoji]
                    em_split = functools.reduce(operator.concat, em_split_whitespace)
                    new_dict['description'] = (em_split_emoji[0]).replace('\\n', '').rstrip()
                    descrWithHashtags.pop(0)
                    new_dict['hashtags'] = descrWithHashtags
                    if(len(em_split_emoji)>1):
                        new_dict['emojis'] = ', '.join(c for c in em_split_emoji if c >= 'U+1F600' and c != '\\n' and c)
                    else:
                        new_dict['emojis'] = []
                    new_dict['comments'] = node.get('edge_media_to_comment').get('count')
                    new_dict['comments_disabled'] = node.get('comments_disabled')
                    new_dict['time'] = node.get('taken_at_timestamp')
                    new_dict['likes'] = node.get('edge_liked_by').get('count')
                    new_dict['location'] = "" if node.get('location') is None else node.get('location').get('name')
                    new_dict['is_video'] = node.get('is_video')
                    new_dict['img_description'] = node.get('accessibility_caption') if node.get('accessibility_caption') else 'Na'
                    results.append(new_dict)
        return results

    def getinfo(self, url):
        html = urllib.request.urlopen(url, context=self.ctx).read()
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('meta', attrs={'property': 'og:description'
                             })
        text = data[0].get('content').split()
        user = '%s %s %s' % (text[-3], text[-2], text[-1])
        followers = text[0]
        following = text[2]
        posts = text[4]
        info={}
        info["User"] = user
        info["Followers"] = followers
        info["Following"] = following
        info["PostsCount"] = posts
        info["PostsDetails"] = self.post_metrics(url)
        self.info_arr.append(info)

    def main(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.info_arr=[]

        print('***** INSTABIZBIZ *****')
        print('Selectionner votre niche : ')
        print('1) Simple user')
        print('2) Sneakers user (fashion - chaussure)')
        print('3) Fitness')
        choice = input('Votre choix : ')
        if choice == '1':
            user_file = 'users.txt'
        elif choice == '2':
            user_file = 'sneakers.txt'
        elif choice == '3':
            user_file = 'users.txt'
        else :
            user_file = 'users.txt'

        with open(user_file) as f:
            self.content = f.readlines()
        self.content = [x.strip() for x in self.content]
        for url in self.content:
            self.getinfo(url)
        with open('data.json', 'w') as outfile:
            json.dump(self.info_arr, outfile, indent=4)
        print("Json file containing required info is created............")    

if __name__ == '__main__':
    instagram = Insta_Info_Scraper()
    instagram.main()

