import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')
CODE = '92196'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'ALREADY_AUTHORIZED:{s}')
        return
    try:
        await client.sign_in(PHONE, CODE)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except Exception as e:
        print(f'ERROR:{type(e).__name__}:{e}')
    await client.disconnect()

asyncio.run(main())
