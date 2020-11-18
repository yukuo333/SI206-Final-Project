from googleapiclient.discovery import build

#enter your youtube api key
youtube_api_key = 'AIzaSyACtD8D34hwm44lqQU_gwoTL5207HMWls8'
#build the service object
youtube_service = build('youtube','v3',developerKey=youtube_api_key)

def search_videos(q,max_results=5,order='relevance',token=None,location=None,location_radius=None):

    search_response = youtube_service.search().list(
        q=q,
        type = "video",
        pageToken = token,
        order = order,
        part = "id,snippet",
        maxResults = max_results,
        location = location,
        locationRadius = location_radius
    ).execute()

    videos = []
    
    for result in search_response.get("items",[]):
        if result['id']['kind'] == 'youtube#video':
            videos.append(result)
    
    

    return videos

# item['id']['videoId']
def get_likes_dislikes(id):

    search_response = youtube_service.videos().list(
        id = id,
        part = "id,snippet,statistics",
    ).execute()

    video_likes = search_response['items'][0]['statistics']['likeCount']
    video_dislikes = search_response['items'][0]['statistics']['dislikeCount']
    
    return (video_likes,video_dislikes)

def create_video_list(video_list):
    videos_list = []
    video_data = {}
    for video in video_list:
        video_data['title'] = video['snippet']['title']
        ldc = get_likes_dislikes(video['id']['videoId'])
        video_data['likes'] = ldc[0]
        video_data['dislikes'] = ldc[1]
        videos_list.append(video_data)
    
    return videos_list

print(create_video_list(search_videos('League of Legends')))
