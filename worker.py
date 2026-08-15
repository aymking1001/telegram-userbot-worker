import os

from telethon import TelegramClient
from telethon.sessions import StringSession


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])
SOURCE_USERNAME = os.environ.get("SOURCE_USERNAME", "").strip()


client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


def normalize_channel_id(value):
    value = int(value)

    if value < 0:
        value = abs(value)

        if str(value).startswith("100"):
            value = int(str(value)[3:])

    return value


def get_entity_normalized_id(entity):
    entity_id = getattr(entity, "id", None)

    if entity_id is None:
        return None

    return normalize_channel_id(entity_id)


async def main():

    print("===================================")
    print("🚀 بدء Worker")
    print("===================================")

    print(f"Forwarded chat ID    : {CHAT_ID}")
    print(f"Forwarded message ID : {MESSAGE_ID}")
    print(f"Source chat ID       : {SOURCE_CHAT_ID}")
    print(f"Source message ID    : {SOURCE_MESSAGE_ID}")
    print(f"Source username      : {SOURCE_USERNAME}")

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

    print("===================================")
    print("🔎 فحص محادثة الرسالة المحولة")
    print("===================================")

    try:
        chat_entity = await client.get_entity(CHAT_ID)

        print("✅ تم العثور على المحادثة.")

        print(f"Entity ID   : {getattr(chat_entity, 'id', None)}")
        print(f"Chat type   : {type(chat_entity).__name__}")

        if hasattr(chat_entity, "title"):
            print(f"Title       : {getattr(chat_entity, 'title', None)}")

        if hasattr(chat_entity, "username"):
            print(f"Username    : {getattr(chat_entity, 'username', None)}")

    except Exception as e:
        print("❌ لا يمكن الوصول إلى CHAT_ID.")
        print(f"Error: {type(e).__name__}: {e}")
        return

    print("===================================")
    print("🔎 البحث عن الرسالة المحولة")
    print("===================================")

    try:
        forwarded_message = await client.get_messages(
            chat_entity,
            ids=MESSAGE_ID
        )

    except Exception as e:
        print("❌ فشل الحصول على الرسالة المحولة.")
        print(f"Error: {type(e).__name__}: {e}")
        return

    if not forwarded_message:
        print("❌ الرسالة المحولة غير موجودة.")
        print(f"CHAT_ID    : {CHAT_ID}")
        print(f"MESSAGE_ID : {MESSAGE_ID}")
        return

    print("✅ تم العثور على الرسالة المحولة.")

    print(f"Message ID : {forwarded_message.id}")
    print(f"Date       : {forwarded_message.date}")
    print(f"Text       : {forwarded_message.text}")
    print(
        f"Media      : "
        f"{'نعم' if forwarded_message.media else 'لا'}"
    )

    if forwarded_message.id != MESSAGE_ID:
        print("❌ Message ID mismatch.")
        print(f"Expected : {MESSAGE_ID}")
        print(f"Actual   : {forwarded_message.id}")
        return

    print("✅ Forwarded Message ID صحيح.")

    print("===================================")
    print("🔎 التحقق من معلومات الـ Forward")
    print("===================================")

    fwd = getattr(
        forwarded_message,
        "fwd_from",
        None
    )

    if fwd:

        print("✅ الرسالة تحتوي على معلومات Forward.")

        print(
            f"Forward from ID : "
            f"{getattr(fwd, 'from_id', None)}"
        )

        print(
            f"Channel post ID : "
            f"{getattr(fwd, 'channel_post', None)}"
        )

        print(
            f"Forward date    : "
            f"{getattr(fwd, 'date', None)}"
        )

    else:

        print(
            "⚠️ الرسالة لا تحتوي على fwd_from."
        )

        print(
            "سيتم الاعتماد على SOURCE_USERNAME "
            "و SOURCE_CHAT_ID."
        )

    print("===================================")
    print("🔎 البحث عن القناة الأصلية")
    print("===================================")

    source_entity = None

    if SOURCE_USERNAME:

        username = SOURCE_USERNAME.lstrip("@").strip()

        try:

            print(
                f"🔎 محاولة الوصول بواسطة username: @{username}"
            )

            source_entity = await client.get_entity(
                username
            )

            print("✅ تم العثور على القناة بواسطة username.")

            print(
                f"Entity ID : "
                f"{getattr(source_entity, 'id', None)}"
            )

            print(
                f"Title     : "
                f"{getattr(source_entity, 'title', None)}"
            )

            print(
                f"Username  : "
                f"{getattr(source_entity, 'username', None)}"
            )

        except Exception as e:

            print("⚠️ فشل الوصول بواسطة username.")
            print(
                f"Error: {type(e).__name__}: {e}"
            )

    if source_entity is None:

        try:

            print(
                "🔎 محاولة الوصول بواسطة SOURCE_CHAT_ID..."
            )

            source_entity = await client.get_entity(
                SOURCE_CHAT_ID
            )

            print(
                "✅ تم العثور على القناة بواسطة SOURCE_CHAT_ID."
            )

        except Exception as e:

            print(
                "⚠️ فشل الوصول بواسطة SOURCE_CHAT_ID."
            )

            print(
                f"Error: {type(e).__name__}: {e}"
            )

    if source_entity is None:

        print(
            "🔎 البحث عن القناة في dialogs..."
        )

        try:

            expected_id = normalize_channel_id(
                SOURCE_CHAT_ID
            )

            async for dialog in client.iter_dialogs():

                dialog_id = getattr(
                    dialog,
                    "id",
                    None
                )

                if dialog_id is None:
                    continue

                if normalize_channel_id(
                    dialog_id
                ) == expected_id:

                    source_entity = dialog.entity

                    print(
                        "✅ تم العثور على القناة في dialogs."
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

    if source_entity is None:

        print("===================================")
        print("❌ لم يتم العثور على القناة الأصلية")
        print("===================================")

        print(
            f"SOURCE_CHAT_ID  : {SOURCE_CHAT_ID}"
        )

        print(
            f"SOURCE_USERNAME : {SOURCE_USERNAME}"
        )

        return

    print("===================================")
    print("🔎 التحقق من Source Chat ID")
    print("===================================")

    actual_id = getattr(
        source_entity,
        "id",
        None
    )

    expected_normalized = normalize_channel_id(
        SOURCE_CHAT_ID
    )

    actual_normalized = get_entity_normalized_id(
        source_entity
    )

    print(
        f"Expected raw ID     : {SOURCE_CHAT_ID}"
    )

    print(
        f"Actual entity ID    : {actual_id}"
    )

    print(
        f"Expected normalized : {expected_normalized}"
    )

    print(
        f"Actual normalized   : {actual_normalized}"
    )

    if actual_normalized != expected_normalized:

        print(
            "❌ SOURCE_CHAT_ID لا يطابق القناة."
        )

        return

    print(
        "✅ SOURCE_CHAT_ID صحيح."
    )

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

    if not original_message:

        print("===================================")
        print("❌ الرسالة الأصلية غير موجودة")
        print("===================================")

        print(
            f"Source Chat ID    : {SOURCE_CHAT_ID}"
        )

        print(
            f"Source Message ID : {SOURCE_MESSAGE_ID}"
        )

        return

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

    if original_message.id != SOURCE_MESSAGE_ID:

        print(
            "❌ Original Message ID لا يطابق المطلوب."
        )

        print(
            f"Expected : {SOURCE_MESSAGE_ID}"
        )

        print(
            f"Actual   : {original_message.id}"
        )

        return

    print(
        "✅ Original Message ID صحيح."
    )

    print("===================================")
    print("📦 فحص Media")
    print("===================================")

    if original_message.media:

        print(
            "✅ الرسالة الأصلية تحتوي على Media."
        )

        print(
            f"Media type : "
            f"{type(original_message.media).__name__}"
        )

        document = getattr(
            original_message,
            "document",
            None
        )

        if document:

            print(
                f"Document ID : "
                f"{getattr(document, 'id', None)}"
            )

            print(
                f"Size        : "
                f"{getattr(document, 'size', None)} bytes"
            )

            print(
                f"MIME type   : "
                f"{getattr(document, 'mime_type', None)}"
            )

    else:

        print(
            "⚠️ الرسالة الأصلية لا تحتوي على Media."
        )

    print("===================================")
    print("🎯 التحقق النهائي")
    print("===================================")

    print("✅ Forwarded chat")
    print("✅ Forwarded message")
    print("✅ Forwarded message ID")
    print("✅ Source channel")
    print("✅ Source channel ID")
    print("✅ Original message")
    print("✅ Original message ID")

    if original_message.media:
        print("✅ Original media")
    else:
        print("⚠️ Original media: غير موجود")

    print("===================================")
    print("✅ انتهى العمل بنجاح")
    print("===================================")


with client:
    client.loop.run_until_complete(main())
