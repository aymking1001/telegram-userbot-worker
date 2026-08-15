import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import (
    MessageMediaDocument,
    MessageMediaPhoto,
)


# ============================================================
# Telegram credentials
# ============================================================

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]


# ============================================================
# Forwarded message
# ============================================================

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])


# ============================================================
# Original message
# ============================================================

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])
SOURCE_USERNAME = os.environ.get("SOURCE_USERNAME", "").strip()


# ============================================================
# Telegram client
# ============================================================

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


# ============================================================
# Helpers
# ============================================================

def normalize_channel_id(entity_id):
    """
    Telethon يعرض ID القناة/السوبرغروب كرقم موجب داخل entity.

    مثال:
        Entity ID:
            1839480260

        Telegram Bot API ID:
            -1001839480260
    """

    entity_id = int(entity_id)

    if entity_id > 0:
        return -1000000000000 - entity_id

    return entity_id


def normalize_id(value):
    """
    تحويل أي صيغة Telegram ID إلى صيغة -100xxxxxxxxxx
    عند الحاجة.
    """

    value = int(value)

    if value > 0:
        return -1000000000000 - value

    return value


def get_media_type(message):

    if not message or not message.media:
        return None

    if isinstance(message.media, MessageMediaDocument):
        return "document"

    if isinstance(message.media, MessageMediaPhoto):
        return "photo"

    return type(message.media).__name__


# ============================================================
# Main
# ============================================================

