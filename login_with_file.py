import asyncio, sys, os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')
CODE_FILE = '/tmp/telegram_code.txt'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
        return
    
    if os.path.exists(CODE_FILE):
        os.remove(CODE_FILE)
    
    await client.send_code_request(PHONE)
    print('CODE_SENT')
    sys.stdout.flush()
    
    # Wait for code file
    for _ in range(60):
        if os.path.exists(CODE_FILE):
            with open(CODE_FILE) as f:
                code = f.read().strip()
            if code:
                break
        await asyncio.sleep(1)
    else:
        print('TIMEOUT')
        return
    
    os.remove(CODE_FILE)
    print(f'CODE:{code}', file=sys.stderr)
    await client.sign_in(PHONE, code)
    s = StringSession.save(client.session)
    print(f'SESSION:{s}')
    await client.disconnect()

asyncio.run(main())
