import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
CODE = '46938'
PASSWORD = 'T3l3gr@m!DeeP2026X'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS'), timeout=10)
    await client.connect()
    
    # Use start() with code and password pre-provided
    await client.start(phone=lambda: PHONE, code_callback=lambda: CODE, password=lambda: PASSWORD)
    
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    
    await client.disconnect()

asyncio.run(main())
