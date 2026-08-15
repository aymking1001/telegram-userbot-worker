import os
import asyncio
from telethon import TelegramClient


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])


async def main():
    client = TelegramClient(
        "worker_session",
        API_ID,
        API_HASH
    )

    # استخدام Session موجود مسبقًا
    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError(
            "TELEGRAM_SESSION غير صالح أو منتهي. "
            "يجب إنشاء Session صالح وإضافته إلى GitHub Secrets."
        )

    print("Telegram connected successfully.")

    # الحصول على الرسالة من المصدر
    message = await client.get_messages(
        SOURCE_CHAT_ID,
        ids=SOURCE_MESSAGE_ID
    )

    if not message:
        raise RuntimeError("لم يتم العثور على الرسالة المصدر.")

    print(f"Source message found: {message.id}")

    # انتظار 3 دقائق
    print("Waiting 3 minutes before sending...")
    await asyncio.sleep(180)

    # إعادة إرسال الرسالة
    await client.forward_messages(
        entity=CHAT_ID,
        messages=message
    )

    print("Message forwarded successfully.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
