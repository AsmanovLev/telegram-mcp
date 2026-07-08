"""Event-driven incoming-message tracking + debounce (settle window) + channel event cache.

Lets agents react to new client messages instead of polling. A Telethon
NewMessage(incoming=True) handler records incoming private (non-bot, non-self)
messages per chat; the two tools below expose them, with wait_for_settled_message
debouncing a burst (several messages typed in a row) into a single settled event.

Also caches new messages from monitored channels (folder sources) into a JSON
file, so get_message_updates can return them without calling get_history.
"""

import asyncio
import json
import time
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from collections import deque

from telethon import events as _events
from telethon import utils

from telegram_mcp.runtime import *  # mcp, clients, ToolAnnotations, log_and_format_error

# === Private message debounce (existing) ===
# chat_id -> {first_ts, last_ts, count, first_id, last_id, name, username}
_pending_msgs: Dict[int, Dict[str, Any]] = {}
_activity_event: Optional[asyncio.Event] = None

# === Channel event cache (new) ===
CACHE_DIR = Path.home() / '.hermes' / 'data' / 'tg_events'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / 'events.json'
MAX_CACHE_EVENTS = 10000
MAX_CACHE_AGE = 24 * 3600  # 24 hours

# Folder sources chat IDs
FOLDER_CHAT_IDS = {
    -1001288489154, -1001754906826, -1001391345080, -1001319248631,
    -1001307778786, -1001279926928, -1001418440636, -1001202159807,
    -1001827745282, -1001863130748, -1001767686479, -1001747110091,
    -1001752992242, -1001742369677, -1001708761316, -1001381927809,
    -1001009232144, -1001607197661,
}

_channel_cache: deque = deque(maxlen=MAX_CACHE_EVENTS)

def _load_cache():
    if CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text())
            _channel_cache.extend(data)
            _prune_cache()
        except:
            pass

def _save_cache():
    CACHE_FILE.write_text(json.dumps(list(_channel_cache), ensure_ascii=False))

def _prune_cache():
    cutoff = time.time() - MAX_CACHE_AGE
    while _channel_cache and _channel_cache[0]['ts'] < cutoff:
        _channel_cache.popleft()

# Load existing cache on import
_load_cache()


def _get_activity_event() -> asyncio.Event:
    """Lazily create the asyncio.Event on the running loop."""
    global _activity_event
    if _activity_event is None:
        _activity_event = asyncio.Event()
    return _activity_event


async def _on_new_incoming(event) -> None:
    """Record incoming private (non-bot, non-self) messages for the debounce tools."""
    try:
        if not event.is_private:
            return
        sender = await event.get_sender()
        if sender is None:
            return
        if getattr(sender, "bot", False) or getattr(sender, "is_self", False):
            return
        chat_id = event.chat_id
        now = time.time()
        msg_id = event.message.id
        rec = _pending_msgs.get(chat_id)
        if rec is None:
            _pending_msgs[chat_id] = {
                "first_ts": now,
                "last_ts": now,
                "count": 1,
                "first_id": msg_id,
                "last_id": msg_id,
                "name": utils.get_display_name(sender) or str(chat_id),
                "username": getattr(sender, "username", None),
            }
        else:
            rec["last_ts"] = now
            rec["last_id"] = msg_id
            rec["count"] += 1
        _get_activity_event().set()
    except Exception:
        logging.getLogger("telegram_mcp").exception("error in _on_new_incoming")


async def _on_channel_message(event) -> None:
    """Cache messages from any chat for later filtering in get_message_updates."""
    try:
        chat = await event.get_chat()
        if not hasattr(chat, 'id'):
            return
        
        chat_id = chat.id
        msg = event.message
        now = time.time()
        
        _channel_cache.append({
            'id': msg.id,
            'chat_id': chat_id,
            'chat_title': getattr(chat, 'title', getattr(chat, 'first_name', str(chat_id))),
            'username': getattr(chat, 'username', ''),
            'text': msg.text or '',
            'ts': msg.date.timestamp() if msg.date else now,
            'media': bool(msg.media),
            'has_video': bool(msg.video) if hasattr(msg, 'video') else False,
            'has_photo': bool(msg.photo) if hasattr(msg, 'photo') else False,
            'views': getattr(msg, 'views', 0),
            'forwards': getattr(msg, 'forwards', 0),
        })
        
        _prune_cache()
        if len(_channel_cache) % 20 == 0:
            _save_cache()
    except Exception:
        logging.getLogger("telegram_mcp").exception("error in _on_channel_message")


def register_incoming_handlers() -> None:
    """Attach handlers to every configured client."""
    for cl in clients.values():
        try:
            cl.add_event_handler(_on_new_incoming, _events.NewMessage(incoming=True))
        except Exception:
            logging.getLogger("telegram_mcp").exception("failed to register incoming handler")
        try:
            cl.add_event_handler(_on_channel_message, _events.NewMessage())
        except Exception:
            logging.getLogger("telegram_mcp").exception("failed to register channel handler")


