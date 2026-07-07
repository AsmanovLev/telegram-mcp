import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import functions

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    
    sent = await client.send_code_request(PHONE)
    print(f'CODE_SENT (hash: {sent.phone_code_hash[:10]}...)')
    
    # Try signing in with correct code first
    await client.sign_in(PHONE, '85439', phone_code_hash=sent.phone_code_hash)

asyncio.run(main())
