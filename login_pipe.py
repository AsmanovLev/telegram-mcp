import asyncio, os, sys
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
        return
    
    sent = await client.send_code_request(PHONE)
    print(f'CODE_SENT (hash: {sent.phone_code_hash[:10]}...)')
    sys.stdout.flush()
    
    # Wait for code from stdin
    code = sys.stdin.readline().strip()
    if not code:
        print('NO_CODE')
        return
    
    try:
        await client.sign_in(PHONE, code, phone_code_hash=sent.phone_code_hash)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except SessionPasswordNeededError:
        print('2FA_NEEDED')
        sys.stdout.flush()
        # Get hint
        pwd = await client(functions.account.GetPasswordRequest())
        print(f'HINT:{pwd.hint or "none"}')
        
        # Wait for password from stdin
        pwd_str = sys.stdin.readline().strip()
        if not pwd_str:
            print('NO_PWD')
            return
        
        await client.sign_in(password=pwd_str)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    
    await client.disconnect()

asyncio.run(main())
