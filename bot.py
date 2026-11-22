import os
import json
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

STATE_FILE = "last_videos.json"
SEARCH_QUERIES = [
    "GTA 6 trailer",
    "Grand Theft Auto VI Rockstar Games"
]


def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_TOKEN or CHAT_ID is missing.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload, timeout=15)
    response.raise_for_status()


def load_seen_videos():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_seen_videos(seen_ids):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_ids), f, ensure_ascii=False, indent=2)


def search_youtube(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "date",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json().get("items", [])


def main():
    if not YOUTUBE_API_KEY:
        print("Error: YOUTUBE_API_KEY is missing.")
        return

    seen_ids = load_seen_videos()
    new_videos = []

    for query in SEARCH_QUERIES:
        items = search_youtube(query)
        for item in items:
            video_id = item.get("id", {}).get("videoId")
            if video_id and video_id not in seen_ids:
                seen_ids.add(video_id)
                title = item.get("snippet", {}).get("title", "New Video")
                channel = item.get("snippet", {}).get("channelTitle", "Unknown Channel")
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                new_videos.append((title, channel, video_url))

    for title, channel, video_url in new_videos:
        message = (
            f"🎬 <b>فيديو جديد متعلق بـ GTA 6!</b>\n\n"
            f"📌 <b>العنوان:</b> {title}\n"
            f"📺 <b>القناة:</b> {channel}\n"
            f"🔗 {video_url}"
        )
        send_telegram_message(message)

    save_seen_videos(seen_ids)
    print(f"Done. Found {len(new_videos)} new video(s).")


if __name__ == "__main__":
    main()
