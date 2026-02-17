import asyncio
import socketio
import httpx
from fastapi import FastAPI, Request
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from TikTokLive import TikTokLiveClient
from TikTokLive.events import LikeEvent, ConnectEvent, DisconnectEvent, CommentEvent
import uvicorn
import os
import csv
import io
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

VERSION = "1.0.3"
UPDATE_URL = "https://your-github-username.github.io/your-repo-name/version.json" # Placeholder

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

templates = Jinja2Templates(directory="templates")

# Global state to manage the TikTok client and tap counts
class TikTokManager:
    def __init__(self):
        self.client = None
        self.user_taps = {}
        self.current_streamer = None
        self.is_connected = False
        self.update_available = False

    async def check_for_updates(self):
        print("Checking for updates...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(UPDATE_URL)
                if response.status_code == 200:
                    data = response.json()
                    remote_version = data.get("version")
                    if remote_version and remote_version != VERSION:
                        print(f"Update available: {remote_version}")
                        self.update_available = remote_version
                        await sio.emit('update_available', data)
                    else:
                        print("App is up to date.")
        except Exception as e:
            print(f"Update check failed: {e}")

    async def connect(self, unique_id):
        if self.client:
            await self.stop()
        
        self.current_streamer = unique_id
        self.user_taps = {}
        self.client = TikTokLiveClient(unique_id=unique_id)

        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            self.is_connected = True
            await sio.emit('status', {'connected': True, 'streamer': self.current_streamer})
            logging.info(f"Connected to @{unique_id}")

        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            # Log comments just to verify we are receiving data
            logging.info(f"Comment: {event.user.nickname}: {event.comment}")

        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            try:
                # In newer versions of TikTokLive, unique_id is often the identifier
                # and user_id might be inside event.user.id or similar.
                # Let's use unique_id as it's definitely available.
                uid = str(event.user.unique_id)
                nickname = event.user.nickname
                
                # Fix for attribute error: try 'count', then 'likes', then default to 1
                if hasattr(event, 'count'):
                    like_count = event.count
                elif hasattr(event, 'likes'):
                    like_count = event.likes
                elif hasattr(event, 'like_count'):
                     like_count = event.like_count
                else:
                    logging.warning(f"Could not find like count attribute in {dir(event)}")
                    like_count = 1
                
                logging.info(f"LikeEvent detected! {nickname} (@{uid}) +{like_count}")
                
                if uid not in self.user_taps:
                    self.user_taps[uid] = {
                        'nickname': nickname, 
                        'count': 0,
                        'avatar': event.user.avatar.urls[0] if event.user.avatar and event.user.avatar.urls else None
                    }
                else:
                    # Update avatar if available (might change)
                    if event.user.avatar and event.user.avatar.urls:
                         self.user_taps[uid]['avatar'] = event.user.avatar.urls[0]
                
                self.user_taps[uid]['count'] += like_count
                
                logging.info(f"Emitting tap_update for {nickname}")
                await sio.emit('tap_update', {
                    'user_id': uid,
                    'nickname': nickname,
                    'avatar': self.user_taps[uid]['avatar'],
                    'add_count': like_count,
                    'total_count': self.user_taps[uid]['count']
                })
            except Exception as e:
                logging.error(f"Error in on_like: {e}")
            except Exception as e:
                logging.error(f"Error in on_like: {e}")
                import traceback
                logging.error(traceback.format_exc())

        @self.client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            self.is_connected = False
            await sio.emit('status', {'connected': False, 'streamer': self.current_streamer})
            logging.info(f"Disconnected from @{unique_id}")

        # Run the client in a separate task
        asyncio.create_task(self.run_client())

    async def run_client(self):
        try:
            await self.client.start()
        except Exception as e:
            logging.error(f"Client error: {e}")
            await sio.emit('error', {'message': str(e)})
            self.is_connected = False

    async def stop(self):
        if self.client:
            try:
                await self.client.stop()
            except:
                pass
            self.client = None
            self.is_connected = False
            await sio.emit('status', {'connected': False})

    def get_csv_data(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['User ID', 'Nickname', 'Total Likes', 'Avatar URL'])
        
        # Sort by count descending
        sorted_users = sorted(self.user_taps.values(), key=lambda x: x['count'], reverse=True)
        
        for user in sorted_users:
            writer.writerow([
                # We need to find the ID for this user object (a bit inefficient but works for now)
                # Actually, better to store ID in the object too? 
                # Let's iterate items() instead.
                # Wait, sorted_users is a list of dicts. 
                # Let's do this cleaner:
                '', # Placeholder for ID if not easily accessible in values, but we need it.
                user['nickname'],
                user['count'],
                user.get('avatar', '')
            ])
        return output.getvalue()
        
    def get_csv_data_with_ids(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Rank', 'User ID', 'Nickname', 'Total Likes', 'Avatar URL'])
        
        # Create list of (id, data) tuples
        items = list(self.user_taps.items())
        # Sort by count desc
        items.sort(key=lambda x: x[1]['count'], reverse=True)
        
        for i, (uid, data) in enumerate(items, 1):
             writer.writerow([
                 i,
                 uid,
                 data['nickname'],
                 data['count'],
                 data.get('avatar', '')
             ])
        return output.getvalue()

manager = TikTokManager()

@app.get("/export_csv")
async def export_csv():
    csv_content = manager.get_csv_data_with_ids()
    filename = f"tiktok_taps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "version": VERSION})

@app.post("/shutdown")
async def shutdown():
    print("Shutdown requested from frontend. Exiting...")
    os._exit(0)

@sio.on('connect')
async def handle_connect_socket(sid, environ):
    if manager.update_available:
        await sio.emit('update_available', {'version': manager.update_available}, to=sid)
    if manager.is_connected:
        await sio.emit('status', {'connected': True, 'streamer': manager.current_streamer}, to=sid)
    
    # Rehydration: Send full current data
    if manager.user_taps:
        # Send as a list for easier frontend handling? Or just dict.
        # Let's send dict for now, or maybe the list for the leaderboard directly.
        # Sending the raw dictionary allows frontend to rebuild whatever it needs.
        await sio.emit('initial_data', manager.user_taps, to=sid)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(manager.check_for_updates())

@sio.on('connect_streamer')
async def handle_connect(sid, data):
    unique_id = data.get('unique_id')
    if unique_id:
        print(f"Web request to connect to @{unique_id}")
        await manager.connect(unique_id)

@sio.on('disconnect_streamer')
async def handle_disconnect(sid):
    print("Web request to disconnect")
    manager.user_taps = {} # Clear session data
    await manager.stop()

@sio.on('confirm_update')
async def handle_confirm_update(sid, data):
    download_url = data.get('url')
    if download_url:
        print(f"Update confirmed. Launching updater for: {download_url}")
        import subprocess
        import sys
        
        # Determine paths
        current_exe = sys.executable
        if not current_exe.endswith(".exe"):
            # If running from source, this might not work as intended for end users, 
            # but for testing we can mock it or just print.
            print("Running from source, cannot update exe directly.")
            return

        updater_exe = os.path.join(os.path.dirname(current_exe), "updater.exe")
        
        # If updater not found (e.g. running from source), try to find it in current dir
        if not os.path.exists(updater_exe):
            updater_exe = "updater.exe"
        
        if os.path.exists(updater_exe):
            subprocess.Popen([updater_exe, download_url, current_exe])
            os._exit(0) # Force exit
        else:
             print("Updater executable not found.")

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
