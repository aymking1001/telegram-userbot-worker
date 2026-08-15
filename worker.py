import os
from telethon import TelegramClient
from telethon.sessions import StringSession


# ============================================================
# Telegram
# ============================================================

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]


# ============================================================
# الرسالة المحولة
# ============================================================

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])


# ============================================================
# معلومات الرسالة الأصلية القادمة من n8n
# ============================================================

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])
SOURCE_USERNAME = os.environ.get("SOURCE_USERNAME", "").strip()


# ============================================================
# Telegram Client
# ============================================================

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


# ============================================================
# أدوات مساعدة
# ============================================================

def normalize_channel_id(value):
    """
    يحول Telegram Channel ID إلى الشكل -100xxxxxxxxxx
    عند الحاجة.
    """
    value = int(value)

    if value < 0:
        return value

    # إذا كان ID قناة بدون -100
    if len(str(value)) >= 10:
        return int(f"-100{value}")

    return value


def print_entity(entity, name="Entity"):

    print("-----------------------------------")
    print(f"{name}")
    print("-----------------------------------")

    print(f"Type     : {type(entity).__name__}")
    print(f"ID       : {getattr(entity, 'id', None)}")
    print(f"Title    : {getattr(entity, 'title', None)}")
    print(f"Username : {getattr(entity, 'username', None)}")


def print_message(message, name="Message"):

    print("-----------------------------------")
    print(f"{name}")
    print("-----------------------------------")

    if message is None:
        print("❌ None")
        return

    print(f"ID       : {message.id}")
    print(f"Date     : {message.date}")
    print(f"Text     : {message.text}")

    print(
        f"Media    : "
        f"{'YES' if message.media else 'NO'}"
    )

    if message.media:
        print(
            f"MediaType: "
            f"{type(message.media).__name__}"
        )

    print(
        f"Forward  : "
        f"{'YES' if message.fwd_from else 'NO'}"
    )


# ============================================================
# Main
# ============================================================

