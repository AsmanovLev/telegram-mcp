import asyncio
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')
PASSWORD = 'T3l3gr@m!DeeP2026X'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'ALREADY_AUTH:{s}')
        return
    
    try:
        sent = await client.send_code_request(PHONE)
        print(f'CODE_SENT (hash: {sent.phone_code_hash[:10]}...)')
    except Exception as e:
        print(f'FLOOD_OR_ERROR:{type(e).__name__}:{e}')
        return
    
    # Wait for code from stdin
    code = input().strip()
    if not code:
        print('NO_CODE')
        return
    
    try:
        await client.sign_in(PHONE, code, phone_code_hash=sent.phone_code_hash)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except SessionPasswordNeededError:
        print('2FA_NEEDED')
        await client.sign_in(password=PASSWORD)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    
    await client.disconnect()

asyncio.run(main())
