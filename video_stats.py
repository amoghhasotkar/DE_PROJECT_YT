import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import date

load_dotenv(dotenv_path=Path(__file__).resolve().with_name('.env'))

API_KEY = os.getenv('API_KEY')

max_results = 10

if not API_KEY:
    raise RuntimeError('API_KEY is missing from .env')

CHANNEL_HANDLE = 'SamayRainaOfficial'

def get_playlist_id():
    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()
        # print(json.dumps(data, indent=4))

        channel_items = data["items"][0]

        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        print(channel_playlistId)

        return channel_playlistId

        
    except requests.exceptions.RequestException as e:
        raise e


def get_video_ids(playlistId):

    video_ids=[]

    page_token = None

    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlistId}&key={API_KEY}'

    try:
        while True:
            url = base_url
            if page_token:
                url += f'&pageToken={page_token}'

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()
            # print(json.dumps(data, indent=4))

            items = data.get("items", [])
            for item in items:
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            page_token = data.get("nextPageToken")
            
            if not page_token:
                break
        return video_ids
    
    except requests.exceptions.RequestException as e:
        raise e
    

def extract_video_data(video_id_list):

    video_data = []

    def batch_list(video_id_list, batch_size):
        for video_id in range(0,len(video_id_list), batch_size):
            yield video_id_list[video_id:video_id + batch_size]
        
    f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id=LhpZJwUboeI&maxResults=1&key={API_KEY}"

    try:
        for batch in batch_list(video_id_list, max_results):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            for item in items:
                video_info = {
                    "videoId": item["id"],
                    "title": item["snippet"]["title"],
                    "publishedAt": item["snippet"]["publishedAt"],
                    "viewCount": item["statistics"].get("viewCount", 0),
                    "likeCount": item["statistics"].get("likeCount", 0),
                    "commentCount": item["statistics"].get("commentCount", 0)
                }
                video_data.append(video_info)
        return video_data

    except requests.exceptions.RequestException as e:
        raise e
    
def save_to_json(video_data):
    file_path = f'./data/YT_video_data_{date.today()}.json'
    with open(file_path, 'w',encoding='utf-8') as json_file:
        json.dump(video_data, json_file, indent=4,ensure_ascii=False)
        
if __name__ == "__main__":
    playlistId = get_playlist_id()
    video_ids = get_video_ids(playlistId)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)