async def main():

    print("===================================")
    print("🚀 Telegram Worker")
    print("===================================")

    print(f"CHAT_ID           : {CHAT_ID}")
    print(f"MESSAGE_ID        : {MESSAGE_ID}")
    print(f"SOURCE_CHAT_ID    : {SOURCE_CHAT_ID}")
    print(f"SOURCE_MESSAGE_ID : {SOURCE_MESSAGE_ID}")
    print(f"SOURCE_USERNAME   : {SOURCE_USERNAME}")

    # ========================================================
    # تسجيل الدخول
    # ========================================================

    try:

        me = await client.get_me()

        print("===================================")
        print("👤 الحساب")
        print("===================================")

        print(f"ID       : {me.id}")
        print(
            f"Username : @{me.username}"
            if me.username
            else "Username : None"
        )

    except Exception as e:

        print("❌ فشل تسجيل الدخول")
        print(f"Error: {e}")

        return


    # ========================================================
    # الحصول على Chat الرسالة المحولة
    # ========================================================

    print("===================================")
    print("🔎 البحث عن محادثة الرسالة المحولة")
    print("===================================")

    try:

        forwarded_chat = await client.get_entity(CHAT_ID)

        print("✅ تم العثور على المحادثة")

        print_entity(
            forwarded_chat,
            "Forwarded Chat"
        )

    except Exception as e:

        print("❌ فشل الوصول إلى CHAT_ID")
        print(f"CHAT_ID: {CHAT_ID}")
        print(f"Error: {e}")

        return


    # ========================================================
    # الحصول على الرسالة المحولة
    # ========================================================

    print("===================================")
    print("🔎 الحصول على الرسالة المحولة")
    print("===================================")

    try:

        forwarded_message = await client.get_messages(
            forwarded_chat,
            ids=MESSAGE_ID
        )

    except Exception as e:

        print("❌ خطأ أثناء الحصول على الرسالة المحولة")
        print(f"Error: {e}")

        return


    # ========================================================
    # التأكد من وجود Forwarded Message
    # ========================================================

    if not forwarded_message:

        print("===================================")
        print("❌ الرسالة المحولة غير موجودة")
        print("===================================")

        print(f"CHAT_ID    : {CHAT_ID}")
        print(f"MESSAGE_ID : {MESSAGE_ID}")

        print()
        print("⚠️ السبب المحتمل:")
        print(
            "MESSAGE_ID لا ينتمي إلى CHAT_ID الذي يتم استخدامه."
        )

        return


    print_message(
        forwarded_message,
        "📨 Forwarded Message"
    )


    # ========================================================
    # التحقق من أن الرسالة Forward فعلاً
    # ========================================================

    print("===================================")
    print("🔎 التحقق من Forward")
    print("===================================")

    if not forwarded_message.fwd_from:

        print("❌ الرسالة ليست Forward")
        print(
            "لا توجد معلومات fwd_from داخل الرسالة."
        )

        return

    print("✅ الرسالة تحتوي على Forward information")


    # ========================================================
    # عرض معلومات Forward
    # ========================================================

    fwd = forwarded_message.fwd_from

    print("-----------------------------------")
    print("📦 Forward information")
    print("-----------------------------------")

    print(
        f"from_id       : "
        f"{getattr(fwd, 'from_id', None)}"
    )

    print(
        f"channel_id    : "
        f"{getattr(fwd, 'channel_id', None)}"
    )

    print(
        f"channel_post  : "
        f"{getattr(fwd, 'channel_post', None)}"
    )

    print(
        f"post_author   : "
        f"{getattr(fwd, 'post_author', None)}"
    )

    print(
        f"saved_from_id : "
        f"{getattr(fwd, 'saved_from_id', None)}"
    )

    print(
        f"saved_from_msg_id : "
        f"{getattr(fwd, 'saved_from_msg_id', None)}"
    )


    # ========================================================
    # استخراج ID الأصلي من Forward
    # ========================================================

    detected_source_id = None
    detected_source_message_id = None


    # --------------------------------------------------------
    # Channel post
    # --------------------------------------------------------

    if getattr(fwd, "channel_id", None):

        detected_source_id = int(fwd.channel_id)

        if getattr(fwd, "channel_post", None):

            detected_source_message_id = int(
                fwd.channel_post
            )


    # --------------------------------------------------------
    # Saved message
    # --------------------------------------------------------

    if (
        detected_source_id is None
        and getattr(fwd, "saved_from_id", None)
    ):

        saved_id = fwd.saved_from_id

        if hasattr(saved_id, "channel_id"):

            detected_source_id = int(
                saved_id.channel_id
            )

        elif hasattr(saved_id, "user_id"):

            detected_source_id = int(
                saved_id.user_id
            )

        if getattr(
            fwd,
            "saved_from_msg_id",
            None
        ):

            detected_source_message_id = int(
                fwd.saved_from_msg_id
            )


    # ========================================================
    # عرض الـ IDs المستخرجة
    # ========================================================

    print("===================================")
    print("🧩 IDs المستخرجة من Forward")
    print("===================================")

    print(
        f"Detected Source ID         : "
        f"{detected_source_id}"
    )

    print(
        f"Detected Source Message ID : "
        f"{detected_source_message_id}"
    )


    # ========================================================
    # البحث عن المصدر
    # ========================================================

    source_entity = None


    # --------------------------------------------------------
    # أولاً: المصدر المستخرج من Forward
    # --------------------------------------------------------

    if detected_source_id:

        print("===================================")
        print("🔎 البحث عن المصدر من Forward")
        print("===================================")

        possible_ids = [
            detected_source_id,
            normalize_channel_id(
                detected_source_id
            )
        ]

        for source_id in possible_ids:

            try:

                print(
                    f"محاولة ID: {source_id}"
                )

                source_entity = await client.get_entity(
                    source_id
                )

                if source_entity:

                    print(
                        "✅ تم العثور على المصدر"
                    )

                    print_entity(
                        source_entity,
                        "Source Entity"
                    )

                    break

            except Exception as e:

                print(
                    f"⚠️ فشل ID {source_id}: {e}"
                )


    # --------------------------------------------------------
    # ثانياً: username
    # --------------------------------------------------------

    if source_entity is None and SOURCE_USERNAME:

        print("===================================")
        print("🔎 البحث بواسطة Username")
        print("===================================")

        username = SOURCE_USERNAME.lstrip("@")

        try:

            source_entity = await client.get_entity(
                username
            )

            print(
                "✅ تم العثور على المصدر بواسطة username"
            )

            print_entity(
                source_entity,
                "Source Entity"
            )

        except Exception as e:

            print(
                "⚠️ فشل البحث بواسطة username"
            )

            print(
                f"Username: @{username}"
            )

            print(
                f"Error: {e}"
            )


    # --------------------------------------------------------
    # ثالثاً: SOURCE_CHAT_ID
    # --------------------------------------------------------

    if source_entity is None:

        print("===================================")
        print("🔎 البحث باستخدام SOURCE_CHAT_ID")
        print("===================================")

        ids_to_try = [
            SOURCE_CHAT_ID,
            normalize_channel_id(
                SOURCE_CHAT_ID
            )
        ]

        for source_id in ids_to_try:

            try:

                source_entity = await client.get_entity(
                    source_id
                )

                if source_entity:

                    print(
                        "✅ تم العثور على المصدر"
                    )

                    print_entity(
                        source_entity,
                        "Source Entity"
                    )

                    break

            except Exception as e:

                print(
                    f"⚠️ فشل ID {source_id}: {e}"
                )


    # ========================================================
    # لم نجد المصدر
    # ========================================================

    if source_entity is None:

        print("===================================")
        print("❌ لم يتم العثور على المصدر")
        print("===================================")

        print(
            f"SOURCE_CHAT_ID  : {SOURCE_CHAT_ID}"
        )

        print(
            f"SOURCE_USERNAME : {SOURCE_USERNAME}"
        )

        print(
            f"Detected ID     : {detected_source_id}"
        )

        return


    # ========================================================
    # تحديد Message ID الحقيقي
    # ========================================================

    original_message_id = (
        detected_source_message_id
        or SOURCE_MESSAGE_ID
    )


    print("===================================")
    print("🎯 Message ID النهائي")
    print("===================================")

    print(
        f"Original Message ID: "
        f"{original_message_id}"
    )


    # ========================================================
    # الحصول على الرسالة الأصلية
    # ========================================================

    print("===================================")
    print("🔎 البحث عن الرسالة الأصلية")
    print("===================================")

    try:

        original_message = await client.get_messages(
            source_entity,
            ids=original_message_id
        )

    except Exception as e:

        print(
            "❌ فشل الحصول على الرسالة الأصلية"
        )

        print(
            f"Error: {e}"
        )

        return


    # ========================================================
    # التأكد من الرسالة الأصلية
    # ========================================================

    if not original_message:

        print("===================================")
        print("❌ الرسالة الأصلية غير موجودة")
        print("===================================")

        print(
            f"Source Entity ID : "
            f"{getattr(source_entity, 'id', None)}"
        )

        print(
            f"Message ID       : "
            f"{original_message_id}"
        )

        return


    # ========================================================
    # عرض الرسالة الأصلية
    # ========================================================

    print_message(
        original_message,
        "📄 Original Message"
    )


    # ========================================================
    # التحقق من Media
    # ========================================================

    print("===================================")
    print("📦 فحص Media")
    print("===================================")

    if original_message.media:

        print("✅ الرسالة الأصلية تحتوي على Media")

        print(
            f"Media type: "
            f"{type(original_message.media).__name__}"
        )

        # ----------------------------------------------------
        # معلومات الملف إذا كانت متوفرة
        # ----------------------------------------------------

        if original_message.file:

            print(
                f"File name : "
                f"{original_message.file.name}"
            )

            print(
                f"File size : "
                f"{original_message.file.size}"
            )

            print(
                f"MIME type : "
                f"{original_message.file.mime_type}"
            )

    else:

        print(
            "⚠️ الرسالة الأصلية لا تحتوي على Media"
        )


    # ========================================================
    # مقارنة الـ Forward مع Original
    # ========================================================

    print("===================================")
    print("🔗 التحقق النهائي")
    print("===================================")

    print(
        f"Forwarded message ID : "
        f"{forwarded_message.id}"
    )

    print(
        f"Original message ID  : "
        f"{original_message.id}"
    )

    print(
        f"Original source ID   : "
        f"{getattr(source_entity, 'id', None)}"
    )


    # ========================================================
    # مقارنة Media
    # ========================================================

    if (
        forwarded_message.media
        and original_message.media
    ):

        print(
            "✅ Forward يحتوي Media "
            "و Original يحتوي Media"
        )

    elif original_message.media:

        print(
            "⚠️ Original يحتوي Media "
            "لكن Forward لا يحتوي Media"
        )

    else:

        print(
            "ℹ️ Original لا يحتوي Media"
        )


    # ========================================================
    # النهاية
    # ========================================================

    print("===================================")
    print("✅ انتهى Worker بنجاح")
    print("===================================")


# ============================================================
# تشغيل
# ============================================================

with client:

    client.loop.run_until_complete(
        main()
    )
