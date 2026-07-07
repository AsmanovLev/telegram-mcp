#!/usr/bin/env python3
"""Telegram login: sends code, polls ADB notification, logs in, saves session"""
import asyncio, sys, re, subprocess
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 10409143
API_HASH = 'f69e8485c5b271e1bde17c225acc101f'
PHONE = '+79095400316'
PASSWORD = 'T3l3gr@m!DeeP2026X'
PROXY = ('http', '212.102.144.197', 9534, True, '4N0EgT', 'xr9kXS')

async def get_code_from_adb():
    """Poll ADB notification for Telegram login code"""
    for _ in range(30):
        await asyncio.sleep(0.5)
        try:
            r = subprocess.run(['adb', 'shell', 'dumpsys', 'notification', '--noredact'],
                             capture_output=True, text=True, timeout=3)
            match = re.search(r'(\d{5})\.', r.stdout)
            if match:
                return match.group(1)
        except:
            pass
    return None

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=PROXY)
    await client.connect()
    
    if await client.is_user_authorized():
        session_str = client.session.save()
        print(f"SESSION:{session_str}")
        await client.disconnect()
        return
    
    # Send code
    result = await client.send_code_request(PHONE)
    phone_code_hash = result.phone_code_hash
    print(f"Code sent, waiting for notification...")
    sys.stdout.flush()
    
    # Get code from ADB
    code = await get_code_from_adb()
    if not code:
        print("NO_CODE")
        await client.disconnect()
        return
    
    print(f"Got code: {code}")
    sys.stdout.flush()
    
    # Sign in
    try:
        await client.sign_in(PHONE, code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        print("2FA")
        await client.sign_in(password=PASSWORD)
    
    if await client.is_user_authorized():
        session_str = client.session.save()
        me = await client.get_me()
        print(f"SESSION:{session_str}")
        print(f"USER:{me.first_name} {me.last_name} (@{me.username})")
    else:
        print("LOGIN_FAILED")
    
    await client.disconnect()

asyncio.run(main())
