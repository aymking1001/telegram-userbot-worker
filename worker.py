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

FORWARD_CHAT_ID = int(os.environ["CHAT_ID"])
FORWARD_MESSAGE_ID = int(os.environ["MESSAGE_ID"])


async def main():
    await client.start()

    # 1. الحصول على الرسالة المحولة
    forwarded_message = await client.get_messages(
        FORWARD_CHAT_ID,
        ids=FORWARD_MESSAGE_ID
    )

    if not forwarded_message:
        raise Exception("Forwarded message not found")

    print("Forwarded message found")

    # 2. التأكد أنها رسالة محولة
    if not forwarded_message.fwd_from:
        raise Exception("This message is not forwarded")

    forward = forwarded_message.fwd_from

    # 3. الحصول على معلومات الرسالة الأصلية
    original_message_id = forward.channel_post

    if not original_message_id:
        raise Exception("Original message ID not found")

    # 4. الحصول على القناة الأصلية
    original_channel = await client.get_entity(forward.from_id)

    print(f"Original channel: {original_channel.id}")
    print(f"Original message ID: {original_message_id}")

    # 5. الحصول على الرسالة الأصلية
    original_message = await client.get_messages(
        original_channel,
        ids=original_message_id
    )

    if not original_message:
        raise Exception("Original message not found")

    print("Original message found")

    # 6. تحميل الملف إن وجد
    path = await original_message.download_media()

    if path:
        print(f"Downloaded: {path}")
    else:
        print("Original message has no downloadable media")


with client:
    client.loop.run_until_complete(main())
