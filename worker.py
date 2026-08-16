import asyncio
import os
import sys
import tempfile
import mimetypes
import traceback

import requests

import cloudinary
import cloudinary.uploader

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError


def send_callback(callback_url, data):
    """
    إرسال نتيجة العملية إلى n8n
    """

    if not callback_url:
        print("⚠️ CALLBACK_URL غير موجود")
        return

    try:
        print("📡 إرسال النتيجة إلى n8n...")

        response = requests.post(
            callback_url,
            json=data,
            timeout=30
        )

        print(
            f"📡 n8n HTTP Status: {response.status_code}"
        )

        if response.ok:
            print("✅ تم إرسال النتيجة إلى n8n بنجاح")
        else:
            print(
                f"❌ فشل إرسال النتيجة إلى n8n: "
                f"{response.text[:500]}"
            )

    except Exception as e:
        print(
            f"❌ خطأ أثناء إرسال النتيجة إلى n8n: {e}"
        )


async def main():

    temp_path = None
    client = None

    try:

        # ============================================================
        # Telegram
        # ============================================================

        api_id = int(
            os.environ.get(
                "TELEGRAM_API_ID",
                0
            )
        )

        api_hash = os.environ.get(
            "TELEGRAM_API_HASH",
            ""
        )

        session_string = os.environ.get(
            "TELEGRAM_SESSION",
            ""
        )

        source_chat_id = os.environ.get(
            "SOURCE_CHAT_ID",
            ""
        )

        source_message_id = int(
            os.environ.get(
                "SOURCE_MESSAGE_ID",
                0
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
        # n8n callback
        # ============================================================

        callback_url = os.environ.get(
            "CALLBACK_URL",
            ""
        )

        # ============================================================
        # التحقق
        # ============================================================

        print("📋 التحقق من المتغيرات...")

        required = {
            "TELEGRAM_API_ID": api_id,
            "TELEGRAM_API_HASH": api_hash,
            "TELEGRAM_SESSION": session_string,
            "SOURCE_CHAT_ID": source_chat_id,
            "SOURCE_MESSAGE_ID": source_message_id,
            "CLOUDINARY_CLOUD_NAME": cloudinary_cloud_name,
            "CLOUDINARY_API_KEY": cloudinary_api_key,
            "CLOUDINARY_API_SECRET": cloudinary_api_secret,
            "CALLBACK_URL": callback_url,
        }

        missing = [
            key
            for key, value in required.items()
            if not value
        ]

        if missing:

            print(
                "❌ المتغيرات الناقصة:"
            )

            for item in missing:
                print(
                    f"   - {item}"
                )

            sys.exit(1)

        print("✅ جميع المتغيرات موجودة")

        print(
            f"📌 Source Chat ID: "
            f"{source_chat_id}"
        )

        print(
            f"📌 Source Message ID: "
            f"{source_message_id}"
        )

        print(
            f"📌 Source Username: "
            f"{source_username}"
        )

        print(
            f"☁️ Cloudinary Cloud Name: "
            f"{cloudinary_cloud_name}"
        )

        # ============================================================
        # Cloudinary
        # ============================================================

        cloudinary.config(
            cloud_name=cloudinary_cloud_name,
            api_key=cloudinary_api_key,
            api_secret=cloudinary_api_secret,
            secure=True
        )

        print(
            "✅ تم إعداد Cloudinary"
        )

        # ============================================================
        # Telegram Client
        # ============================================================

        client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash
        )

        try:

            # ========================================================
            # تسجيل الدخول
            # ========================================================

            print(
                "🔐 تسجيل الدخول إلى Telegram..."
            )

            await client.start()

            me = await client.get_me()

            print(
                "✅ تسجيل الدخول إلى Telegram نجح."
            )

            print(
                f"👤 الحساب: {me.first_name}"
            )

            print(
                f"🆔 Telegram ID: {me.id}"
            )

            # ========================================================
            # الوصول إلى المصدر
            # ========================================================

            print(
                "🔎 الوصول إلى المصدر..."
            )

            if source_username:

                try:

                    source_entity = await client.get_entity(
                        f"@{source_username}"
                    )

                except Exception:

                    source_entity = await client.get_entity(
                        int(source_chat_id)
                    )

            else:

                source_entity = await client.get_entity(
                    int(source_chat_id)
                )

            print(
                "✅ تم الوصول إلى المصدر."
            )

            # ========================================================
            # جلب الرسالة
            # ========================================================

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
                    "❌ لم يتم العثور على الرسالة."
                )

                send_callback(
                    callback_url,
                    {
                        "success": False,
                        "error": "MESSAGE_NOT_FOUND",
                        "source_message_id": source_message_id
                    }
                )

                sys.exit(1)

            print(
                f"✅ تم العثور على الرسالة "
                f"`{source_message.id}`."
            )

            # ========================================================
            # التحقق من الصوت
            # ========================================================

            if not (
                source_message.voice
                or source_message.audio
            ):

                print(
                    "❌ الرسالة لا تحتوي على صوتية."
                )

                send_callback(
                    callback_url,
                    {
                        "success": False,
                        "error": "NO_AUDIO",
                        "source_message_id": source_message_id
                    }
                )

                sys.exit(1)

            # ========================================================
            # معلومات الصوت
            # ========================================================

            if source_message.voice:

                media = source_message.voice

                media_type = "voice"

                file_size = media.size or 0

                mime_type = (
                    media.mime_type
                    or "audio/ogg"
                )

            else:

                media = source_message.audio

                media_type = "audio"

                file_size = media.size or 0

                mime_type = (
                    media.mime_type
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

            # ========================================================
            # الامتداد
            # ========================================================

            extension = mimetypes.guess_extension(
                mime_type
            )

            if not extension:

                if mime_type == "audio/mpeg":
                    extension = ".mp3"

                elif mime_type == "audio/ogg":
                    extension = ".ogg"

                else:
                    extension = ".audio"

            print(
                f"📄 امتداد الملف: "
                f"{extension}"
            )

            # ========================================================
            # ملف مؤقت
            # ========================================================

            temp_file = tempfile.NamedTemporaryFile(
                suffix=extension,
                delete=False
            )

            temp_path = temp_file.name

            temp_file.close()

            # ========================================================
            # تنزيل من Telegram
            # ========================================================

            print(
                "⬇️ تنزيل الصوت من Telegram..."
            )

            downloaded_file = await client.download_media(
                source_message,
                file=temp_path
            )

            if not downloaded_file:

                print(
                    "❌ فشل تنزيل الصوت."
                )

                send_callback(
                    callback_url,
                    {
                        "success": False,
                        "error": "TELEGRAM_DOWNLOAD_FAILED",
                        "source_message_id": source_message_id
                    }
                )

                sys.exit(1)

            downloaded_size = os.path.getsize(
                downloaded_file
            )

            print(
                "✅ تم تنزيل الصوت بنجاح."
            )

            print(
                f"📁 الملف المؤقت: "
                f"{downloaded_file}"
            )

            print(
                f"📦 الحجم بعد التنزيل: "
                f"{downloaded_size} بايت"
            )

            # ========================================================
            # رفع Cloudinary
            # ========================================================

            print(
                "☁️ رفع الصوت إلى Cloudinary..."
            )

            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                temp_path,
                resource_type="video"
            )

            # ========================================================
            # استخراج النتيجة
            # ========================================================

            secure_url = upload_result.get(
                "secure_url"
            )

            public_id = upload_result.get(
                "public_id"
            )

            resource_type = upload_result.get(
                "resource_type"
            )

            format_name = upload_result.get(
                "format"
            )

            if not secure_url:

                print(
                    "❌ Cloudinary لم يرجع الرابط."
                )

                send_callback(
                    callback_url,
                    {
                        "success": False,
                        "error": "CLOUDINARY_URL_MISSING",
                        "source_message_id": source_message_id
                    }
                )

                sys.exit(1)

            # ========================================================
            # نجاح
            # ========================================================

            print("")
            print(
                "============================================================"
            )

            print(
                "✅ رفع الصوت إلى Cloudinary نجح."
            )

            print(
                f"☁️ Public ID: {public_id}"
            )

            print(
                f"📦 Resource Type: {resource_type}"
            )

            print(
                f"🎼 Format: {format_name}"
            )

            print(
                f"🔗 Cloudinary URL:"
            )

            print(
                secure_url
            )

            print(
                "============================================================"
            )

            # ========================================================
            # إرسال الرابط إلى n8n
            # ========================================================

            callback_data = {

                "success": True,

                "cloudinary_url": secure_url,

                "cloudinary_public_id": public_id,

                "cloudinary_resource_type": resource_type,

                "cloudinary_format": format_name,

                "telegram_source_chat_id": source_chat_id,

                "telegram_source_message_id": source_message_id,

                "file_size": file_size,

                "mime_type": mime_type
            }

            send_callback(
                callback_url,
                callback_data
            )

            print(
                "🎉 انتهت المهمة بنجاح."
            )

        except SessionPasswordNeededError:

            print(
                "❌ مطلوب كلمة مرور للجلسة."
            )

            send_callback(
                callback_url,
                {
                    "success": False,
                    "error": "SESSION_PASSWORD_NEEDED"
                }
            )

            sys.exit(1)

        except Exception as e:

            print(
                f"❌ خطأ في Telegram: {e}"
            )

            traceback.print_exc()

            send_callback(
                callback_url,
                {
                    "success": False,
                    "error": str(e)
                }
            )

            sys.exit(1)

    except Exception as e:

        print(
            f"❌ خطأ غير متوقع: {e}"
        )

        traceback.print_exc()

        sys.exit(1)

    finally:

        # ============================================================
        # حذف الملف
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
        # Telegram disconnect
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

        asyncio.run(
            main()
        )

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
