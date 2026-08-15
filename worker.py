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
# الرسالة الأصلية
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
# أدوات ID
# ============================================================

def normalize_channel_id(value):
    """
    Telethon:
        Channel entity ID = 1839480260

    Bot API style:
        Channel chat ID = -1001839480260

    نحول الاثنين إلى صيغة واحدة للمقارنة.
    """

    value = int(value)

    if value > 0:
        return -1000000000000 - value

    return value


def get_entity_id(entity):
    return getattr(entity, "id", None)


# ============================================================
# معلومات Media
# ============================================================

def print_media_info(message, label):

    print("-----------------------------------")
    print(f"📦 Media: {label}")
    print("-----------------------------------")

    if not message:
        print("❌ لا توجد رسالة.")
        return

    if not message.media:
        print("⚠️ لا توجد Media.")
        return

    print("✅ الرسالة تحتوي على Media.")

    print(
        f"Media class : "
        f"{type(message.media).__name__}"
    )

    # --------------------------------------------------------
    # Document
    # --------------------------------------------------------

    if message.document:

        document = message.document

        print("Media type : Document")

        print(
            f"Document ID : "
            f"{document.id}"
        )

        print(
            f"Size        : "
            f"{document.size}"
        )

        print(
            f"MIME type   : "
            f"{document.mime_type}"
        )

        print(
            f"Attributes  : "
            f"{document.attributes}"
        )

    # --------------------------------------------------------
    # Photo
    # --------------------------------------------------------

    elif message.photo:

        print("Media type : Photo")

        print(
            f"Photo ID : "
            f"{message.photo.id}"
        )

    else:

        print(
            f"Media type: "
            f"{type(message.media).__name__}"
        )


# ============================================================
# Main
# ============================================================