async def main():

    print("===================================")
    print("🚀 بدء Worker")
    print("===================================")

    print(f"Forwarded chat ID : {CHAT_ID}")
    print(f"Forwarded message : {MESSAGE_ID}")

    print(f"Source chat ID    : {SOURCE_CHAT_ID}")
    print(f"Source message ID : {SOURCE_MESSAGE_ID}")
    print(f"Source username   : {SOURCE_USERNAME}")

    # ========================================================
    # Account
    # ========================================================

    try:

        me = await client.get_me()

        print("===================================")
        print("👤 Telegram Account")
        print("===================================")

        print(f"ID       : {me.id}")

        if me.username:
            print(f"Username : @{me.username}")
        else:
            print("Username : None")

        if me.phone:
            print(f"Phone    : {me.phone}")
        else:
            print("Phone    : None")

    except Exception as e:

        print("❌ فشل الحصول على معلومات الحساب.")
        print(f"Error: {type(e).__name__}: {e}")

        return


    # ========================================================
    # Get forwarded chat
    # ========================================================

    print("===================================")
    print("🔎 فحص محادثة الرسالة المحولة")
    print("===================================")

    try:

        forwarded_chat = await client.get_entity(CHAT_ID)

        print("✅ تم العثور على المحادثة.")

        print(
            f"Entity ID : "
            f"{getattr(forwarded_chat, 'id', None)}"
        )

        print(
            f"Entity type : "
            f"{type(forwarded_chat).__name__}"
        )

        if hasattr(forwarded_chat, "username"):
            print(
                f"Username : "
                f"{getattr(forwarded_chat, 'username', None)}"
            )

        if hasattr(forwarded_chat, "title"):
            print(
                f"Title : "
                f"{getattr(forwarded_chat, 'title', None)}"
            )

    except Exception as e:

        print("❌ لا يمكن الوصول إلى CHAT_ID.")
        print(f"Error: {type(e).__name__}: {e}")

        return


    # ========================================================
    # Get forwarded message
    # ========================================================

    print("===================================")
    print("🔎 البحث عن الرسالة المحولة")
    print("===================================")

    try:

        forwarded_message = await client.get_messages(
            forwarded_chat,
            ids=MESSAGE_ID
        )

    except Exception as e:

        print("❌ فشل الحصول على الرسالة المحولة.")
        print(f"Error: {type(e).__name__}: {e}")

        return


    # ========================================================
    # Validate forwarded message
    # ========================================================

    if not forwarded_message:

        print("❌ لم يتم العثور على الرسالة المحولة.")

        print(
            f"CHAT_ID    : {CHAT_ID}"
        )

        print(
            f"MESSAGE_ID : {MESSAGE_ID}"
        )

        return


    print("✅ تم العثور على الرسالة المحولة.")

    print(
        f"Forwarded ID   : {forwarded_message.id}"
    )

    print(
        f"Forwarded date : {forwarded_message.date}"
    )

    print(
        f"Forwarded text : "
        f"{forwarded_message.text}"
    )

    print(
        f"Forwarded media: "
        f"{get_media_type(forwarded_message)}"
    )


    # ========================================================
    # Check whether message is actually forwarded
    # ========================================================

    print("===================================")
    print("🔎 التحقق من Forward")
    print("===================================")

    if forwarded_message.fwd_from:

        print("✅ الرسالة تحتوي على معلومات Forward.")

        print(
            f"Forward info : "
            f"{forwarded_message.fwd_from}"
        )

    else:

        print(
            "⚠️ الرسالة موجودة، ولكن لا تحتوي على "
            "معلومات Forward."
        )

        print(
            "هذا يعني أن MESSAGE_ID قد يشير إلى "
            "رسالة عادية وليست Forward."
        )


    # ========================================================
    # Find source channel
    # ========================================================

    print("===================================")
    print("🔎 البحث عن القناة الأصلية")
    print("===================================")

    source_entity = None


    # ========================================================
    # Try username first
    # ========================================================

    if SOURCE_USERNAME:

        username = SOURCE_USERNAME.lstrip("@").strip()

        try:

            print(
                f"🔎 محاولة الوصول بواسطة username: "
                f"@{username}"
            )

            source_entity = await client.get_entity(
                username
            )

            print(
                "✅ تم العثور على القناة بواسطة username."
            )

            actual_id = getattr(
                source_entity,
                "id",
                None
            )

            print(
                f"Entity ID       : {actual_id}"
            )

            print(
                f"Normalized ID   : "
                f"{normalize_channel_id(actual_id)}"
            )

            print(
                f"Title           : "
                f"{getattr(source_entity, 'title', None)}"
            )

            print(
                f"Username        : "
                f"{getattr(source_entity, 'username', None)}"
            )

        except Exception as e:

            print(
                "⚠️ فشل الوصول بواسطة username."
            )

            print(
                f"Error: {type(e).__name__}: {e}"
            )


    # ========================================================
    # Validate source ID
    # ========================================================

    if source_entity:

        print("===================================")
        print("🔎 التحقق من Source Chat ID")
        print("===================================")

        actual_id = getattr(
            source_entity,
            "id",
            None
        )

        normalized_actual_id = normalize_channel_id(
            actual_id
        )

        normalized_expected_id = normalize_id(
            SOURCE_CHAT_ID
        )

        print(
            f"Expected raw ID       : "
            f"{SOURCE_CHAT_ID}"
        )

        print(
            f"Actual entity ID      : "
            f"{actual_id}"
        )

        print(
            f"Expected normalized   : "
            f"{normalized_expected_id}"
        )

        print(
            f"Actual normalized     : "
            f"{normalized_actual_id}"
        )

        if normalized_actual_id == normalized_expected_id:

            print(
                "✅ Source Chat ID مطابق."
            )

        else:

            print(
                "⚠️ Source Chat ID مختلف."
            )

            print(
                "لكن سيتم استخدام الـ entity الذي "
                "تم الحصول عليه من username."
            )


    # ========================================================
    # If username failed, search dialogs
    # ========================================================

    if source_entity is None:

        print("===================================")
        print("🔎 البحث في dialogs")
        print("===================================")

        try:

            target_id = normalize_id(
                SOURCE_CHAT_ID
            )

            async for dialog in client.iter_dialogs():

                dialog_id = int(dialog.id)

                if (
                    dialog_id == SOURCE_CHAT_ID
                    or
                    normalize_id(dialog_id) == target_id
                ):

                    source_entity = dialog.entity

                    print(
                        "✅ تم العثور على القناة "
                        "داخل dialogs."
                    )

                    print(
                        f"Dialog ID : {dialog.id}"
                    )

                    print(
                        f"Name      : {dialog.name}"
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
    # Source not found
    # ========================================================

    if source_entity is None:

        print("===================================")
        print("❌ لم يتم العثور على القناة الأصلية")
        print("===================================")

        print(
            f"SOURCE_CHAT_ID : "
            f"{SOURCE_CHAT_ID}"
        )

        print(
            f"SOURCE_USERNAME: "
            f"{SOURCE_USERNAME}"
        )

        print()
        print("الأسباب المحتملة:")
        print("1. الحساب ليس لديه وصول للقناة.")
        print("2. username غير صحيح.")
        print("3. القناة خاصة.")
        print("4. SOURCE_CHAT_ID غير صحيح.")
        print("5. الرسالة لم تعد متاحة.")

        return


    # ========================================================
    # Get original message
    # ========================================================

    print("===================================")
    print("🔎 البحث عن الرسالة الأصلية")
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
    # Validate original message
    # ========================================================

    if not original_message:

        print("===================================")
        print("❌ الرسالة الأصلية غير موجودة")
        print("===================================")

        print(
            f"Source chat ID    : "
            f"{SOURCE_CHAT_ID}"
        )

        print(
            f"Source message ID : "
            f"{SOURCE_MESSAGE_ID}"
        )

        return


    print("===================================")
    print("✅ تم العثور على الرسالة الأصلية")
    print("===================================")

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

    print(
        f"Original media: "
        f"{get_media_type(original_message)}"
    )


    # ========================================================
    # Validate original message ID
    # ========================================================

    if original_message.id == SOURCE_MESSAGE_ID:

        print(
            "✅ Original Message ID مطابق."
        )

    else:

        print(
            "❌ Original Message ID غير مطابق!"
        )

        print(
            f"Expected: {SOURCE_MESSAGE_ID}"
        )

        print(
            f"Actual  : {original_message.id}"
        )

        return


    # ========================================================
    # Compare Forward with Original
    # ========================================================

    print("===================================")
    print("🔎 مقارنة Forward مع Original")
    print("===================================")

    if forwarded_message.fwd_from:

        fwd = forwarded_message.fwd_from

        print(
            f"Forward source channel ID : "
            f"{getattr(fwd, 'from_id', None)}"
        )

        print(
            f"Forward source message ID : "
            f"{getattr(fwd, 'channel_post', None)}"
        )

        forward_source_id = getattr(
            fwd,
            "from_id",
            None
        )

        forward_message_id = getattr(
            fwd,
            "channel_post",
            None
        )

        # ----------------------------------------------------
        # Channel post ID
        # ----------------------------------------------------

        if forward_message_id is not None:

            if (
                int(forward_message_id)
                ==
                int(SOURCE_MESSAGE_ID)
            ):

                print(
                    "✅ Forward يشير إلى "
                    "نفس Original Message ID."
                )

            else:

                print(
                    "⚠️ Forward Message ID مختلف."
                )

                print(
                    f"Expected: "
                    f"{SOURCE_MESSAGE_ID}"
                )

                print(
                    f"Actual: "
                    f"{forward_message_id}"
                )

        # ----------------------------------------------------
        # Source channel ID
        # ----------------------------------------------------

        if forward_source_id is not None:

            print(
                f"Forward source entity: "
                f"{forward_source_id}"
            )


    else:

        print(
            "⚠️ لا توجد معلومات Forward "
            "للمقارنة."
        )


    # ========================================================
    # Media verification
    # ========================================================

    print("===================================")
    print("📦 التحقق من Media")
    print("===================================")

    original_media_type = get_media_type(
        original_message
    )

    forwarded_media_type = get_media_type(
        forwarded_message
    )

    print(
        f"Original Media : "
        f"{original_media_type}"
    )

    print(
        f"Forwarded Media: "
        f"{forwarded_media_type}"
    )


    if original_message.media:

        print(
            "✅ Original message تحتوي على Media."
        )

    else:

        print(
            "⚠️ Original message لا تحتوي على Media."
        )


    if forwarded_message.media:

        print(
            "✅ Forwarded message تحتوي على Media."
        )

    else:

        print(
            "⚠️ Forwarded message لا تحتوي على Media."
        )


    # ========================================================
    # Media document information
    # ========================================================

    if original_message.document:

        document = original_message.document

        print("===================================")
        print("📄 معلومات Document")
        print("===================================")

        print(
            f"Document ID : "
            f"{document.id}"
        )

        print(
            f"Document size : "
            f"{document.size}"
        )

        print(
            f"MIME type : "
            f"{document.mime_type}"
        )

        print(
            f"Attributes : "
            f"{document.attributes}"
        )


    # ========================================================
    # Final result
    # ========================================================

    print("===================================")
    print("✅ انتهى الفحص")
    print("===================================")

    print(
        "Forwarded message : OK"
    )

    print(
        "Original message  : OK"
    )

    print(
        "Source entity     : OK"
    )

    print(
        f"Original media    : "
        f"{original_media_type}"
    )

    print(
        f"Forward media     : "
        f"{forwarded_media_type}"
    )

    print("===================================")


# ============================================================
# Run
# ============================================================

with client:

    client.loop.run_until_complete(
        main()
    )
