import asyncio
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
    
    sent = await client.send_code_request(PHONE)
    print(f'CODE_RE_SENT (hash: {sent.phone_code_hash[:10]}...)')
    
    # Wait a moment for code
    await asyncio.sleep(5)
    print('WAITED_5S')

    # Actually, let's just check the password hint using account.getPassword
    try:
        pwd = await client(functions.account.GetPasswordRequest())
        hint = pwd.hint
        if hint:
            print(f'HINT:{hint}')
        else:
            print('HINT:No hint set')
        print(f'HAS_RECOVERY:{pwd.has_recovery}')
        print(f'HAS_SECURE_SECRET:{pwd.has_secure_values}')
    except Exception as e:
        print(f'PWD_ERROR:{type(e).__name__}:{e}')
    
    await client.disconnect()

asyncio.run(main())
