from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 123456  # رقمك من my.telegram.org
API_HASH = 'your_api_hash_here'  # مفتاحك

async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        await client.start()
        session = client.session.save()
        print(f"TELEGRAM_SESSION={session}")
        # انسخ الناتج بالكامل وأضفه كـ Secret

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
