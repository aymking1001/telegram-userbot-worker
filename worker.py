import asyncio

message = None

print("🔎 البحث عن الرسالة المحولة")
print("===================================")

for attempt in range(36):
    try:
        message = await client.get_messages(
            CHAT_ID,
            ids=MESSAGE_ID
        )

        if message:
            elapsed = attempt * 5

            print("===================================")
            print("✅ تم العثور على الرسالة المحولة.")
            print(f"⏱️ وقت الانتظار: {elapsed} ثانية")
            print(f"Message ID : {message.id}")
            print(f"Chat ID    : {CHAT_ID}")
            print("===================================")

            break

        remaining = 180 - (attempt * 5)

        print(
            f"⏳ الرسالة غير موجودة | "
            f"المحاولة {attempt + 1}/36 | "
            f"المتبقي {remaining} ثانية"
        )

        if attempt < 35:
            await asyncio.sleep(5)

    except Exception as e:
        print(f"⚠️ خطأ أثناء البحث عن الرسالة: {e}")

        if attempt < 35:
            print("⏳ إعادة المحاولة بعد 5 ثوانٍ...")
            await asyncio.sleep(5)

if not message:
    print("===================================")
    print("❌ لم يتم العثور على الرسالة بعد انتظار 3 دقائق.")
    print(f"CHAT_ID    : {CHAT_ID}")
    print(f"MESSAGE_ID : {MESSAGE_ID}")
    print("===================================")
    return
