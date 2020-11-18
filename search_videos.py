from googleapiclient.discovery import build

#youtube api key
youtube_api_key = 'AIzaSyACtD8D34hwm44lqQU_gwoTL5207HMWls8'

def search_videos(q,max_results=10,order='relevance',token=None,location=None,location_radius=None):

    #build the service object
    youtube_service = build('youtube','v3',developerKey=youtube_api_key)

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

print(search_videos('League of Legends'))


