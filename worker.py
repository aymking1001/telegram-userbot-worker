
import os
import base64
from telethon import TelegramClient

session_data = base64.b64decode(
    os.environ["TELEGRAM_SESSION"]
)

with open("github_session.session", "wb") as f:
    f.write(session_data)

client = TelegramClient(
    "github_session",
    int(os.environ["TELEGRAM_API_ID"]),
    os.environ["TELEGRAM_API_HASH"]
)

async def main():
    me = await client.get_me()
    print(f"Logged in as: {me.id} | {me.first_name}")

with client:
    client.loop.run_until_complete(main())
