import asyncio, os, sys
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')
CODE_FILE = '/tmp/telegram_code2.txt'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
        return
    
    if os.path.exists(CODE_FILE):
        os.remove(CODE_FILE)
    
    # Send code and get hash
    sent = await client.send_code_request(PHONE)
    code_hash = sent.phone_code_hash
    print(f'CODE_SENT (hash: {code_hash[:10]}...)')
    sys.stdout.flush()
    
    # Wait for code file
    for i in range(120):
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
    
    try:
        await client.sign_in(PHONE, code, phone_code_hash=code_hash)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except Exception as e:
        print(f'ERROR:{type(e).__name__}:{e}')
    
    await client.disconnect()

asyncio.run(main())
