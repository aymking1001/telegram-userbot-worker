import asyncio
import os
import sys
import tempfile
import mimetypes
import traceback

import cloudinary
import cloudinary.uploader

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError


async def main():

    client = None
    temp_path = None

    try:

        # ============================================================
        # Telegram credentials
        # ============================================================

        api_id = int(
            os.environ.get("TELEGRAM_API_ID", "0")
        )

        api_hash = os.environ.get(
            "TELEGRAM_API_HASH",
            ""
        )

        session_string = os.environ.get(
            "TELEGRAM_SESSION",
            ""
        )

        # ============================================================
        # Telegram source
        # ============================================================

        source_chat_id = os.environ.get(
            "SOURCE_CHAT_ID",
            ""
        )

        source_message_id = int(
            os.environ.get(
                "SOURCE_MESSAGE_ID",
                "0"
            )
        )

        source_username = os.environ.get(
            "SOURCE_USERNAME",
            ""
        )

        # ============================================================
        # Cloudinary
        # ============================================================

        cloudinary_cloud_name = os.environ.get(
            "CLOUDINARY_CLOUD_NAME",
            ""
        )

        cloudinary_api_key = os.environ.get(
            "CLOUDINARY_API_KEY",
            ""
        )

        cloudinary_api_secret = os.environ.get(
            "CLOUDINARY_API_SECRET",
            ""
        )

        # ============================================================
        # Validate variables
        # ============================================================

        print("📋 التحقق من المتغيرات...")

        if not api_id:
            print("❌ TELEGRAM_API_ID مفقود")
            sys.exit(1)

        if not api_hash:
            print("❌ TELEGRAM_API_HASH مفقود")
            sys.exit(1)

        if not session_string:
            print("❌ TELEGRAM_SESSION مفقود")
            sys.exit(1)

        if not source_chat_id:
            print("❌ SOURCE_CHAT_ID مفقود")
            sys.exit(1)

        if not source_message_id:
            print("❌ SOURCE_MESSAGE_ID مفقود")
            sys.exit(1)

        if not cloudinary_cloud_name:
            print("❌ CLOUDINARY_CLOUD_NAME مفقود")
            sys.exit(1)

        if not cloudinary_api_key:
            print("❌ CLOUDINARY_API_KEY مفقود")
            sys.exit(1)

        if not cloudinary_api_secret:
            print("❌ CLOUDINARY_API_SECRET مفقود")
            sys.exit(1)

        print("✅ جميع المتغيرات موجودة")

        print(
            f"📌 Source Chat ID: {source_chat_id}"
        )

        print(
            f"📌 Source Message ID: {source_message_id}"
        )

        print(
            f"📌 Source Username: {source_username}"
        )

        print(
            f"☁️ Cloudinary Cloud Name: "
            f"{cloudinary_cloud_name}"
        )

        # ============================================================
        # Configure Cloudinary
        # ============================================================

        cloudinary.config(
            cloud_name=cloudinary_cloud_name,
            api_key=cloudinary_api_key,
            api_secret=cloudinary_api_secret,
            secure=True
        )

        print("✅ تم إعداد Cloudinary")

        # ============================================================
        # Create Telegram client
        # ============================================================

        client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash
        )

        # ============================================================
        # Login
        # ============================================================

        print("🔐 تسجيل الدخول إلى Telegram...")

        await client.start()

        me = await client.get_me()

        print(
            f"✅ تسجيل الدخول إلى Telegram نجح."
        )

        print(
            f"👤 الحساب: {me.first_name}"
        )

        print(
            f"🆔 Telegram ID: {me.id}"
        )

        # ============================================================
        # Get source entity
        # ============================================================

        print("🔎 الوصول إلى المصدر...")

        if source_username:

            try:

                source_entity = await client.get_entity(
                    f"@{source_username}"
                )

            except Exception:

                print(
                    "⚠️ تعذر الوصول باستخدام username."
                )

                print(
                    "🔄 محاولة استخدام SOURCE_CHAT_ID..."
                )

                source_entity = await client.get_entity(
                    int(source_chat_id)
                )

        else:

            source_entity = await client.get_entity(
                int(source_chat_id)
            )

        print("✅ تم الوصول إلى المصدر.")

        # ============================================================
        # Get original message
        # ============================================================

        print(
            f"🔎 البحث عن الرسالة "
            f"{source_message_id}..."
        )

        source_message = await client.get_messages(
            source_entity,
            ids=source_message_id
        )

        if not source_message:

            print(
                f"❌ لم يتم العثور على الرسالة "
                f"{source_message_id}."
            )

            sys.exit(1)

        print(
            f"✅ تم العثور على الرسالة "
            f"`{source_message.id}`."
        )

        # ============================================================
        # Check audio
        # ============================================================

        if not (
            source_message.voice
            or source_message.audio
        ):

            print(
                "❌ الرسالة لا تحتوي على voice/audio."
            )

            if source_message.media:

                print(
                    f"نوع الـ media: "
                    f"{type(source_message.media)}"
                )

            else:

                print(
                    "نوع المحتوى: بدون media"
                )

            sys.exit(1)

        # ============================================================
        # Get audio information
        # ============================================================

        if source_message.voice:

            media_type = "صوتية"

            file_size = (
                source_message.voice.size
                or 0
            )

            mime_type = (
                source_message.voice.mime_type
                or "audio/ogg"
            )

        else:

            media_type = "ملف صوتي"

            file_size = (
                source_message.audio.size
                or 0
            )

            mime_type = (
                source_message.audio.mime_type
                or "audio/mpeg"
            )

        print(
            f"🎵 تم اكتشاف {media_type}."
        )

        print(
            f"📦 الحجم: {file_size} بايت"
        )

        print(
            f"📦 الحجم: "
            f"{file_size / 1024 / 1024:.2f} MB"
        )

        print(
            f"🎼 MIME: {mime_type}"
        )

        # ============================================================
        # Determine extension
        # ============================================================

        extension = mimetypes.guess_extension(
            mime_type
        )

        if not extension:

            if mime_type == "audio/ogg":

                extension = ".ogg"

            elif mime_type == "audio/mpeg":

                extension = ".mp3"

            elif mime_type == "audio/mp4":

                extension = ".m4a"

            else:

                extension = ".audio"

        print(
            f"📄 امتداد الملف: {extension}"
        )

        # ============================================================
        # Temporary file
        # ============================================================

        temp_file = tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False
        )

        temp_path = temp_file.name

        temp_file.close()

        # ============================================================
        # Download from Telegram
        # ============================================================

        print(
            "⬇️ تنزيل الصوت من Telegram..."
        )

        downloaded_file = await client.download_media(
            source_message,
            file=temp_path
        )

        if not downloaded_file:

            print(
                "❌ فشل تنزيل الملف من Telegram."
            )

            sys.exit(1)

        print(
            "✅ تم تنزيل الصوت بنجاح."
        )

        print(
            f"📁 الملف المؤقت: {downloaded_file}"
        )

        # ============================================================
        # Check downloaded file
        # ============================================================

        if not os.path.exists(temp_path):

            print(
                "❌ الملف الذي تم تنزيله غير موجود."
            )

            sys.exit(1)

        downloaded_size = os.path.getsize(
            temp_path
        )

        print(
            f"📦 الحجم بعد التنزيل: "
            f"{downloaded_size} بايت"
        )

        # ============================================================
        # Upload to Cloudinary
        # ============================================================

        print(
            "☁️ رفع الصوت إلى Cloudinary..."
        )

        upload_result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            temp_path,
            resource_type="video"
        )

        # ============================================================
        # Cloudinary result
        # ============================================================

        secure_url = upload_result.get(
            "secure_url"
        )

        public_id = upload_result.get(
            "public_id"
        )

        resource_type = upload_result.get(
            "resource_type"
        )

        format_value = upload_result.get(
            "format"
        )

        if not secure_url:

            print(
                "❌ Cloudinary لم يرجع secure_url."
            )

            print(
                "📋 نتيجة Cloudinary:"
            )

            print(upload_result)

            sys.exit(1)

        # ============================================================
        # SUCCESS
        # ============================================================

        print("")
        print("=" * 60)
        print("✅ رفع الصوت إلى Cloudinary نجح.")
        print("=" * 60)

        print(
            f"☁️ Public ID: {public_id}"
        )

        print(
            f"📦 Resource Type: {resource_type}"
        )

        print(
            f"🎼 Format: {format_value}"
        )

        print(
            f"🔗 Cloudinary URL:"
        )

        print(
            secure_url
        )

        print("=" * 60)

        # ============================================================
        # Output in easy-to-find format
        # ============================================================

        print(
            f"CLOUDINARY_URL={secure_url}"
        )

        print(
            f"CLOUDINARY_PUBLIC_ID={public_id}"
        )

        print("🎉 انتهت المهمة بنجاح.")

    except SessionPasswordNeededError:

        print(
            "❌ Telegram يحتاج كلمة مرور 2FA."
        )

        print(
            "تحقق من TELEGRAM_SESSION."
        )

        sys.exit(1)

    except Exception as e:

        print(
            f"❌ حدث خطأ: {e}"
        )

        traceback.print_exc()

        sys.exit(1)

    finally:

        # ============================================================
        # Delete temporary file
        # ============================================================

        if temp_path:

            try:

                if os.path.exists(temp_path):

                    os.remove(temp_path)

                    print(
                        "🗑️ تم حذف الملف المؤقت."
                    )

            except Exception as e:

                print(
                    f"⚠️ تعذر حذف الملف المؤقت: {e}"
                )

        # ============================================================
        # Disconnect Telegram
        # ============================================================

        if client:

            try:

                await client.disconnect()

                print(
                    "🔌 تم قطع الاتصال بـ Telegram."
                )

            except Exception:

                pass


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "🛑 تم إيقاف البرنامج."
        )

        sys.exit(0)

    except Exception as e:

        print(
            f"❌ خطأ أثناء تشغيل البرنامج: {e}"
        )

        traceback.print_exc()

        sys.exit(1)
