import os
import asyncio

from telethon import TelegramClient
from telethon.errors import RPCError


# ============================================================
# ENV
# ============================================================

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ["TELEGRAM_SESSION"]

CHAT_ID = int(os.environ["CHAT_ID"])
MESSAGE_ID = int(os.environ["MESSAGE_ID"])

SOURCE_CHAT_ID = int(os.environ["SOURCE_CHAT_ID"])
SOURCE_MESSAGE_ID = int(os.environ["SOURCE_MESSAGE_ID"])

SOURCE_USERNAME = os.environ.get("SOURCE_USERNAME", "").strip()


# ============================================================
# MAIN
# ============================================================

async def main():

    print("===================================")
    print("🚀 بدء Worker")
    print("===================================")

    print(f"Forwarded chat ID    : {CHAT_ID}")
    print(f"Forwarded message ID : {MESSAGE_ID}")
    print(f"Source chat ID       : {SOURCE_CHAT_ID}")
    print(f"Source message ID    : {SOURCE_MESSAGE_ID}")
    print(f"Source username      : {SOURCE_USERNAME}")

    # ========================================================
    # Telegram Client
    # ========================================================

    client = TelegramClient(
        "worker_session",
        API_ID,
        API_HASH
    )

    try:

        # ----------------------------------------------------
        # تسجيل الدخول
        # ----------------------------------------------------

        print("===================================")
        print("🔐 تسجيل الدخول")
        print("===================================")

        # مهم جدًا:
        # لا نريد Telethon أن يحاول طلب رقم الهاتف
        # داخل GitHub Actions.
        #
        # SESSION يجب أن تكون Session String صالحة.

        await client.start(
            bot_token=None
        )

        # ----------------------------------------------------
        # معلومات الحساب
        # ----------------------------------------------------

        me = await client.get_me()

        print("===================================")
        print("👤 Telegram Account")
        print("===================================")

        print(f"ID       : {me.id}")
        print(f"Username : @{me.username}")
        print(f"Phone    : {me.phone}")

        # ====================================================
        # البحث عن الرسالة المحولة
        # ====================================================

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
                        "From ID : "
                        f"{getattr(forwarded_message.fwd_from, 'from_id', None)}"
                    )

                else:

                    print("⚠️ الرسالة ليست Forward.")

        except RPCError as e:

            print("❌ خطأ Telegram أثناء البحث عن الرسالة المحولة:")
            print(type(e).__name__)
            print(e)

        except Exception as e:

            print("❌ خطأ غير متوقع أثناء البحث عن الرسالة المحولة:")
            print(type(e).__name__)
            print(e)

        # ====================================================
        # الحصول على Source Entity
        # ====================================================

        print("===================================")
        print("🔎 الحصول على Source Entity")
        print("===================================")

        source_entity = None

        # ----------------------------------------------------
        # الطريقة الأولى: username
        # ----------------------------------------------------

        if SOURCE_USERNAME:

            try:

                username = SOURCE_USERNAME

                if username.startswith("@"):
                    username = username[1:]

                print(
                    f"🔍 محاولة الوصول إلى القناة بواسطة username: "
                    f"@{username}"
                )

                source_entity = await client.get_entity(
                    username
                )

                print("✅ تم الحصول على Source Entity.")

                print(
                    f"Entity ID       : "
                    f"{getattr(source_entity, 'id', None)}"
                )

                print(
                    f"Entity username : "
                    f"@{getattr(source_entity, 'username', None)}"
                )

                print(
                    f"Entity title    : "
                    f"{getattr(source_entity, 'title', None)}"
                )

            except RPCError as e:

                print("❌ Telegram رفض الوصول إلى Source Entity:")
                print(type(e).__name__)
                print(e)

            except Exception as e:

                print("❌ فشل الحصول على Source Entity بواسطة username:")
                print(type(e).__name__)
                print(e)

        # ----------------------------------------------------
        # إذا فشل username نحاول SOURCE_CHAT_ID
        # ----------------------------------------------------

        if source_entity is None:

            print("===================================")
            print("🔄 محاولة الوصول بواسطة SOURCE_CHAT_ID")
            print("===================================")

            try:

                source_entity = await client.get_entity(
                    SOURCE_CHAT_ID
                )

                print("✅ تم الحصول على Source Entity بواسطة ID.")

            except RPCError as e:

                print("❌ لا يمكن الوصول إلى Source Chat بواسطة ID:")
                print(type(e).__name__)
                print(e)

            except Exception as e:

                print("❌ خطأ غير متوقع:")
                print(type(e).__name__)
                print(e)

        # ====================================================
        # البحث عن الرسالة الأصلية
        # ====================================================

        print("===================================")
        print("🔎 البحث عن الرسالة الأصلية")
        print("===================================")

        if source_entity is None:

            print("❌ لا يمكن البحث عن الرسالة الأصلية.")
            print("السبب: Source Entity غير متوفر.")

        else:

            try:

                print(
                    f"Source Entity ID : "
                    f"{getattr(source_entity, 'id', None)}"
                )

                print(
                    f"Source Message ID : "
                    f"{SOURCE_MESSAGE_ID}"
                )

                source_message = await client.get_messages(
                    source_entity,
                    ids=SOURCE_MESSAGE_ID
                )

                if source_message is None:

                    print("❌ الرسالة الأصلية غير موجودة.")

                    print(
                        f"SOURCE_MESSAGE_ID : "
                        f"{SOURCE_MESSAGE_ID}"
                    )

                else:

                    print("✅ تم العثور على الرسالة الأصلية.")

                    print(
                        f"Message ID : "
                        f"{source_message.id}"
                    )

                    print(
                        f"Chat ID    : "
                        f"{getattr(source_entity, 'id', None)}"
                    )

                    # ----------------------------------------
                    # النص
                    # ----------------------------------------

                    if source_message.message:

                        print("===================================")
                        print("📝 النص")
                        print("===================================")

                        print(
                            source_message.message[:500]
                        )

                    else:

                        print("⚠️ الرسالة لا تحتوي على نص.")

                    # ----------------------------------------
                    # Media
                    # ----------------------------------------

                    if source_message.media:

                        print("📎 الرسالة تحتوي على Media.")

                        print(
                            f"Media type : "
                            f"{type(source_message.media).__name__}"
                        )

                    else:

                        print("⚠️ الرسالة لا تحتوي على Media.")

                    # ----------------------------------------
                    # Forward info
                    # ----------------------------------------

                    if source_message.fwd_from:

                        print("🔁 الرسالة الأصلية نفسها تحتوي على Forward.")

            except RPCError as e:

                print("❌ خطأ Telegram أثناء البحث عن الرسالة الأصلية:")
                print(type(e).__name__)
                print(e)

            except Exception as e:

                print("❌ خطأ غير متوقع أثناء البحث عن الرسالة الأصلية:")
                print(type(e).__name__)
                print(e)

    finally:

        # ====================================================
        # Disconnect
        # ====================================================

        await client.disconnect()

        print("===================================")
        print("🏁 انتهاء Worker")
        print("===================================")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
