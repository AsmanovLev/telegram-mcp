import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')

async def check():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY)
    await client.connect()
    if not await client.is_user_authorized():
        result = await client.send_code_request(PHONE)
        print(f"Phone code hash: {result.phone_code_hash}")
        print(f"Timeout: {result.timeout}")
        print(f"Flood wait: {getattr(result, 'flood_wait', 0)}")
    else:
        print("Already authorized!")
    await client.disconnect()

asyncio.run(check())
