import os
import json
from datetime import datetime

from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import openai

app = Flask(__name__)

SUMMARIES_FILE = 'summaries.json'

# Load API keys from environment
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

openai.api_key = OPENAI_API_KEY

# Helper functions

def load_summaries():
    if os.path.exists(SUMMARIES_FILE):
        with open(SUMMARIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_summaries(data):
    with open(SUMMARIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_subscribed_channels():
    """Return list of channel IDs the user is subscribed to."""
    # Placeholder implementation using YouTube API should be implemented here.
    return []


def get_latest_videos(channel_id):
    """Return latest video titles for a channel"""
    # Placeholder implementation. Real code should call YouTube API.
    return []


def summarize_text(text):
    if not OPENAI_API_KEY:
        return "No OPENAI_API_KEY provided."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant summarizing YouTube videos."},
                  {"role": "user", "content": text}]
    )
    return response.choices[0].message.content.strip()


def summarize_new_videos():
    summaries = load_summaries()
    channels = get_subscribed_channels()
    for channel_id in channels:
        videos = get_latest_videos(channel_id)
        for video in videos:
            video_id = video.get('id')
            title = video.get('title')
            if video_id not in summaries:
                summary = summarize_text(title)
                summaries[video_id] = {
                    'title': title,
                    'summary': summary,
                    'timestamp': datetime.utcnow().isoformat()
                }
    save_summaries(summaries)


scheduler = BackgroundScheduler()
scheduler.add_job(summarize_new_videos, 'cron', hour=0, minute=0)
scheduler.start()


@app.route('/')
def index():
    return "YouTube Summary Service running"


@app.route('/summaries')
def get_summaries():
    return jsonify(load_summaries())


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000)
    finally:
        scheduler.shutdown()
