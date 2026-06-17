import os
import base64
from telethon import TelegramClient

session_data = base64.b64decode(os.environ["TELEGRAM_SESSION"])

with open("github_session.session", "wb") as f:
    f.write(session_data)

client = TelegramClient(
    "github_session",
    int(os.environ["TELEGRAM_API_ID"]),
    os.environ["TELEGRAM_API_HASH"]
)

file_id = os.environ["FILE_ID"]

async def main():
    await client.start()

    path = await client.download_media(file_id)

    print(f"Downloaded: {path}")

with client:
    client.loop.run_until_complete(main())
