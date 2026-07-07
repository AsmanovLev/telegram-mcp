import asyncio, os, sys
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')
CODE_FILE = '/tmp/telegram_code3.txt'
PWD_FILE = '/tmp/telegram_pwd.txt'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
        return
    
    if os.path.exists(CODE_FILE):
        os.remove(CODE_FILE)
    
    sent = await client.send_code_request(PHONE)
    print(f'CODE_SENT (hash: {sent.phone_code_hash[:10]}...)')
    sys.stdout.flush()
    
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
        await client.sign_in(PHONE, code, phone_code_hash=sent.phone_code_hash)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except SessionPasswordNeededError:
        print('2FA_NEEDED')
        sys.stdout.flush()
        # Get password hint
        try:
            pwd = await client(functions.account.GetPasswordRequest())
            if pwd.hint:
                print(f'HINT:{pwd.hint}')
            else:
                print('HINT:No hint set')
        except Exception as e:
            print(f'HINT_ERROR:{type(e).__name__}:{e}')
        
        # Try password from file
        for i in range(60):
            if os.path.exists(PWD_FILE):
                with open(PWD_FILE) as f:
                    pwd_str = f.read().strip()
                if pwd_str:
                    break
            await asyncio.sleep(1)
        else:
            print('PWD_TIMEOUT')
            return
        
        os.remove(PWD_FILE)
        await client.sign_in(password=pwd_str)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    
    await client.disconnect()

asyncio.run(main())
