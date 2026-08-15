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

    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError(
            "TELEGRAM_SESSION غير صالح أو منتهي."
        )

    print("Telegram connected successfully.")

    # جلب الرسالة الأصلية
    print(
        f"Searching for source message "
        f"{SOURCE_MESSAGE_ID} in chat {SOURCE_CHAT_ID}..."
    )

    message = await client.get_messages(
        SOURCE_CHAT_ID,
        ids=SOURCE_MESSAGE_ID
    )

    if not message:
        raise RuntimeError(
            f"لم يتم العثور على الرسالة "
            f"{SOURCE_MESSAGE_ID} في المحادثة "
            f"{SOURCE_CHAT_ID}"
        )

    print(f"Source message found: {message.id}")

    # الانتظار 3 دقائق
    print("Waiting 3 minutes before forwarding...")

    await asyncio.sleep(180)

    # إعادة توجيه الرسالة
    print(
        f"Forwarding message {message.id} "
        f"to {CHAT_ID}..."
    )

    await client.forward_messages(
        entity=CHAT_ID,
        messages=message,
        from_peer=SOURCE_CHAT_ID
    )

    print("Message forwarded successfully.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
