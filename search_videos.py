from googleapiclient.discovery import build
import sqlite3
import os

#enter your youtube api key
youtube_api_key = ''
#build the service object
youtube_service = build('youtube','v3',developerKey=youtube_api_key)

def search_videos(q,max_results=1,order='viewCount',token=None,location=None,location_radius=None,publishedDate = '2018-01-01T00:00:00Z'):

    search_response = youtube_service.search().list(
        q=q,
        type = "video",
        pageToken = token,
        order = order,
        part = "id,snippet",
        maxResults = max_results,
        location = location,
        locationRadius = location_radius,
        publishedAfter = publishedDate
    ).execute()

    videos = []
    
    for result in search_response.get("items",[]):
        if result['id']['kind'] == 'youtube#video':
            videos.append(result)
    
    return videos

#return like and dislike count for 1 video
#parameter id = unique youtube video id
def get_likes_dislikes(id):

    search_response = youtube_service.videos().list(
        id = id,
        part = "id,snippet,statistics",
    ).execute()

    video_likes = search_response['items'][0]['statistics']['likeCount']
    video_dislikes = search_response['items'][0]['statistics']['dislikeCount']
    view_count = search_response['items'][0]['statistics']['viewCount']
    
    return (video_likes,video_dislikes,view_count)

#create a dict of videos with keys: title, likes, dislikes
def create_video_list(q):
    input_list = search_videos(q)
    videos_list = []
    video_data = {}
    for video in input_list:
        video_data['title'] = video['snippet']['title']
        ldc = get_likes_dislikes(video['id']['videoId'])
        video_data['likes'] = ldc[0]
        video_data['dislikes'] = ldc[1]
        video_data['viewCount'] = ldc[2]
        videos_list.append(video_data)
    
    return videos_list

