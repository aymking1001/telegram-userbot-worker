import os
from telethon import TelegramClient

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])

client = TelegramClient("worker", API_ID, API_HASH)


async def main():
    # الحصول على الرسالة المحوّلة الموجودة في CHAT_ID
    forwarded_message = await client.get_messages(
        CHAT_ID,
        ids=MESSAGE_ID
    )

    if not forwarded_message:
        print("❌ لم يتم العثور على الرسالة.")
        return

    print(f"✅ تم العثور على الرسالة: {forwarded_message.id}")

    # التأكد أنها رسالة محوّلة
    if not forwarded_message.fwd_from:
        print("❌ هذه الرسالة ليست رسالة محوّلة.")
        return

    fwd = forwarded_message.fwd_from

    print("✅ الرسالة محوّلة من مصدر.")

    # --------------------------------------------------
    # محاولة معرفة القناة الأصلية
    # --------------------------------------------------

    if not fwd.from_id:
        print("❌ Telegram لم يعطِ مصدر الرسالة.")
        print("قد تكون معلومات المصدر مخفية.")
        return

    print(f"Source ID: {fwd.from_id}")

    # الحصول على Entity الخاص بالمصدر
    try:
        source_entity = await client.get_entity(fwd.from_id)
    except Exception as e:
        print("❌ لم أستطع الوصول إلى القناة/الحساب الأصلي.")
        print(f"Error: {e}")
        return

    print(f"✅ تم العثور على المصدر: {source_entity}")

    # --------------------------------------------------
    # الحصول على ID الرسالة الأصلية
    # --------------------------------------------------

    original_message_id = fwd.channel_post

    if not original_message_id:
        print("❌ لا يوجد channel_post في معلومات التحويل.")
        return

    print(f"Original message ID: {original_message_id}")

    # --------------------------------------------------
    # جلب الرسالة الأصلية
    # --------------------------------------------------

    try:
        original_message = await client.get_messages(
            source_entity,
            ids=original_message_id
        )
    except Exception as e:
        print("❌ فشل الحصول على الرسالة الأصلية.")
        print(f"Error: {e}")
        return

    if not original_message:
        print("❌ الرسالة الأصلية غير موجودة أو لا يمكن الوصول إليها.")
        return

    print("===================================")
    print("✅ تم العثور على الرسالة الأصلية")
    print("===================================")

    print(f"Original ID: {original_message.id}")
    print(f"Original date: {original_message.date}")
    print(f"Original text: {original_message.text}")

    # معلومات إضافية
    if original_message.media:
        print("Original message contains media.")

    print("===================================")


with client:
    client.loop.run_until_complete(main())
