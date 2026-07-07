import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY, timeout=10)
    await client.connect()
    
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'ALREADY_AUTHORIZED:{s}')
        return
    
    sent = await client.send_code_request(PHONE)
    print(f'CODE_SENT (hash: {sent.phone_code_hash[:10]}...)')
    
    # Try to get password hint without signing in first
    try:
        hint = await client.get_password_hint()
        if hint:
            print(f'HINT:{hint}')
        else:
            print('HINT:No hint set')
    except Exception as e:
        print(f'HINT_ERROR:{type(e).__name__}:{e}')
    
    # Also try sign-in with a placeholder to trigger the error properly
    try:
        await client.sign_in(PHONE, '00000', phone_code_hash=sent.phone_code_hash)
    except Exception as e:
        print(f'SIGNIN_ERROR:{type(e).__name__}:{e}')
        # Now check for hint
        try:
            hint = await client.get_password_hint()
            if hint:
                print(f'HINT:{hint}')
            else:
                print('HINT:No hint set')
        except Exception as e2:
            print(f'HINT_ERROR2:{type(e2).__name__}:{e2}')
    
    await client.disconnect()

asyncio.run(main())
