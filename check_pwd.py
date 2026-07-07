import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PASSWORD = 'T3l3gr@m!DeeP2026X'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS'), timeout=10)
    await client.connect()
    
    # Try to complete 2FA directly (pending challenge)
    try:
        await client.sign_in(password=PASSWORD)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except Exception as e:
        print(f'ERROR:{type(e).__name__}:{e}')
    
    await client.disconnect()

asyncio.run(main())
