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

import logging
import environ
from vault import store
from wire import glyph as G
from pyrogram.enums import ParseMode

log = logging.getLogger("TeamDev.logger")
_app = None
_log_channel_ok = False


def init(app):
    global _app
    _app = app


async def validate_log_channel():
    global _log_channel_ok
    if not _app or not environ.LOG_CHANNEL:
        _log_channel_ok = False
        return

    try:
        await _app.send_message(
            environ.LOG_CHANNEL,
            f"<b>{G.STAR} TeamDev v{environ.VERSION} started.</b>\n"
            f"<code>Log channel connection verified.</code>",
            parse_mode=ParseMode.HTML,
        )
        _log_channel_ok = True
        log.info(f"[logger] Log channel {environ.LOG_CHANNEL} — OK")
    except Exception as e:
        _log_channel_ok = False
        log.error(
            f"[logger] *** LOG CHANNEL ERROR ***\n"
            f"  Channel : {environ.LOG_CHANNEL}\n"
            f"  Error   : {e}\n"
            f"  Fix     : Set LOG_CHANNEL=@channelusername in .env\n"
            f"            Make sure the bot is admin in that channel."
        )


async def emit(user_id: int, action: str, detail: str = "", level: str = "info"):
    await store.log_activity(user_id, action, detail)

    if not _app or not environ.LOG_CHANNEL or not _log_channel_ok:
        return

    prefix = {
        "info":    G.INFO,
        "success": G.CHECK,
        "warn":    G.WARN,
        "error":   G.ERR,
        "admin":   G.ADMIN,
        "owner":   G.CROWN,
        "pipe":    G.PIPE,
        "fwd":     G.ARR2,
    }.get(level, G.DOT)

    text = (
        f"<b>{prefix} {G.g(action)}</b>\n"
        f"{G.LINE}\n"
        f"<b>{G.g('User')}:</b> <code>{user_id}</code>\n"
        f"<b>{G.g('Detail')}:</b> {detail or G.g('none')}\n"
        f"{G.THIN}"
    )

    try:
        await _app.send_message(environ.LOG_CHANNEL, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        log.warning(f"[logger] Failed to send to log channel: {e}")