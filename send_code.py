import asyncio, sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PASSWORD = 'T3l3gr@m!DeeP2026X'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY)
    await client.connect()
    
    if not await client.is_user_authorized():
        # Step 1: send code
        result = await client.send_code_request(PHONE)
        phone_code_hash = result.phone_code_hash
        print(f"PHONE_CODE_HASH:{phone_code_hash}")
        print("CODE_SENT")
    else:
        session_str = client.session.save()
        print(f"SESSION:{session_str}")
    
    await client.disconnect()

asyncio.run(main())
