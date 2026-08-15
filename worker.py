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
SOURCE_USERNAME = os.environ["SOURCE_USERNAME"]


async def main():
    client = TelegramClient("worker", API_ID, API_HASH)

    await client.start()

    print("===================================")
    print("🚀 بدء Worker")
    print("===================================")

    print(f"Forwarded chat ID    : {CHAT_ID}")
    print(f"Forwarded message ID : {MESSAGE_ID}")
    print(f"Source chat ID       : {SOURCE_CHAT_ID}")
    print(f"Source message ID    : {SOURCE_MESSAGE_ID}")
    print(f"Source username      : {SOURCE_USERNAME}")

    print("===================================")
    print("🔐 إنشاء اتصال Telegram")
    print("===================================")

    me = await client.get_me()

    print("===================================")
    print("👤 Telegram Account")
    print("===================================")
    print(f"ID       : {me.id}")
    print(f"Username : @{me.username}")
    print(f"Phone    : {me.phone}")
    print("===================================")

    print("🔎 تحميل Source Entity")
    print("===================================")

    print(f"🔎 محاولة الوصول إلى: @{SOURCE_USERNAME}")

    source_entity = await client.get_entity(SOURCE_USERNAME)

    print("✅ تم العثور على Source Entity")
    print(f"Entity ID: {source_entity.id}")

    print("===================================")
    print("🔎 البحث عن الرسالة الأصلية")
    print("===================================")

    message = await client.get_messages(
        source_entity,
        ids=SOURCE_MESSAGE_ID
    )

    if message:
        print("✅ تم العثور على الرسالة الأصلية.")
        print(f"Message ID : {message.id}")
        print(f"Chat ID    : {source_entity.id}")

        if message.text:
            print("Text:")
            print(message.text)

        if message.media:
            print("📎 الرسالة تحتوي على Media.")
            print(f"Media type: {type(message.media).__name__}")

    else:
        print("❌ لم يتم العثور على الرسالة الأصلية.")

    # ===================================
    # الانتظار 3 دقائق
    # ===================================

    print("===================================")
    print("⏳ انتظار 3 دقائق قبل البحث عن الرسالة المحولة")
    print("===================================")

    await asyncio.sleep(180)

    print("===================================")
    print("🔎 البحث عن الرسالة المحولة")
    print("===================================")

    forwarded_message = await client.get_messages(
        CHAT_ID,
        ids=MESSAGE_ID
    )

    if forwarded_message:
        print("✅ تم العثور على الرسالة المحولة.")
        print(f"Message ID : {forwarded_message.id}")
        print(f"Chat ID    : {CHAT_ID}")

        if forwarded_message.text:
            print("Text:")
            print(forwarded_message.text)

        if forwarded_message.media:
            print("📎 الرسالة المحولة تحتوي على Media.")
            print(
                f"Media type: "
                f"{type(forwarded_message.media).__name__}"
            )

    else:
        print("❌ الرسالة المحولة غير موجودة.")
        print(f"CHAT_ID    : {CHAT_ID}")
        print(f"MESSAGE_ID : {MESSAGE_ID}")

    print("===================================")
    print("🏁 انتهاء Worker")
    print("===================================")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
