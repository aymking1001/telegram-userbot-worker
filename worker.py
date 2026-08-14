import os
from telethon import TelegramClient
from telethon.sessions import StringSession


# ==================================================
# معلومات Telegram
# ==================================================

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]


# ==================================================
# الرسالة المحولة الموجودة في محادثة الاستقبال
# ==================================================

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])


# ==================================================
# معلومات الرسالة الأصلية
# ==================================================

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])
SOURCE_USERNAME = os.environ.get("SOURCE_USERNAME", "").strip()


# ==================================================
# إنشاء Telegram Client باستخدام StringSession
# ==================================================

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


async def main():

    print("===================================")
    print("🚀 بدء Worker")
    print("===================================")

    print(f"Forwarded chat ID : {CHAT_ID}")
    print(f"Forwarded message : {MESSAGE_ID}")

    print(f"Source chat ID    : {SOURCE_CHAT_ID}")
    print(f"Source message ID : {SOURCE_MESSAGE_ID}")
    print(f"Source username   : {SOURCE_USERNAME}")

    # --------------------------------------------------
    # الحصول على الرسالة المحولة
    # --------------------------------------------------

    try:

        print("🔎 البحث عن الرسالة المحولة...")

        forwarded_message = await client.get_messages(
            CHAT_ID,
            ids=MESSAGE_ID
        )

    except Exception as e:

        print("❌ فشل الحصول على الرسالة المحولة.")
        print(f"Error: {e}")

        return

    if not forwarded_message:

        print("❌ لم يتم العثور على الرسالة المحولة.")

        return

    print(f"✅ تم العثور على الرسالة المحولة: {forwarded_message.id}")


    # --------------------------------------------------
    # الوصول إلى القناة الأصلية
    # --------------------------------------------------

    source_entity = None


    # --------------------------------------------------
    # أولاً نحاول باستخدام username
    # --------------------------------------------------

    if SOURCE_USERNAME:

        try:

            print("🔎 محاولة الوصول إلى القناة بواسطة username...")

            source_entity = await client.get_entity(
                SOURCE_USERNAME
            )

            print("✅ تم العثور على القناة بواسطة username.")

        except Exception as e:

            print("⚠️ فشل الوصول بواسطة username.")
            print(f"Error: {e}")


    # --------------------------------------------------
    # إذا فشل username نحاول باستخدام ID
    # --------------------------------------------------

    if source_entity is None:

        try:

            print("🔎 محاولة الوصول إلى القناة بواسطة chat_id...")

            async for dialog in client.iter_dialogs():

                if dialog.id == SOURCE_CHAT_ID:

                    source_entity = dialog.entity

                    print("✅ تم العثور على القناة بواسطة chat_id.")

                    break

        except Exception as e:

            print("⚠️ فشل البحث بواسطة chat_id.")
            print(f"Error: {e}")


    # --------------------------------------------------
    # التأكد من أننا وجدنا القناة
    # --------------------------------------------------

    if source_entity is None:

        print("===================================")
        print("❌ لم يتم العثور على القناة الأصلية.")
        print("===================================")

        print("SOURCE_CHAT_ID:", SOURCE_CHAT_ID)
        print("SOURCE_USERNAME:", SOURCE_USERNAME)

        return


    print("===================================")
    print("✅ تم العثور على القناة الأصلية")
    print("===================================")

    print(f"Entity: {source_entity}")


    # --------------------------------------------------
    # الحصول على الرسالة الأصلية
    # --------------------------------------------------

    try:

        print("🔎 البحث عن الرسالة الأصلية...")

        original_message = await client.get_messages(
            source_entity,
            ids=SOURCE_MESSAGE_ID
        )

    except Exception as e:

        print("❌ فشل الحصول على الرسالة الأصلية.")
        print(f"Error: {e}")

        return


    # --------------------------------------------------
    # التأكد من وجود الرسالة
    # --------------------------------------------------

    if not original_message:

        print("❌ الرسالة الأصلية غير موجودة.")

        return


    # --------------------------------------------------
    # عرض معلومات الرسالة الأصلية
    # --------------------------------------------------

    print("===================================")
    print("✅ تم العثور على الرسالة الأصلية")
    print("===================================")

    print(f"Original ID   : {original_message.id}")
    print(f"Original date : {original_message.date}")
    print(f"Original text : {original_message.text}")


    # --------------------------------------------------
    # فحص الوسائط
    # --------------------------------------------------

    if original_message.media:

        print("Original message contains media.")

    else:

        print("Original message has no media.")


    print("===================================")
    print("✅ انتهى العمل بنجاح")
    print("===================================")


# ==================================================
# تشغيل Worker
# ==================================================

with client:

    client.loop.run_until_complete(main())
