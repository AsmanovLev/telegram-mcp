import asyncio
from telethon import TelegramClient, functions
from telethon.sessions import StringSession

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PASSWORD = 'T3l3gr@m!DeeP2026X'

async def main():
    # Try with a fresh session and see if we can complete 2FA without new code
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS'), timeout=10)
    await client.connect()
    
    # Check if already authorized 
    me = await client.get_me()
    if me:
        s = StringSession.save(client.session)
        print(f'ALREADY_AUTH:{s}')
        return
    
    # Try to get pending 2FA state and submit password  
    try:
        pwd = await client(functions.account.GetPasswordRequest())
        print(f'HINT:{pwd.hint or "none"}')
        
        # Try to sign in with password directly (no code needed if pending)
        await client.sign_in(password=PASSWORD)
        s = StringSession.save(client.session)
        print(f'SESSION:{s}')
    except Exception as e:
        print(f'ERROR:{type(e).__name__}:{e}')
    
    await client.disconnect()

asyncio.run(main())
