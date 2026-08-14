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
# إنشاء Telegram Client
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

    # ==================================================
    # التأكد من الحساب
    # ==================================================

    try:

        me = await client.get_me()

        print("===================================")
        print("👤 Telegram Account")
        print("===================================")

        print(f"ID       : {me.id}")
        print(f"Username : @{me.username}" if me.username else "Username : None")
        print(f"Phone    : {me.phone}" if me.phone else "Phone    : None")

    except Exception as e:

        print("❌ فشل الحصول على معلومات الحساب.")
        print(f"Error: {e}")

        return


    # ==================================================
    # محاولة الحصول على Chat الرسالة المحولة
    # ==================================================

    print("===================================")
    print("🔎 فحص محادثة الرسالة المحولة")
    print("===================================")

    try:

        chat_entity = await client.get_entity(CHAT_ID)

        print("✅ تم العثور على المحادثة.")

        print(f"Chat ID   : {getattr(chat_entity, 'id', None)}")
        print(f"Chat type : {type(chat_entity).__name__}")

        if hasattr(chat_entity, "title"):
            print(f"Title     : {chat_entity.title}")

        if hasattr(chat_entity, "username"):
            print(f"Username  : {chat_entity.username}")

    except Exception as e:

        print("❌ لا يمكن الوصول إلى CHAT_ID.")
        print(f"Error: {e}")

        chat_entity = None


    # ==================================================
    # البحث عن الرسالة المحولة
    # ==================================================

    forwarded_message = None

    if chat_entity is not None:

        try:

            print("===================================")
            print("🔎 البحث عن الرسالة المحولة")
            print("===================================")

            forwarded_message = await client.get_messages(
                chat_entity,
                ids=MESSAGE_ID
            )

            if forwarded_message:

                print("✅ تم العثور على الرسالة المحولة.")

                print(f"Message ID : {forwarded_message.id}")
                print(f"Date       : {forwarded_message.date}")
                print(f"Text       : {forwarded_message.text}")

                if forwarded_message.media:

                    print("Media      : نعم")

                else:

                    print("Media      : لا")

            else:

                print("⚠️ لم يتم العثور على الرسالة المحولة.")

        except Exception as e:

            print("⚠️ حدث خطأ أثناء الحصول على الرسالة المحولة.")
            print(f"Error: {e}")


    # ==================================================
    # الوصول إلى القناة الأصلية
    # ==================================================

    source_entity = None

    print("===================================")
    print("🔎 البحث عن القناة الأصلية")
    print("===================================")


    # ==================================================
    # أولاً بواسطة username
    # ==================================================

    if SOURCE_USERNAME:

        try:

            username = SOURCE_USERNAME

            if username.startswith("@"):
                username = username[1:]

            print(
                f"🔎 محاولة الوصول بواسطة username: @{username}"
            )

            source_entity = await client.get_entity(
                username
            )

            print("✅ تم العثور على القناة بواسطة username.")

            print(
                f"Source entity ID: "
                f"{getattr(source_entity, 'id', None)}"
            )

            print(
                f"Source title: "
                f"{getattr(source_entity, 'title', None)}"
            )

            print(
                f"Source username: "
                f"{getattr(source_entity, 'username', None)}"
            )

        except Exception as e:

            print("⚠️ فشل الوصول بواسطة username.")
            print(f"Error: {e}")


    # ==================================================
    # التأكد من تطابق ID
    # ==================================================

    if source_entity is not None:

        actual_source_id = getattr(
            source_entity,
            "id",
            None
        )

        print("===================================")
        print("🔎 التحقق من Source Chat ID")
        print("===================================")

        print(f"Expected ID : {SOURCE_CHAT_ID}")
        print(f"Actual ID   : {actual_source_id}")

        # --------------------------------------------------
        # Telegram قد يعرض ID القناة بصيغة مختلفة حسب السياق.
        # لذلك لا نرفض entity فقط بسبب اختلاف الصيغة هنا.
        # --------------------------------------------------


    # ==================================================
    # إذا فشل username نبحث في dialogs
    # ==================================================

    if source_entity is None:

        try:

            print("🔎 البحث في المحادثات الموجودة في الحساب...")

            async for dialog in client.iter_dialogs():

                if dialog.id == SOURCE_CHAT_ID:

                    source_entity = dialog.entity

                    print(
                        "✅ تم العثور على القناة بواسطة chat_id."
                    )

                    print(
                        f"Title: {dialog.name}"
                    )

                    print(
                        f"ID: {dialog.id}"
                    )

                    break

        except Exception as e:

            print("⚠️ فشل البحث في dialogs.")
            print(f"Error: {e}")


    # ==================================================
    # إذا لم نجد القناة
    # ==================================================

    if source_entity is None:

        print("===================================")
        print("❌ لم يتم العثور على القناة الأصلية")
        print("===================================")

        print(f"SOURCE_CHAT_ID : {SOURCE_CHAT_ID}")
        print(f"SOURCE_USERNAME: {SOURCE_USERNAME}")

        print()
        print("الأسباب المحتملة:")
        print("1. الحساب ليس عضوًا في القناة.")
        print("2. username غير صحيح.")
        print("3. القناة خاصة.")
        print("4. الحساب لا يستطيع الوصول إلى القناة.")
        print("5. SOURCE_CHAT_ID غير صحيح.")

        return


    # ==================================================
    # الحصول على الرسالة الأصلية
    # ==================================================

    print("===================================")
    print("🔎 البحث عن الرسالة الأصلية")
    print("===================================")

    try:

        original_message = await client.get_messages(
            source_entity,
            ids=SOURCE_MESSAGE_ID
        )

    except Exception as e:

        print("❌ فشل الحصول على الرسالة الأصلية.")
        print(f"Error: {e}")

        return


    # ==================================================
    # التأكد من وجود الرسالة
    # ==================================================

    if not original_message:

        print("===================================")
        print("❌ الرسالة الأصلية غير موجودة")
        print("===================================")

        print(
            f"Source chat ID    : {SOURCE_CHAT_ID}"
        )

        print(
            f"Source message ID : {SOURCE_MESSAGE_ID}"
        )

        return


    # ==================================================
    # عرض معلومات الرسالة الأصلية
    # ==================================================

    print("===================================")
    print("✅ تم العثور على الرسالة الأصلية")
    print("===================================")

    print(
        f"Original ID   : {original_message.id}"
    )

    print(
        f"Original date : {original_message.date}"
    )

    print(
        f"Original text : {original_message.text}"
    )


    # ==================================================
    # فحص الوسائط
    # ==================================================

    if original_message.media:

        print("===================================")
        print("📦 الرسالة تحتوي على Media")
        print("===================================")

        print(
            f"Media type: "
            f"{type(original_message.media).__name__}"
        )

    else:

        print("⚠️ الرسالة الأصلية لا تحتوي على Media.")


    # ==================================================
    # النهاية
    # ==================================================

    print("===================================")
    print("✅ انتهى العمل بنجاح")
    print("===================================")


# ==================================================
# تشغيل Worker
# ==================================================

with client:

    client.loop.run_until_complete(main())
