name: Telegram UserBot Worker

on:
  workflow_dispatch:
    inputs:
      chat_id:
        description: 'معرف المحادثة المراد الإرسال إليها'
        required: true
        type: string
      message_id:
        description: 'رقم الرسالة الموجودة'
        required: true
        type: string
      source_chat_id:
        description: 'معرف المحادثة الأصلية'
        required: true
        type: string
      source_message_id:
        description: 'رقم الرسالة الأصلية'
        required: true
        type: string
      source_username:
        description: 'اسم المستخدم للمصدر'
        required: false
        type: string
        default: ''

jobs:
  forward-voice:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install telethon

      - name: Create Python script
        run: |
          cat > forward_voice.py << 'EOF'
          import asyncio
          import os
          import sys
          from telethon import TelegramClient
          from telethon.errors import SessionPasswordNeededError

          async def main():
              # قراءة المتغيرات من GitHub Actions
              api_id = int(os.environ.get('API_ID'))
              api_hash = os.environ.get('API_HASH')
              session_string = os.environ.get('TELEGRAM_SESSION')
              
              chat_id = os.environ.get('INPUT_CHAT_ID')
              message_id = int(os.environ.get('INPUT_MESSAGE_ID'))
              source_chat_id = os.environ.get('INPUT_SOURCE_CHAT_ID')
              source_message_id = int(os.environ.get('INPUT_SOURCE_MESSAGE_ID'))
              source_username = os.environ.get('INPUT_SOURCE_USERNAME', '')

              print(f"Chat ID: {chat_id}")
              print(f"Message ID: {message_id}")
              print(f"Source Chat ID: {source_chat_id}")
              print(f"Source Message ID: {source_message_id}")

              # إنشاء العميل
              client = TelegramClient(
                  StringSession(session_string),
                  api_id,
                  api_hash
              )

              try:
                  # تسجيل الدخول
                  await client.start()
                  print("✅ تم تسجيل الدخول بنجاح")

                  # جلب الرسالة الأصلية
                  try:
                      source_entity = await client.get_entity(source_chat_id)
                      target_entity = await client.get_entity(chat_id)
                      
                      # جلب الرسالة الأصلية
                      source_message = await client.get_messages(
                          source_entity,
                          ids=source_message_id
                      )
                      
                      if source_message is None:
                          print(f"❌ لم يتم العثور على الرسالة رقم {source_message_id} في المصدر")
                          sys.exit(1)
                      
                      print(f"✅ تم العثور على الرسالة الأصلية")
                      
                      # التحقق من وجود صوت في الرسالة
                      if source_message.voice:
                          print(f"🎵 تم العثور على ملف صوتي، حجمه: {source_message.voice.size} بايت")
                          
                          # إرسال الملف الصوتي مع النص المرفق
                          caption = source_message.text or "تم إعادة التوجيه"
                          
                          # إرسال الصوت مع النص
                          await client.send_file(
                              target_entity,
                              file=source_message.media,
                              caption=caption,
                              reply_to=message_id if message_id else None,
                              voice_note=True  # إرسال كملاحظة صوتية
                          )
                          print("✅ تم إرسال الملف الصوتي بنجاح")
                          
                      elif source_message.audio:
                          print(f"🎵 تم العثور على ملف صوتي، حجمه: {source_message.audio.size} بايت")
                          
                          caption = source_message.text or "تم إعادة التوجيه"
                          
                          await client.send_file(
                              target_entity,
                              file=source_message.media,
                              caption=caption,
                              reply_to=message_id if message_id else None
                          )
                          print("✅ تم إرسال الملف الصوتي بنجاح")
                          
                      else:
                          print("❌ الرسالة لا تحتوي على ملف صوتي")
                          sys.exit(1)
                          
                  except ValueError as e:
                      print(f"❌ خطأ في معرف المحادثة: {e}")
                      sys.exit(1)
                  except Exception as e:
                      print(f"❌ خطأ أثناء جلب الرسالة: {e}")
                      sys.exit(1)

              except SessionPasswordNeededError:
                  print("❌ مطلوب كلمة مرور للجلسة")
                  sys.exit(1)
              except Exception as e:
                  print(f"❌ خطأ في تسجيل الدخول: {e}")
                  sys.exit(1)
              finally:
                  await client.disconnect()
                  print("🔌 تم قطع الاتصال")

          if __name__ == "__main__":
              try:
                  from telethon import TelegramClient
                  from telethon.sessions import StringSession
                  
                  asyncio.run(main())
              except ImportError:
                  print("❌ خطأ: Telethon غير مثبت")
                  sys.exit(1)
              except Exception as e:
                  print(f"❌ خطأ غير متوقع: {e}")
                  sys.exit(1)
          EOF

      - name: Run Telegram UserBot
        env:
          API_ID: ${{ secrets.API_ID }}
          API_HASH: ${{ secrets.API_HASH }}
          TELEGRAM_SESSION: ${{ secrets.TELEGRAM_SESSION }}
          INPUT_CHAT_ID: ${{ github.event.inputs.chat_id }}
          INPUT_MESSAGE_ID: ${{ github.event.inputs.message_id }}
          INPUT_SOURCE_CHAT_ID: ${{ github.event.inputs.source_chat_id }}
          INPUT_SOURCE_MESSAGE_ID: ${{ github.event.inputs.source_message_id }}
          INPUT_SOURCE_USERNAME: ${{ github.event.inputs.source_username }}
        run: python forward_voice.py
