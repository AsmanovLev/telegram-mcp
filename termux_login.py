import asyncio, sys
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, timeout=10)
    await client.connect()
    if await client.is_user_authorized():
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
        return
    sent = await client.send_code_request(PHONE)
    print(f'CODE_SENT (hash: {sent.phone_code_hash[:10]}...)')
    sys.stdout.flush()
    code = sys.stdin.readline().strip()
    try:
        await client.sign_in(PHONE, code, phone_code_hash=sent.phone_code_hash)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except Exception as e:
        if '2FA' in str(e) or 'password' in str(e).lower():
            print('2FA_NEEDED')
            sys.stdout.flush()
            pwd = sys.stdin.readline().strip()
            await client.sign_in(password=pwd)
            s = StringSession.save(client.session)
            print(f'SESSION:{s}')
        else:
            print(f'ERROR:{e}')
    await client.disconnect()

asyncio.run(main())
