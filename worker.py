import os
import base64
from telethon import TelegramClient

# =========================
# Load session
# =========================
session_data = base64.b64decode(
    os.environ["TELEGRAM_SESSION"]
)

with open("github_session.session", "wb") as f:
    f.write(session_data)

# =========================
# Client
# =========================
client = TelegramClient(
    "github_session",
    int(os.environ["TELEGRAM_API_ID"]),
    os.environ["TELEGRAM_API_HASH"]
)

chat_id = int(os.environ["CHAT_ID"])
message_id = int(os.environ["MESSAGE_ID"])


# =========================
# Main logic
# =========================
async def main():
    await client.start()

    # مهم جدًا: تحميل الجلسة + التعرف على القنوات
    await client.get_dialogs()

    # تحويل chat_id إلى entity (حل PeerChannel error)
    entity = await client.get_entity(chat_id)

    # جلب الرسالة بشكل آمن
    message = await client.get_messages(
        entity,
        ids=int(message_id)
    )

    if not message:
        raise Exception("Message not found")

    # تحميل الميديا
    path = await message.download_media()

    print(f"Downloaded: {path}")


# =========================
# Run
# =========================
with client:
    client.loop.run_until_complete(main())
