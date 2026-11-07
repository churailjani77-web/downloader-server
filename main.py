from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import yt_dlp

app = FastAPI(title="Namaz Ka Sakoon - Master Video Streamer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "engine": "FastAPI Proxy Stream Active 🚀"}

# 🚀 1. ASAL PROXY STREAM PIPE (Direct mobile ko video bhejna, Zero 403 Error!)
@app.get("/stream")
async def stream_video(video_url: str = Query(..., description="Target Video Stream URL")):
    if not video_url:
        raise HTTPException(status_code=400, detail="video_url missing!")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    }

    client = httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=60.0)
    req = client.build_request("GET", video_url)
    resp = await client.send(req, stream=True)

    if resp.status_code != 200:
        await resp.aclose()
        await client.aclose()
        raise HTTPException(status_code=resp.status_code, detail="Video source stream failed")

    async def stream_generator():
        try:
            async for chunk in resp.aiter_raw():
                yield chunk
        finally:
            await resp.aclose()
            await client.aclose()

    return StreamingResponse(
        stream_generator(),
        media_type=resp.headers.get("content-type", "video/mp4"),
        headers={
            "Content-Disposition": "attachment; filename=downloaded_video.mp4",
            "Accept-Ranges": "bytes"
        }
    )

# 2. RESOLVER (Direct Links Extraction)
@app.get("/download")
async def extract_info(url: str = Query(..., description="Target Video URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing!")

    # TikTok Fast Clean Gateway
    if "tiktok.com" in url or "vt.tiktok" in url:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.get(f"https://www.tikwm.com/api/?url={url}")
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    raw_video = data.get("play") or data.get("wmplay")
                    if raw_video:
                        # 🚀 Magic: Mobile ko Vercel ki apni Proxy Pipe ka link do!
                        proxy_url = f"https://downloader-server-swart.vercel.app/stream?video_url={raw_video}"
                        return {
                            "success": True,
                            "title": data.get("title", "TikTok Video"),
                            "thumbnail": data.get("cover"),
                            "video_url": proxy_url, # 👈 Mobile Vercel se download karega!
                            "platform": "TikTok"
                        }
        except Exception:
            pass

    # Universal yt-dlp for Shorts, Insta, Snapchat
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {'player_client': ['android', 'ios']}
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            if not video_url and 'entries' in info and len(info['entries']) > 0:
                video_url = info['entries'][0].get('url')

            if not video_url:
                raise Exception("Stream nahi mila")

            # Baqi platforms ko bhi Vercel ki Proxy Pipe se guzaro:
            proxy_url = f"https://downloader-server-swart.vercel.app/stream?video_url={video_url}"
            return {
                "success": True,
                "title": info.get('title', 'Video Download'),
                "thumbnail": info.get('thumbnail'),
                "video_url": proxy_url,
                "platform": info.get('extractor_key', 'Universal')
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
