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
import json
import pandas as pd
import io
from pandas.io.json import json_normalize
from datetime import datetime
from nltk.stem.porter import *
from nltk.corpus import stopwords
import os
import os.path
from imageai.Prediction import ImagePrediction
from PIL import Image

USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36']
execution_path = os.getcwd()

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

    def post_metrics(self,user, followers, following, posts, url):
        try:
            response = self.__request_url(url)
            json_data = self.extract_json(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        except Exception as e:
            raise e
            df_postDetails['followers'] = (df_postDetails['followers'].replace(r'[km]+$', '', regex=True).astype(float) *  df_postDetails['followers'].str.extract(r'[\d\.]+([km]+)', expand=False).na(1).ce(['k','m'], [10**3, 10**6]).astype(int))

        else:
            for node in metrics:
                node = node.get('node')
                new_dict = {}
                if node and isinstance(node,dict):
                    fullDescr = str(node.get('edge_media_to_caption').get('edges'))[20:-4]
                    descrWithHashtags = [hash.split(' ')[0].replace('\\n', '') for hash in fullDescr.split('#')]
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
                    new_dict["user"] = user
                    print('User : ',user)
                    new_dict["followers"] = followers
                    new_dict["following"] = following
                    new_dict["postsCount"] = posts
                    new_dict['comments'] = node.get('edge_media_to_comment').get('count')
                    new_dict['comments_disabled'] = node.get('comments_disabled')
                    new_dict['time'] = node.get('taken_at_timestamp')
                    new_dict['likes'] = node.get('edge_liked_by').get('count')
                    print('likes : ',new_dict['likes'])
                    new_dict['location'] = "" if node.get('location') is None else node.get('location').get('name')
                    new_dict['is_video'] = node.get('is_video')
                    new_dict['img_description'] = node.get('accessibility_caption')[19:] if node.get('accessibility_caption') else 'Na'
                    self.info_arr.append(new_dict)

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
        self.post_metrics(user, followers, following, posts,url)

    def main(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.info_arr=[]

        print('***** INSTABIZBIZ *****')
        print('Menu : ')
        print('1) Analyse d\'image')
        print('2) Sneakers user (fashion - chaussure)')
        print('3) Fitness')
        choice = input('Votre choix : ')
        if choice == '1':
            path = execution_path + "/pics"
            valid_images = [".jpg",".gif",".png"]
            if(len(os.listdir(path)) != 1):
                print("Le dossier contient plus d'une image.")
                menu()
            else:
                ext = os.path.splitext(os.listdir(path)[0])[1]
                if ext.lower() not in valid_images:
                    print("L'extension n'est pas supportée.")
                    menu()
                else:
                    strFichier = os.listdir(path)[0]
                    newDict = {}
                    prediction = ImagePrediction()
                    prediction.setModelTypeAsResNet()
                    prediction.setModelPath( execution_path + "/resnet50_weights_tf_dim_ordering_tf_kernels.h5")
                    prediction.loadModel()

                    predictions, percentage_probabilities = prediction.predictImage(execution_path + "/pics/" + strFichier, result_count=2)
                    for index in range(len(predictions)):
                        newDict.update({predictions[index] : percentage_probabilities[index]})
                    pred = newDict
                    print("Votre image contient : " + (next(iter(pred)).replace('_', ' ')))
                    return 0
        elif choice == '2':
            user_file = 'sneakers.txt'
        elif choice == '3':
            user_file = 'users.txt'
        else :
            user_file = 'users.txt'

        # with open(user_file) as f:
        #     self.content = f.readlines()
        # self.content = [x.strip() for x in self.content]
        # for url in self.content:
        #     self.getinfo(url)
        # with open('data.json', 'w') as outfile:
        #     json.dump(self.info_arr, outfile, indent=4)
        # print("Json file containing required info is created............")    
        
        df = pd.read_json("data.json")
        df.head(2)
        df_postDetails = df
        del df_postDetails['emojis']
        del df_postDetails['user']
        df_postDetails['img_description'] = df_postDetails['img_description'].astype(str).str[19:]
        df_postDetails['hashtags'] = df_postDetails['hashtags'].apply(','.join)
        del df_postDetails['hashtags']
        del df_postDetails['comments_disabled']
        df_postDetails['time'] = pd.to_datetime(df_postDetails['time'].astype(int), unit='s')
        df_postDetails.head()
        df_postDetails['followers'] = (df_postDetails['followers'].replace(r'[kmb]+$', '', regex=True).astype(float) * df_postDetails['followers'].str.extract(r'[\d\.]+([kmb]+)', expand=False).fillna(1).replace(['k','m', 'b'], [10**3, 10**6, 10**9]).astype(int))

        #stop words
        import nltk
        nltk.download('stopwords')

        ps = PorterStemmer()
        from nltk.stem.wordnet import WordNetLemmatizer
        nltk.download('wordnet')
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')

        lmtzr = WordNetLemmatizer()
        stop = stopwords.words("english")
        df_postDetails['description'] = df_postDetails['description'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
        df_postDetails['description'] = df_postDetails['description'].apply(lambda x: ' '.join([ps.stem(word) for word in x.split()]))
        df_postDetails['description'] = df_postDetails['description'].apply(lambda x: ' '.join([lmtzr.lemmatize(word, 'v') for word in x.split()]))
        df_postDetails['POS'] = df_postDetails['description'].apply(lambda x: nltk.pos_tag(nltk.word_tokenize(x)))
        del df_postDetails['description']
        del df_postDetails['POS']
        df_postDetails.head(5)

        # format data for trainning 
        from sklearn.model_selection import train_test_split
        X = df_postDetails.get(['comments','followers','is_video']).values 
        Y = df_postDetails["likes"].values
        features_train, features_test, target_train, target_test = train_test_split(
            X, Y, test_size=0.20, random_state=0)
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators = 100,max_depth=12,max_features='log2')
        X.tolist()
        #fit sur le train
        model.fit(features_train,target_train)
        #predict test
        y_pred = model.predict(features_test)
        #get score : 
        from sklearn.metrics import f1_score
        print('Score: ', model.score(X, Y))

if __name__ == '__main__':
    instagram = Insta_Info_Scraper()
    instagram.main()

