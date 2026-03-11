"""
                      [TeamDev](https://t.me/team_x_og)
          
          Project Id -> 30.
          Project Name -> TeamDev Auto-Forward
          Project Age -> 1Month+ (Updated On 11/03/2026)
          Project Idea By -> @MR_ARMAN_08
          Project Dev -> @MR_ARMAN_08
          Powered By -> @Team_X_Og ( On Telegram )
          Updates -> @CrimeZone_Update ( On telegram )
    
    Setup Guides -> Read > README.md
    
          This Script Part Off https://t.me/Team_X_Og's Team.
          Copyright ©️ 2026 TeamDev | @Team_X_Og

    Compatible In BotApi 9.5 Fully
"""

import re
import logging
from pyrogram import Client
from pyrogram.errors import (
    UsernameInvalid, UsernameNotOccupied, PeerIdInvalid,
    ChatAdminRequired, ChannelPrivate, FloodWait,
    UserNotParticipant, ChatForbidden,
)

log = logging.getLogger("nexus.validator")

_USERNAME_RE = re.compile(r"^@?[a-zA-Z][a-zA-Z0-9_]{2,30}$")
_LINK_RE     = re.compile(r"^(?:https?://)?t\.me/([a-zA-Z][a-zA-Z0-9_]{2,30})$")

_USERNAME_ONLY_ERROR = (
    "<b>Username required.</b>\n\n"
    "Only public @usernames and t.me links are supported.\n"
    "Numeric IDs are not accepted.\n\n"
    "<i>Valid examples:</i>\n"
    "<code>@mychannel</code>\n"
    "<code>https://t.me/mychannel</code>"
)


def parse_username_input(text: str) -> str | None:
    text = text.strip()

    m = _LINK_RE.match(text)
    if m:
        return f"@{m.group(1)}"

    if re.match(r"^-?\d+$", text):
        return None

    clean = text.lstrip("@")
    if _USERNAME_RE.match(f"@{clean}"):
        return f"@{clean}"

    return None


class ValidationResult:
    __slots__ = ("ok", "error", "chat_id", "chat_title", "username")

    def __init__(self, ok: bool, error: str = "", chat_id: int = 0,
                 chat_title: str = "", username: str = ""):
        self.ok         = ok
        self.error      = error
        self.chat_id    = chat_id
        self.chat_title = chat_title
        self.username   = username


async def validate_source(client: Client, user_id: int, raw_input: str) -> ValidationResult:
    identifier = parse_username_input(raw_input)
    if identifier is None:
        return ValidationResult(ok=False, error=_USERNAME_ONLY_ERROR)

    try:
        chat = await client.get_chat(identifier)
    except (UsernameInvalid, UsernameNotOccupied):
        return ValidationResult(ok=False, error=f"Username <code>{identifier}</code> does not exist on Telegram.")
    except PeerIdInvalid:
        return ValidationResult(ok=False, error="Cannot access that chat. Make sure the bot is a member.")
    except ChannelPrivate:
        return ValidationResult(ok=False, error="That channel is private. The bot cannot access it.")
    except FloodWait as e:
        return ValidationResult(ok=False, error=f"Telegram rate limit. Wait {e.value}s and try again.")
    except Exception as e:
        log.warning(f"[validator] get_chat({identifier}) error: {e}")
        return ValidationResult(ok=False, error=f"Could not resolve that channel: {e}")


    try:
        member = await client.get_chat_member(chat.id, user_id)
        from pyrogram.enums import ChatMemberStatus
        allowed = {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}
        if member.status not in allowed:
            return ValidationResult(
                ok=False,
                error="You must be a member or admin of that channel to use it as a source."
            )
    except UserNotParticipant:
        return ValidationResult(
            ok=False,
            error="You are not a member of that channel. Join it first, then add it as source."
        )
    except ChatForbidden:
        pass
    except Exception as e:
        log.warning(f"[validator] membership check skipped: {e}")

    uname = f"@{chat.username}" if chat.username else identifier
    return ValidationResult(ok=True, chat_id=chat.id, chat_title=chat.title or str(chat.id), username=uname)


async def validate_target(client: Client, raw_input: str) -> ValidationResult:
    identifier = parse_username_input(raw_input)
    if identifier is None:
        return ValidationResult(ok=False, error=_USERNAME_ONLY_ERROR)

    try:
        chat = await client.get_chat(identifier)
    except (UsernameInvalid, UsernameNotOccupied):
        return ValidationResult(ok=False, error=f"Username <code>{identifier}</code> does not exist.")
    except PeerIdInvalid:
        return ValidationResult(ok=False, error="Cannot access that chat.")
    except ChannelPrivate:
        return ValidationResult(ok=False, error="That channel is private. Add the bot as admin first.")
    except FloodWait as e:
        return ValidationResult(ok=False, error=f"Rate limit hit. Wait {e.value}s and try again.")
    except Exception as e:
        log.warning(f"[validator] get_chat({identifier}) error: {e}")
        return ValidationResult(ok=False, error=f"Could not resolve: {e}")

    try:
        me = await client.get_me()
        bot_member = await client.get_chat_member(chat.id, me.id)
        from pyrogram.enums import ChatMemberStatus
        if bot_member.status not in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR}:
            return ValidationResult(
                ok=False,
                error=(
                    f"Bot is not an admin in <b>{chat.title}</b>.\n"
                    "Add the bot as admin with <b>Post Messages</b> permission, then try again."
                )
            )
        priv = bot_member.privileges
        if priv and not priv.can_post_messages:
            return ValidationResult(
                ok=False,
                error=(
                    f"Bot is admin in <b>{chat.title}</b> but lacks "
                    "<b>Post Messages</b> permission. Please enable it."
                )
            )
    except UserNotParticipant:
        return ValidationResult(
            ok=False,
            error=(
                f"Bot is not in <b>{chat.title}</b>.\n"
                "Add it as admin with post permission first."
            )
        )
    except Exception as e:
        log.warning(f"[validator] bot admin check error for {chat.id}: {e}")
        return ValidationResult(ok=False, error=f"Could not verify bot admin status: {e}")

    uname = f"@{chat.username}" if chat.username else identifier
    return ValidationResult(ok=True, chat_id=chat.id, chat_title=chat.title or str(chat.id), username=uname)


async def validate_log_channel(client: Client, raw_input: str) -> ValidationResult:

    return await validate_target(client, raw_input)
