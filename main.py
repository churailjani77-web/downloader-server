from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import urllib.request
import urllib.parse
import json
import yt_dlp

app = FastAPI(title="Namaz Ka Sakoon Video Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "message": "Namaz Ka Sakoon Video Engine 100% Active 🚀"}

# 1. TIKTOK DIRECT CLEAN ENGINE (Built-in urllib, Zero Crash!)
def get_tiktok(url: str):
    api_url = "https://www.tikwm.com/api/?url=" + urllib.parse.quote(url)
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        data = result.get("data", {})
        play_url = data.get("play") or data.get("wmplay")
        if play_url:
            return {
                "success": True,
                "title": data.get("title", "TikTok Video"),
                "thumbnail": data.get("cover"),
                "video_url": play_url,
                "platform": "TikTok"
            }
    return None

# 2. UNIVERSAL ENGINE (YouTube Shorts, Insta, Snapchat)
def get_universal(url: str):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {'player_client': ['android', 'ios']}
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_url = info.get('url')
        if not video_url and 'entries' in info and len(info['entries']) > 0:
            video_url = info['entries'][0].get('url')

        if not video_url:
            raise Exception("Direct stream URL nahi mil saka.")

        return {
            "success": True,
            "title": info.get('title', 'Video Download'),
            "thumbnail": info.get('thumbnail'),
            "video_url": video_url,
            "platform": info.get('extractor_key', 'Universal')
        }

@app.get("/download")
def download_api(url: str = Query(..., description="Target Video URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing!")

    url = url.strip()

    # TikTok Fast Path:
    if "tiktok.com" in url or "vt.tiktok" in url:
        try:
            res = get_tiktok(url)
            if res:
                return res
        except Exception:
            pass

    # Universal Path:
    try:
        return get_universal(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
