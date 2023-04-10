import os

import httpx
import pocketbase


class DB:
    def __init__(self, url: str | None = None):
        self.url = url or os.getenv('POCKETBASE_URL')
        self.pb = pocketbase.PocketBase(self.url)
        self.user_data = None

    def login(self, username: str, password: str):
        self.user_data = self.pb.collection(
            'users').auth_with_password(username, password)
        return self.user_data

    def login_admin(self, username: str, password: str):
        self.user_data = self.pb.admins.auth_with_password(username, password)
        return self.user_data

    def get_transcript(self, video_id: str):
        url = f'{self.url}/youtube/transcript/{video_id}'
        resp = httpx.get(url)
        return resp.json()

    def get_summary(self, video_id: str, channel_id: str = ""):
        token = self.get_auth_token()
        if not token:
            raise Exception('Not logged in')
        url = f'{self.url}/ai/summary/{video_id}'
        resp = httpx.get(url, headers={
            'Authorization': token,
            "discordChannelId": channel_id
        })

        return resp.json()

    def fetch_summary(self, video_id: str):
        resp = self.pb.collection('summaries').get_list(1, 1, {
            'filter': f'videoId="{video_id}"'
        })
        return resp.items[0]

    def post_summary(self, video_id: str, summary: str):
        resp = self.pb.collection('summaries').create({
            'videoId': video_id,
            'summary': summary
        })
        return resp

    def get_auth_token(self):
        return self.pb.auth_store.token


if __name__ == '__main__':
    db = DB('http://127.0.0.1:8090')
    # we should make the bot its own user
    user = db.login('chand1012', 'password')
    videoId = 'UeCdBVHYa_8'
    transcript = db.get_transcript(videoId)
    print(transcript)
    summary = db.get_summary(videoId)
    print(summary.summary)
