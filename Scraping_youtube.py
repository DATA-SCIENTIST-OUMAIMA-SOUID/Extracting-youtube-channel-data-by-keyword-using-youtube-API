# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 00:56:07 2020

@author: oumaima
"""
# ------------------------------------------------ library-------------------------------------

# examplesprint(numerize('Eight fifty million'))
#from numerizer import numerize
import numpy as np
#from emot.emo_unicode import UNICODE_EMO, EMOTICONS
from itertools import chain
from googleapiclient.discovery import build
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
#from langdetect import detect
import re   # regular expression
import os
from google.auth.transport.requests import Request
import pickle
import time
import demoji
#demoji.download_codes()

# ------------------------------------------------ data recovery -------------------------------------
CLIENT_SECRETS_FILE = "your_code_secret_client_key.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Authentification

def get_authenticated_service():
    try:
        credentials = None
        if os.path.exists('token1.pickle'):
            with open('token1.pickle', 'rb') as token:
                credentials = pickle.load(token)
        #  Check if the credentials are invalid or do not exist
        if not credentials or not credentials.valid:
            # Check if the credentials have expired
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, SCOPES)
                credentials = flow.run_console()
            # Save the credentials for the next run
            with open('token1.pickle', 'wb') as token:
                pickle.dump(credentials, token)
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    except Exception as e:
        print('reeeeeeeeeeeeeeeeeeeeee', str(e))


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
service = get_authenticated_service()



    # Retrieving video list
    
    def get_videos(service, nb, **kwargs):
        final_results = []
        results = service.search().list(**kwargs).execute()
    
        i = 0
        max_pages = nb
        while results and i < max_pages:
            final_results.extend(results['items'])
            # Check if another page exists
            if 'nextPageToken' in results:
                kwargs['pageToken'] = results['nextPageToken']
                results = service.search().list(**kwargs).execute()
                i += 1
            else:
                break
        return final_results

 # Retrieving comments

    def get_video_comments(service, **kwargs):
        comments = []
        results = service.commentThreads().list(**kwargs).execute()
        while results:
            for item in results['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                likeCount = item['snippet']['topLevelComment']['snippet']['likeCount']
                publishedAt = item['snippet']['topLevelComment']['snippet']['publishedAt']
                comments.append({"comment": comment, "username": username,
                                 "likeCount": likeCount, "publishedAt": publishedAt})
            if 'nextPageToken' in results:
                kwargs['pageToken'] = results['nextPageToken']
                results = service.commentThreads().list(**kwargs).execute()
            else:
                break
    
        return comments




def getVideosStats(service, id1):
    request = service.videos().list(
        part="statistics",
        id=id1
    )
    response = request.execute()
    return response["items"][0]['statistics']

    
    def search_videos_by_keyword(service, nb, **kwargs):
        results = get_videos(service, nb, **kwargs)
        retour = []
        for item in results:
    
            try:
                channel_id = item['snippet']['channelId']
                channel_title = item['snippet']['channelTitle']
                published_at = item['snippet']['publishedAt']
                video_id = item['id']['videoId']
                stats = getVideosStats(service, video_id)
                title = item['snippet']['title']
                description = item['snippet']['description']
                publishTime = item["snippet"]["publishTime"]
                likeCnt = stats["likeCount"]
                dislikeCnt = stats["dislikeCount"]
                viewCnt = stats["viewCount"]
                comments = get_video_comments(
                    service, part='snippet', videoId=video_id, textFormat='plainText')
                for c in comments:
                    retour.append({"channel_id": channel_id, "channel_title": channel_title, "vid_view": viewCnt, "vid_like": likeCnt, "vid_dis": dislikeCnt,
                                   "video_id": video_id, "title": title, "description": description, "published_at": published_at, "comment": c["comment"],
                                   "username": c["username"], "likeCount": c["likeCount"], "publishTime": publishTime})
            except Exception as ex:
                print(str(ex), "--------------*----------------")
        return retour

    
    keyword = input('Enter a keyword: ')
    liste_commentaire = []
    try:
        for i in range(3):
            liste_commentaire.append(search_videos_by_keyword(service, 3, q=keyword, part='id,snippet', eventType='completed', type='video'))
            time.sleep(10)
    except Exception as e:
        print("-----", str(e))
    
        
    #convert list to dataframe  
    df_Youtube = pd.DataFrame(list(chain.from_iterable(liste_commentaire)))
    print(df_Youtube.shape)
    #convertir dataframe en fichier excel
    df_Youtube.to_csv(r'export_dataframe.csv', index=False, sep=';')




#df.columns = ['Channel', 'Title', 'ID', 'Comment']
#df = pd.DataFrame(liste_commentaire, columns=['title','id','Commentaires'])
