import os
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import RPCError


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

TELEGRAM_SESSION = os.environ["TELEGRAM_SESSION"]

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

    # --------------------------------------------------------
    # إنشاء Client باستخدام StringSession
    # --------------------------------------------------------

    print("===================================")
    print("🔐 إنشاء اتصال Telegram")
    print("===================================")

    if not TELEGRAM_SESSION:
        print("❌ TELEGRAM_SESSION فارغة.")
        return

    client = TelegramClient(
        StringSession(TELEGRAM_SESSION),
        API_ID,
        API_HASH
    )

    try:

        # لا يستخدم input()
        await client.connect()

        # ----------------------------------------------------
        # التحقق من تسجيل الدخول
        # ----------------------------------------------------

        if not await client.is_user_authorized():

            print("===================================")
            print("❌ الجلسة غير مسجلة الدخول")
            print("===================================")
            print()
            print("TELEGRAM_SESSION ليست جلسة Telethon صالحة.")
            print("يجب إنشاء StringSession جديدة.")
            print()

            return

        print("===================================")
        print("👤 Telegram Account")
        print("===================================")

        me = await client.get_me()

        print(f"ID       : {me.id}")
        print(f"Username : @{me.username}")
        print(f"Phone    : {me.phone}")

        # ----------------------------------------------------
        # تحميل Entity الخاص بالقناة الأصلية
        # ----------------------------------------------------

        print("===================================")
        print("🔎 تحميل Source Entity")
        print("===================================")

        source_entity = None

        try:

            # أولاً نحاول باستخدام username
            if SOURCE_USERNAME:

                username = SOURCE_USERNAME

                if username.startswith("@"):
                    username = username[1:]

                print(f"🔎 محاولة الوصول إلى: @{username}")

                try:
                    source_entity = await client.get_entity(
                        username
                    )

                    print("✅ تم العثور على Source Entity")
                    print(f"Entity ID: {source_entity.id}")

                except RPCError as e:

                    print("⚠️ تعذر الوصول باستخدام username:")
                    print(e)

            # ------------------------------------------------
            # إذا فشل username نستخدم ID
            # ------------------------------------------------

            if source_entity is None:

                print(
                    f"🔎 محاولة الوصول باستخدام "
                    f"SOURCE_CHAT_ID: {SOURCE_CHAT_ID}"
                )

                try:

                    # الحصول على الحوارات يساعد Telethon
                    # على تحميل الـ entities الموجودة في الحساب

                    dialogs = await client.get_dialogs(
                        limit=None
                    )

                    for dialog in dialogs:

                        if dialog.entity:

                            entity_id = getattr(
                                dialog.entity,
                                "id",
                                None
                            )

                            if entity_id == abs(SOURCE_CHAT_ID):

                                source_entity = dialog.entity
                                break

                    if source_entity:

                        print("✅ تم العثور على Source Entity من dialogs")
                        print(
                            f"Entity ID: "
                            f"{source_entity.id}"
                        )

                    else:

                        print(
                            "⚠️ لم يتم العثور على القناة في dialogs."
                        )

                except RPCError as e:

                    print(
                        "❌ خطأ أثناء تحميل dialogs:"
                    )
                    print(e)

        except Exception as e:

            print(
                "❌ خطأ غير متوقع أثناء تحميل Source Entity:"
            )
            print(type(e).__name__)
            print(e)

        # ----------------------------------------------------
        # إذا لم نجد القناة
        # ----------------------------------------------------

        if source_entity is None:

            print("===================================")
            print("❌ لم يتم العثور على Source Entity")
            print("===================================")

            print()
            print("الحساب يجب أن يكون:")
            print("1. داخل القناة، أو")
            print("2. قادرًا على الوصول إليها بواسطة username.")
            print()

            return

        # ----------------------------------------------------
        # البحث عن الرسالة الأصلية
        # ----------------------------------------------------

        print("===================================")
        print("🔎 البحث عن الرسالة الأصلية")
        print("===================================")

        try:

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
                    f"{source_entity.id}"
                )

                # ------------------------------------------------
                # النص
                # ------------------------------------------------

                if source_message.message:

                    print("Text:")
                    print(
                        source_message.message[:1000]
                    )

                else:

                    print("⚠️ لا يوجد نص.")

                # ------------------------------------------------
                # Media
                # ------------------------------------------------

                if source_message.media:

                    print(
                        "📎 الرسالة تحتوي على Media."
                    )

                    print(
                        f"Media type: "
                        f"{type(source_message.media).__name__}"
                    )

                else:

                    print(
                        "ℹ️ الرسالة لا تحتوي على Media."
                    )

        except RPCError as e:

            print(
                "❌ خطأ Telegram أثناء البحث عن "
                "الرسالة الأصلية:"
            )
            print(type(e).__name__)
            print(e)

        except Exception as e:

            print(
                "❌ خطأ غير متوقع أثناء البحث عن "
                "الرسالة الأصلية:"
            )
            print(type(e).__name__)
            print(e)

        # ----------------------------------------------------
        # البحث عن الرسالة المحولة
        # ----------------------------------------------------

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

                print(
                    f"CHAT_ID    : {CHAT_ID}"
                )

                print(
                    f"MESSAGE_ID : {MESSAGE_ID}"
                )

            else:

                print("✅ تم العثور على الرسالة المحولة.")

                print(
                    f"Message ID : "
                    f"{forwarded_message.id}"
                )

                # ------------------------------------------------
                # Forward information
                # ------------------------------------------------

                if forwarded_message.fwd_from:

                    print(
                        "✅ الرسالة تحتوي على معلومات Forward."
                    )

                    print(
                        "Forward information:"
                    )

                    print(
                        forwarded_message.fwd_from
                    )

                else:

                    print(
                        "⚠️ الرسالة ليست Forward."
                    )

                # ------------------------------------------------
                # النص
                # ------------------------------------------------

                if forwarded_message.message:

                    print("Text:")
                    print(
                        forwarded_message.message[:1000]
                    )

                # ------------------------------------------------
                # Media
                # ------------------------------------------------

                if forwarded_message.media:

                    print(
                        "📎 الرسالة المحولة تحتوي على Media."
                    )

        except RPCError as e:

            print(
                "❌ خطأ Telegram أثناء البحث عن "
                "الرسالة المحولة:"
            )

            print(type(e).__name__)
            print(e)

        except Exception as e:

            print(
                "❌ خطأ غير متوقع أثناء البحث عن "
                "الرسالة المحولة:"
            )

            print(type(e).__name__)
            print(e)

    finally:

        # ----------------------------------------------------
        # إغلاق الاتصال
        # ----------------------------------------------------

        if client.is_connected():

            await client.disconnect()

        print("===================================")
        print("🏁 انتهاء Worker")
        print("===================================")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("🛑 تم إيقاف Worker.")

    except Exception as e:

        print("===================================")
        print("❌ خطأ رئيسي")
        print("===================================")
        print(type(e).__name__)
        print(e)