@mcp.tool(
    annotations=ToolAnnotations(
        title="Wait For New Message", openWorldHint=True, readOnlyHint=True
    )
)
async def wait_for_new_message(timeout: float = 50.0) -> str:
    """
    Block until a new incoming private message from a non-bot user arrives, then
    return immediately with the list of chats that currently have pending
    (unprocessed) incoming messages. If nothing arrives within `timeout` seconds,
    returns {"event": false, "reason": "timeout"}. Lets the agent react to events
    instead of polling. Does NOT consume the pending set — use
    wait_for_settled_message to consume a debounced burst.

    Args:
        timeout: Max seconds to block (default 50).
    """
    try:
        ev = _get_activity_event()
        if not _pending_msgs:
            ev.clear()
            try:
                await asyncio.wait_for(ev.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                return json.dumps({"event": False, "reason": "timeout"}, ensure_ascii=False)
        chats = [
            {
                "chat_id": cid,
                "name": rec["name"],
                "username": rec["username"],
                "count": rec["count"],
                "last_message_id": rec["last_id"],
            }
            for cid, rec in _pending_msgs.items()
        ]
        return json.dumps({"event": True, "pending_chats": chats}, ensure_ascii=False)
    except Exception as e:
        return log_and_format_error("wait_for_new_message", e)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Wait For Settled Message", openWorldHint=True, readOnlyHint=True
    )
)
async def wait_for_settled_message(settle_ms: int = 6000, max_wait_ms: int = 50000) -> str:
    """
    Event-driven, DEBOUNCED wait. Blocks until some private user chat has received
    one or more incoming messages AND then gone quiet for `settle_ms` — so a client
    who types several messages (or sends file + text) in a row is delivered as ONE
    settled burst instead of waking the agent on every message. Returns that chat's
    burst summary and removes it from the pending set, so the next call returns the
    next settled chat. If no chat settles within `max_wait_ms`, returns
    {"event": false, "reason": "timeout"} (caller should simply call again).

    Recommended usage (replaces blind per-minute polling): call this, get a settled
    chat, process it (read full history -> draft -> notify -> mark read), call again.

    Args:
        settle_ms: Quiet period after the LAST message before a burst is "settled"
            (default 6000 = 6s). Each new message in the chat resets this timer.
        max_wait_ms: Max total time to block before returning a timeout (default 50000).
    """
    try:
        settle = settle_ms / 1000.0
        deadline = time.time() + max_wait_ms / 1000.0
        ev = _get_activity_event()
        while True:
            now = time.time()
            settled_cid = None
            soonest_remaining = None
            for cid, rec in list(_pending_msgs.items()):
                quiet = now - rec["last_ts"]
                if quiet >= settle:
                    settled_cid = cid
                    break
                rem = settle - quiet
                if soonest_remaining is None or rem < soonest_remaining:
                    soonest_remaining = rem
            if settled_cid is not None:
                rec = _pending_msgs.pop(settled_cid)
                return json.dumps(
                    {
                        "event": True,
                        "chat_id": settled_cid,
                        "name": rec["name"],
                        "username": rec["username"],
                        "message_count": rec["count"],
                        "first_message_id": rec["first_id"],
                        "last_message_id": rec["last_id"],
                        "burst_seconds": round(rec["last_ts"] - rec["first_ts"], 2),
                    },
                    ensure_ascii=False,
                )
            remaining_total = deadline - now
            if remaining_total <= 0:
                return json.dumps({"event": False, "reason": "timeout"}, ensure_ascii=False)
            if soonest_remaining is not None:
                # A chat is pending but not yet quiet — sleep until it would settle,
                # then re-check (a new message meanwhile resets its timer).
                await asyncio.sleep(min(soonest_remaining, remaining_total))
            else:
                # Nothing pending — block on new activity until deadline.
                ev.clear()
                try:
                    await asyncio.wait_for(ev.wait(), timeout=remaining_total)
                except asyncio.TimeoutError:
                    return json.dumps({"event": False, "reason": "timeout"}, ensure_ascii=False)
    except Exception as e:
        return log_and_format_error("wait_for_settled_message", e)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Message Updates", openWorldHint=True, readOnlyHint=True
    )
)
async def get_message_updates(
    minutes_offset: int = 60,
    limit: int = 50,
    folder_name: str = None,
    chat_ids: list = None,
) -> str:
    """
    Get recent messages from the event-driven cache without calling get_history.

    Args:
        minutes_offset: How many minutes back to look (default 60). 0 = no time filter.
        limit: Max messages to return (default 50).
        folder_name: Filter by folder ('Агрегация', etc.). None = no folder filter.
        chat_ids: Filter by specific chat IDs. None = no chat filter.
    """
    try:
        cutoff = time.time() - minutes_offset * 60 if minutes_offset > 0 else 0
        
        # Resolve folder filter to chat IDs
        filter_chat_ids = None
        if folder_name:
            if folder_name == 'Агрегация':
                filter_chat_ids = FOLDER_CHAT_IDS.copy()
        if chat_ids:
            filter_chat_ids = set(chat_ids) if filter_chat_ids is None else filter_chat_ids & set(chat_ids)
        
        results = []
        for e in reversed(_channel_cache):
            if cutoff and e['ts'] < cutoff:
                break
            if filter_chat_ids and e.get('chat_id') not in filter_chat_ids:
                continue
            results.append(e)
            if len(results) >= limit:
                break
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return log_and_format_error("get_message_updates", e)


# Wire up the listener as soon as this module is imported (alongside tool registration).
register_incoming_handlers()


__all__ = [
    "wait_for_new_message",
    "wait_for_settled_message",
    "get_message_updates",
    "register_incoming_handlers",
]
