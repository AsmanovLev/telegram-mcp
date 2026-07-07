import asyncio, sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PASSWORD = 'T3l3gr@m!DeeP2026X'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY)
    await client.connect()
    
    if not await client.is_user_authorized():
        result = await client.send_code_request(PHONE)
        phone_code_hash = result.phone_code_hash
        print(f"CODE_SENT_HASH:{phone_code_hash}")
        sys.stdout.flush()
        
        # Wait for code
        await asyncio.sleep(15)
        
        # Try to read from notification
        import subprocess
        try:
            r = subprocess.run(['adb', 'shell', 'dumpsys', 'notification', '--noredact'], 
                             capture_output=True, text=True, timeout=5)
            import re
            match = re.search(r'(\d{5})', r.stdout)
            if match:
                code = match.group(1)
                print(f"CODE_FOUND:{code}")
                try:
                    await client.sign_in(PHONE, code, phone_code_hash=phone_code_hash)
                except SessionPasswordNeededError:
                    print("2FA_REQUIRED")
                    await client.sign_in(password=PASSWORD)
        except Exception as e:
            print(f"ERROR:{e}")
        
        if await client.is_user_authorized():
            session_str = client.session.save()
            me = await client.get_me()
            print(f"SESSION:{session_str}")
            print(f"USER:{me.first_name} {me.last_name} (@{me.username})")
        else:
            print("LOGIN_FAILED")
    else:
        session_str = client.session.save()
        print(f"SESSION:{session_str}")
    
    await client.disconnect()

asyncio.run(main())
