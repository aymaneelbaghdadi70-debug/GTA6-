import os
import requests
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build

# جلب المفاتيح بأمان من إعدادات GitHub
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# حساب الوقت قبل 8 ساعات لجلب المقاطع الحديثة فقط
eight_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%SZ')

def send_telegram_message(text):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def fetch_gta6_videos():
    results_list = []

    # 1. البحث في مقاطع المشاع الإبداعي (Creative Commons) لـ GTA 6
    cc_request = youtube.search().list(
        part="snippet",
        q="GTA 6 gameplay OR trailer OR highlights",
        type="video",
        videoLicense="creativeCommon", # فلتر المشاع الإبداعي فقط
        publishedAfter=eight_hours_ago,
        order="viewCount",
        maxResults=3
    )
    cc_response = cc_request.execute()

    for item in cc_response.get('items', []):
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        link = f"https://youtube.com{video_id}"
        results_list.append(f"🟢 *[مشاع إبداعي]* {title}\n🔗 {link}")

    # 2. البحث في القناة الرسمية لشركة Rockstar Games
    # المعرف الرسمي لقناة روكستار هو: UC6qhGbK96asGJwk9pZvUHpw
    official_request = youtube.search().list(
        part="snippet",
        channelId="UC6qhGbK96asGJwk9pZvUHpw",
        q="GTA 6",
        type="video",
        publishedAfter=eight_hours_ago,
        order="date",
        maxResults=2
    )
    official_response = official_request.execute()

    for item in official_response.get('items', []):
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        link = f"https://youtube.com{video_id}"
        results_list.append(f"🏢 *[قناة روكستار الرسمية]* {title}\n🔗 {link}")

    return results_list

if __name__ == "__main__":
    videos = fetch_gta6_videos()
    if videos:
        header = "🎮 *تقرير لقطات GTA 6 الجديدة (آخر 8 ساعات):*\n\n"
        full_message = header + "\n\n".join(videos)
        send_telegram_message(full_message)
    else:
        print("لا توجد مقاطع جديدة في آخر 8 ساعات.")