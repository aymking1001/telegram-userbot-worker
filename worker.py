import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])


async def main():

    client = TelegramClient(
        StringSession(SESSION),
        API_ID,
        API_HASH
    )

    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError("TELEGRAM_SESSION غير صالحة.")

    print("Telegram connected successfully.")

    # البحث عن الرسالة المحوّلة
    message = await client.get_messages(
        CHAT_ID,
        ids=MESSAGE_ID
    )

    if not message:
        raise RuntimeError(
            f"لم يتم العثور على الرسالة {MESSAGE_ID} في المحادثة {CHAT_ID}"
        )

    print(f"Forwarded message found: {message.id}")

    # عرض معلومات المصدر إن كانت الرسالة Forward
    if message.forward:
        print("This message is forwarded.")

        if message.forward.chat:
            print(f"Original chat: {message.forward.chat.id}")

        print(f"Original message ID: {message.forward.channel_post}")

    # انتظار 3 دقائق
    print("Waiting 3 minutes before sending...")
    await asyncio.sleep(180)

    # إعادة إرسال الرسالة المحوّلة
    await client.forward_messages(
        entity=CHAT_ID,
        messages=message
    )

    print("Message forwarded successfully.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
