import os
import asyncio
from telethon import TelegramClient


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

CHAT_ID = int(os.environ["CHAT_ID"])

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])


async def main():

    client = TelegramClient(
        "worker_session",
        API_ID,
        API_HASH
    )

    # الاتصال باستخدام Session الموجودة في GitHub Secrets
    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError(
            "TELEGRAM_SESSION غير صالح أو منتهي."
        )

    print("Telegram connected successfully.")

    # الحصول على الرسالة الأصلية
    print(
        f"Getting source message: "
        f"{SOURCE_MESSAGE_ID} "
        f"from {SOURCE_CHAT_ID}"
    )

    message = await client.get_messages(
        SOURCE_CHAT_ID,
        ids=SOURCE_MESSAGE_ID
    )

    if not message:
        raise RuntimeError(
            f"لم يتم العثور على الرسالة "
            f"{SOURCE_MESSAGE_ID} "
            f"في المحادثة {SOURCE_CHAT_ID}"
        )

    print(f"Source message found: {message.id}")

    # الانتظار 3 دقائق
    print("Waiting 3 minutes before forwarding...")

    await asyncio.sleep(180)

    # إعادة إرسال الرسالة إلى CHAT_ID
    print(f"Forwarding message to {CHAT_ID}...")

    sent_message = await client.forward_messages(
        entity=CHAT_ID,
        messages=message
    )

    print(
        f"Message forwarded successfully. "
        f"New message ID: {sent_message.id}"
    )

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
