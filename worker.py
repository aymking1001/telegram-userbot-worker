import os
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])

SOURCE_USERNAME = os.environ.get("SOURCE_USERNAME", "")


async def main():
    print("===================================")
    print("🚀 بدء Worker")
    print("===================================")

    print(f"Forwarded chat ID    : {CHAT_ID}")
    print(f"Forwarded message ID : {MESSAGE_ID}")
    print(f"Source chat ID       : {SOURCE_CHAT_ID}")
    print(f"Source message ID    : {SOURCE_MESSAGE_ID}")
    print(f"Source username      : {SOURCE_USERNAME}")

    client = TelegramClient(
        "worker_session",
        API_ID,
        API_HASH
    )

    await client.start()

    me = await client.get_me()

    print("===================================")
    print("👤 Telegram Account")
    print("===================================")

    print(f"ID       : {me.id}")
    print(f"Username : @{me.username}")
    print(f"Phone    : {me.phone}")

    # --------------------------------------------------
    # البحث عن الرسالة المحولة
    # --------------------------------------------------

    print("===================================")
    print("🔎 البحث عن الرسالة المحولة")
    print("===================================")

    try:
        forwarded_message = await client.get_messages(
            CHAT_ID,
            ids=MESSAGE_ID
        )

        if forwarded_message is None:
            print("❌ الرسالة المحولة غير موجودة.")
            print(f"CHAT_ID    : {CHAT_ID}")
            print(f"MESSAGE_ID : {MESSAGE_ID}")

        else:
            print("✅ تم العثور على الرسالة المحولة.")
            print(f"Message ID : {forwarded_message.id}")

            if forwarded_message.fwd_from:
                print("✅ الرسالة تحتوي على معلومات Forward.")

                print(
                    f"From channel ID : "
                    f"{getattr(forwarded_message.fwd_from, 'from_id', None)}"
                )

            else:
                print("⚠️ الرسالة ليست Forward.")

    except RPCError as e:
        print("❌ خطأ أثناء البحث عن الرسالة المحولة:")
        print(e)

    # --------------------------------------------------
    # البحث عن الرسالة الأصلية
    # --------------------------------------------------

    print("===================================")
    print("🔎 البحث عن الرسالة الأصلية")
    print("===================================")

    try:
        source_message = await client.get_messages(
            SOURCE_CHAT_ID,
            ids=SOURCE_MESSAGE_ID
        )

        if source_message is None:
            print("❌ الرسالة الأصلية غير موجودة.")
            print(f"SOURCE_CHAT_ID    : {SOURCE_CHAT_ID}")
            print(f"SOURCE_MESSAGE_ID : {SOURCE_MESSAGE_ID}")

        else:
            print("✅ تم العثور على الرسالة الأصلية.")

            print(f"Message ID : {source_message.id}")
            print(f"Chat ID    : {SOURCE_CHAT_ID}")

            if source_message.message:
                print("Text:")
                print(source_message.message[:500])

            if source_message.media:
                print("📎 الرسالة تحتوي على Media.")

    except RPCError as e:
        print("❌ خطأ أثناء البحث عن الرسالة الأصلية:")
        print(e)

    # --------------------------------------------------
    # إنهاء
    # --------------------------------------------------

    await client.disconnect()

    print("===================================")
    print("🏁 انتهاء Worker")
    print("===================================")


if __name__ == "__main__":
    asyncio.run(main())
