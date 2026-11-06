from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="Namaz Ka Sakoon - Universal Media Engine")

# App ke sath connect hone ke liye CORS enable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Namaz Ka Sakoon Universal Downloader Engine Active 🚀",
        "supported": ["TikTok (No Watermark)", "Instagram Reels", "Snapchat", "YouTube Shorts", "Facebook"]
    }

@app.get("/download")
def extract_video(url: str = Query(..., description="Video URL to download")):
    if not url:
        raise HTTPException(status_code=400, detail="URL dena zaroori hai!")

    # yt-dlp ki fast extraction settings (bina download kiye direct link nikalna):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Direct video link nikalna
            video_url = info.get('url')
            if not video_url and 'entries' in info and len(info['entries']) > 0:
                video_url = info['entries'][0].get('url')

            if not video_url:
                raise HTTPException(status_code=404, detail="Video ka direct link nahi mil saka.")

            return {
                "success": True,
                "title": info.get('title', 'Video Download'),
                "thumbnail": info.get('thumbnail'),
                "video_url": video_url,
                "duration": info.get('duration'),
                "platform": info.get('extractor_key', 'Universal')
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download Error: {str(e)}")