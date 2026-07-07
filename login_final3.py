import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')
CODE = '46938'
PASSWORD = 'T3l3gr@m!DeeP2026X'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
        return
    sent = await client.send_code_request(PHONE)
    try:
        await client.sign_in(PHONE, CODE, phone_code_hash=sent.phone_code_hash)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except SessionPasswordNeededError:
        print('2FA')
        await client.sign_in(password=PASSWORD)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    await client.disconnect()

asyncio.run(main())