async def main():

    print()
    print("===================================")
    print("🚀 بدء Worker")
    print("===================================")

    print(
        f"Forwarded CHAT_ID     : {CHAT_ID}"
    )

    print(
        f"Forwarded MESSAGE_ID  : {MESSAGE_ID}"
    )

    print(
        f"Source CHAT_ID        : {SOURCE_CHAT_ID}"
    )

    print(
        f"Source MESSAGE_ID     : {SOURCE_MESSAGE_ID}"
    )

    print(
        f"Source USERNAME       : {SOURCE_USERNAME}"
    )


    # ========================================================
    # Account
    # ========================================================

    print()
    print("===================================")
    print("👤 Telegram Account")
    print("===================================")

    try:

        me = await client.get_me()

        print(
            f"ID       : {me.id}"
        )

        print(
            f"Username : "
            f"@{me.username}"
            if me.username
            else
            "Username : None"
        )

        print(
            f"Phone    : {me.phone}"
            if me.phone
            else
            "Phone    : None"
        )

    except Exception as e:

        print(
            "❌ فشل الحصول على معلومات الحساب."
        )

        print(
            f"Error: {type(e).__name__}: {e}"
        )

        return


    # ========================================================
    # الحصول على محادثة الرسالة المحولة
    # ========================================================

    print()
    print("===================================")
    print("🔎 فحص Forwarded Chat")
    print("===================================")

    try:

        forwarded_chat = await client.get_entity(
            CHAT_ID
        )

        print(
            "✅ تم العثور على محادثة الرسالة المحولة."
        )

        actual_chat_id = get_entity_id(
            forwarded_chat
        )

        print(
            f"Requested ID : {CHAT_ID}"
        )

        print(
            f"Entity ID    : {actual_chat_id}"
        )

        print(
            f"Entity type  : "
            f"{type(forwarded_chat).__name__}"
        )

        if hasattr(forwarded_chat, "title"):

            print(
                f"Title        : "
                f"{forwarded_chat.title}"
            )

        if hasattr(forwarded_chat, "username"):

            print(
                f"Username     : "
                f"{forwarded_chat.username}"
            )

    except Exception as e:

        print(
            "❌ لا يمكن الوصول إلى CHAT_ID."
        )

        print(
            f"Error: {type(e).__name__}: {e}"
        )

        return


    # ========================================================
    # الحصول على الرسالة المحولة
    # ========================================================

    print()
    print("===================================")
    print("🔎 البحث عن Forwarded Message")
    print("===================================")

    try:

        forwarded_message = await client.get_messages(
            forwarded_chat,
            ids=MESSAGE_ID
        )

    except Exception as e:

        print(
            "❌ فشل الحصول على الرسالة المحولة."
        )

        print(
            f"Error: {type(e).__name__}: {e}"
        )

        return


    if not forwarded_message:

        print(
            "❌ الرسالة المحولة غير موجودة."
        )

        print(
            f"CHAT_ID    : {CHAT_ID}"
        )

        print(
            f"MESSAGE_ID : {MESSAGE_ID}"
        )

        return


    # ========================================================
    # معلومات Forwarded Message
    # ========================================================

    print(
        "✅ تم العثور على الرسالة المحولة."
    )

    print(
        f"Message ID : "
        f"{forwarded_message.id}"
    )

    print(
        f"Date       : "
        f"{forwarded_message.date}"
    )

    print(
        f"Text       : "
        f"{forwarded_message.text}"
    )

    print(
        f"Media      : "
        f"{'نعم' if forwarded_message.media else 'لا'}"
    )


    # ========================================================
    # التحقق الحقيقي من Forward
    # ========================================================

    print()
    print("===================================")
    print("🔎 التحقق من Forward Header")
    print("===================================")

    fwd = forwarded_message.fwd_from

    if fwd is None:

        print(
            "❌ هذه الرسالة لا تحتوي على Forward Header."
        )

        print(
            "أي أن MESSAGE_ID لا يمثل Forward "
            "حقيقيًا حسب بيانات Telegram."
        )

    else:

        print(
            "✅ توجد معلومات Forward."
        )

        print(
            f"Forward header : {fwd}"
        )

        # ----------------------------------------------------
        # channel_post
        # ----------------------------------------------------

        channel_post = getattr(
            fwd,
            "channel_post",
            None
        )

        print(
            f"Forward channel_post : "
            f"{channel_post}"
        )

        # ----------------------------------------------------
        # from_id
        # ----------------------------------------------------

        from_id = getattr(
            fwd,
            "from_id",
            None
        )

        print(
            f"Forward from_id      : "
            f"{from_id}"
        )

        # ----------------------------------------------------
        # date
        # ----------------------------------------------------

        print(
            f"Original forward date: "
            f"{getattr(fwd, 'date', None)}"
        )

        # ----------------------------------------------------
        # مقارنة MESSAGE_ID
        # ----------------------------------------------------

        if channel_post is not None:

            if int(channel_post) == SOURCE_MESSAGE_ID:

                print(
                    "✅ Forward يشير إلى "
                    "SOURCE_MESSAGE_ID الصحيح."
                )

            else:

                print(
                    "❌ Forward يشير إلى رسالة أخرى."
                )

                print(
                    f"Expected SOURCE_MESSAGE_ID : "
                    f"{SOURCE_MESSAGE_ID}"
                )

                print(
                    f"Actual channel_post         : "
                    f"{channel_post}"
                )

        else:

            print(
                "⚠️ Forward Header لا يحتوي على "
                "channel_post."
            )


    # ========================================================
    # العثور على القناة الأصلية
    # ========================================================

    print()
    print("===================================")
    print("🔎 البحث عن Source Channel")
    print("===================================")

    source_entity = None


    # ========================================================
    # بواسطة username
    # ========================================================

    if SOURCE_USERNAME:

        username = SOURCE_USERNAME.lstrip("@").strip()

        try:

            print(
                f"🔎 محاولة الوصول إلى "
                f"@{username}"
            )

            source_entity = await client.get_entity(
                username
            )

            print(
                "✅ تم العثور على القناة بواسطة username."
            )

            actual_source_id = get_entity_id(
                source_entity
            )

            print(
                f"Entity ID        : "
                f"{actual_source_id}"
            )

            print(
                f"Normalized ID    : "
                f"{normalize_channel_id(actual_source_id)}"
            )

            print(
                f"Expected ID      : "
                f"{SOURCE_CHAT_ID}"
            )

            print(
                f"Expected normalized: "
                f"{normalize_channel_id(SOURCE_CHAT_ID)}"
            )

            print(
                f"Title             : "
                f"{getattr(source_entity, 'title', None)}"
            )

            print(
                f"Username          : "
                f"{getattr(source_entity, 'username', None)}"
            )

        except Exception as e:

            print(
                "⚠️ فشل الوصول إلى القناة بواسطة username."
            )

            print(
                f"Error: {type(e).__name__}: {e}"
            )


    # ========================================================
    # إذا لم ينجح username
    # ========================================================

    if source_entity is None:

        print()
        print(
            "🔎 البحث عن القناة داخل dialogs..."
        )

        try:

            expected_normalized = normalize_channel_id(
                SOURCE_CHAT_ID
            )

            async for dialog in client.iter_dialogs():

                dialog_id = int(dialog.id)

                if (
                    normalize_channel_id(dialog_id)
                    ==
                    expected_normalized
                ):

                    source_entity = dialog.entity

                    print(
                        "✅ تم العثور على القناة داخل dialogs."
                    )

                    print(
                        f"Dialog ID : "
                        f"{dialog.id}"
                    )

                    print(
                        f"Name      : "
                        f"{dialog.name}"
                    )

                    break

        except Exception as e:

            print(
                "⚠️ فشل البحث في dialogs."
            )

            print(
                f"Error: {type(e).__name__}: {e}"
            )


    # ========================================================
    # لم نجد القناة
    # ========================================================

    if source_entity is None:

        print()
        print("===================================")
        print("❌ لم يتم العثور على Source Channel")
        print("===================================")

        print(
            f"SOURCE_CHAT_ID : "
            f"{SOURCE_CHAT_ID}"
        )

        print(
            f"SOURCE_USERNAME: "
            f"{SOURCE_USERNAME}"
        )

        return


    # ========================================================
    # التحقق من Source ID
    # ========================================================

    print()
    print("===================================")
    print("🔎 التحقق من Source Chat ID")
    print("===================================")

    actual_source_id = get_entity_id(
        source_entity
    )

    expected_normalized = normalize_channel_id(
        SOURCE_CHAT_ID
    )

    actual_normalized = normalize_channel_id(
        actual_source_id
    )

    print(
        f"Expected raw ID      : "
        f"{SOURCE_CHAT_ID}"
    )

    print(
        f"Actual entity ID     : "
        f"{actual_source_id}"
    )

    print(
        f"Expected normalized  : "
        f"{expected_normalized}"
    )

    print(
        f"Actual normalized    : "
        f"{actual_normalized}"
    )

    if expected_normalized == actual_normalized:

        print(
            "✅ Source Chat ID مطابق."
        )

    else:

        print(
            "❌ Source Chat ID غير مطابق."
        )

        return


    # ========================================================
    # الحصول على الرسالة الأصلية
    # ========================================================

    print()
    print("===================================")
    print("🔎 البحث عن Original Message")
    print("===================================")

    try:

        original_message = await client.get_messages(
            source_entity,
            ids=SOURCE_MESSAGE_ID
        )

    except Exception as e:

        print(
            "❌ فشل الحصول على الرسالة الأصلية."
        )

        print(
            f"Error: {type(e).__name__}: {e}"
        )

        return


    # ========================================================
    # التحقق من الرسالة الأصلية
    # ========================================================

    if not original_message:

        print(
            "❌ الرسالة الأصلية غير موجودة."
        )

        print(
            f"SOURCE_CHAT_ID    : "
            f"{SOURCE_CHAT_ID}"
        )

        print(
            f"SOURCE_MESSAGE_ID : "
            f"{SOURCE_MESSAGE_ID}"
        )

        return


    print(
        "✅ تم العثور على Original Message."
    )

    print(
        f"Original ID   : "
        f"{original_message.id}"
    )

    print(
        f"Original date : "
        f"{original_message.date}"
    )

    print(
        f"Original text : "
        f"{original_message.text}"
    )


    # ========================================================
    # التأكد من ID
    # ========================================================

    if original_message.id == SOURCE_MESSAGE_ID:

        print(
            "✅ Original Message ID صحيح."
        )

    else:

        print(
            "❌ Original Message ID غير صحيح."
        )

        print(
            f"Expected : {SOURCE_MESSAGE_ID}"
        )

        print(
            f"Actual   : {original_message.id}"
        )

        return


    # ========================================================
    # Media
    # ========================================================

    print_media_info(
        original_message,
        "ORIGINAL"
    )

    print_media_info(
        forwarded_message,
        "FORWARDED"
    )


    # ========================================================
    # مقارنة Media
    # ========================================================

    print()
    print("===================================")
    print("🔎 مقارنة Media")
    print("===================================")

    if original_message.media:

        print(
            "✅ Original يحتوي على Media."
        )

    else:

        print(
            "⚠️ Original لا يحتوي على Media."
        )


    if forwarded_message.media:

        print(
            "✅ Forwarded يحتوي على Media."
        )

    else:

        print(
            "⚠️ Forwarded لا يحتوي على Media."
        )


    # ========================================================
    # النتيجة النهائية
    # ========================================================

    print()
    print("===================================")
    print("🏁 النتيجة النهائية")
    print("===================================")

    print(
        "✅ Forwarded chat       : OK"
    )

    print(
        "✅ Forwarded message    : OK"
    )

    if forwarded_message.fwd_from:

        print(
            "✅ Forward header       : موجود"
        )

    else:

        print(
            "⚠️ Forward header       : غير موجود"
        )

    print(
        "✅ Source channel       : OK"
    )

    print(
        "✅ Original message     : OK"
    )

    print(
        f"Original Media          : "
        f"{'YES' if original_message.media else 'NO'}"
    )

    print(
        f"Forwarded Media         : "
        f"{'YES' if forwarded_message.media else 'NO'}"
    )

    print("===================================")
    print("✅ انتهى Worker")
    print("===================================")


# ============================================================
# تشغيل
# ============================================================

with client:

    client.loop.run_until_complete(
        main()
    )
