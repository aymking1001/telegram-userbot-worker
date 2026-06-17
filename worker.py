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

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])

async def main():
    await client.start()

    message = await client.get_messages(CHAT_ID, ids=MESSAGE_ID)

    if not message:
        raise Exception("Message not found")

    path = await message.download_media()

    print(f"Downloaded: {path}")

with client:
    client.loop.run_until_complete(main())
