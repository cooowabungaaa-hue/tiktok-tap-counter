import sys
from TikTokLive import TikTokLiveClient
from TikTokLive.events import LikeEvent, ConnectEvent

def main():
    if len(sys.argv) < 2:
        print("Usage: python tap_counter.py <uniqueId>")
        print("Example: python tap_counter.py @username")
        sys.exit(1)

    unique_id = sys.argv[1]
    
    # User-specific tap counts
    # key: user_id, value: {'nickname': str, 'count': int}
    user_taps = {}

    client = TikTokLiveClient(unique_id=unique_id)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        print(f"Connected to @{unique_id} (Room ID: {client.room_id})")

    @client.on(LikeEvent)
    async def on_like(event: LikeEvent):
        user_id = event.user.user_id
        nickname = event.user.nickname
        
        # LikeEvent.total_likes might be the count of likes in that specific event (taps are often batched)
        # or the total likes of the stream. For "tap count per user", we increment by event.like_count.
        like_count = event.like_count
        
        if user_id not in user_taps:
            user_taps[user_id] = {'nickname': nickname, 'count': 0}
        
        user_taps[user_id]['count'] += like_count
        
        # Clear console and show leaderboard (simplistic way)
        # In a real tool, you might want index or more complex UI
        print(f"\r[LIKE] {nickname}: +{like_count} (Total: {user_taps[user_id]['count']})", end="", flush=True)

    @client.on("reconnect")
    async def on_reconnect(event):
        print(f"\nReconnecting to @{unique_id}...")

    @client.on("disconnect")
    async def on_disconnect(event):
        print(f"\nDisconnected from @{unique_id}.")

    try:
        print(f"Connecting to @{unique_id}...")
        client.run()
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
