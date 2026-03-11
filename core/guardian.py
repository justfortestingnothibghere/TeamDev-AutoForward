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

from functools import wraps
from pyrogram.enums import ParseMode
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton as Btn
import environ
from vault import store
from wire import glyph as G


async def _get_lang(uid: int) -> str:
    from wire.i18n import get_user_lang_cache, set_user_lang_cache
    try:
        cached = get_user_lang_cache(uid)
        if cached:
            return cached
        lang = await store.get_user_lang(uid)
        set_user_lang_cache(uid, lang)
        return lang
    except Exception:
        return "en"


def _t(key: str, lang: str) -> str:
    from wire.i18n import t
    return t(key, lang)


def _uid(update) -> int:
    return update.from_user.id if update.from_user else 0


async def _check_force_join(client, user_id: int) -> list[str]:
    from vault import store
    db_channels = await store.get_force_join_channels()
    all_channels = list(dict.fromkeys(environ.FORCE_JOIN + db_channels))
    missing = []
    for ch in all_channels:
        try:
            member = await client.get_chat_member(ch, user_id)
            from pyrogram.enums import ChatMemberStatus
            if member.status in (
                ChatMemberStatus.BANNED, ChatMemberStatus.LEFT,
                ChatMemberStatus.RESTRICTED
            ):
                missing.append(ch)
        except Exception:
            missing.append(ch)
    return missing


def _force_join_kb(missing: list, lang: str = "en") -> InlineKeyboardMarkup:
    rows = []
    for ch in missing:
        url = f"https://t.me/{ch.lstrip('@')}" if ch.startswith("@") else f"https://t.me/c/{str(ch).lstrip('-100')}/1"
        rows.append([Btn(f"{G.ARR2} {_t('Join', lang)} {ch}", url=url)])
    rows.append([Btn(f"{G.CHECK}  {_t('Check Again', lang)}", callback_data="fj_check")])
    return InlineKeyboardMarkup(rows)


def owner_only(func):
    @wraps(func)
    async def wrapper(client, update, *args, **kwargs):
        uid  = _uid(update)
        lang = await _get_lang(uid)
        if uid != environ.OWNER_ID:
            if isinstance(update, CallbackQuery):
                await update.answer(_t("Owner only.", lang), show_alert=True)
            else:
                await update.reply(
                    f"<b>{_t('Access Denied', lang)}</b>\n{G.LINE}\n"
                    f"{_t('Owner only.', lang)}",
                    parse_mode=ParseMode.HTML
                )
            return
        return await func(client, update, *args, **kwargs)
    return wrapper


def auth_required(func):
    @wraps(func)
    async def wrapper(client, update, *args, **kwargs):
        uid  = _uid(update)
        lang = await _get_lang(uid)
        if environ.FORCE_JOIN and uid != environ.OWNER_ID:
            missing = await _check_force_join(client, uid)
            if missing:
                chs = ", ".join(missing)
                msg_text = (
                    f"<b>{G.WARN}  {_t('Join Required', lang)}</b>\n{G.LINE}\n\n"
                    f"{_t('You must join the following channels to use this bot:', lang)}\n\n"
                    f"<code>{chs}</code>\n\n"
                    f"<i>{_t('Click below to join, then press Check Again.', lang)}</i>"
                )
                kb = _force_join_kb(missing, lang)
                if isinstance(update, CallbackQuery):
                    await update.answer(_t("Join required channels first!", lang), show_alert=True)
                    try:
                        await update.message.edit_text(msg_text, parse_mode=ParseMode.HTML, reply_markup=kb)
                    except Exception:
                        pass
                else:
                    await update.reply(msg_text, parse_mode=ParseMode.HTML, reply_markup=kb)
                return

        if not await store.is_authorized(uid):
            if isinstance(update, CallbackQuery):
                await update.answer(_t("Not authorized.", lang), show_alert=True)
            else:
                await update.reply(
                    f"<b>{_t('Access Denied', lang)}</b>\n{G.LINE}\n"
                    f"{_t('You are not authorized.', lang)}",
                    parse_mode=ParseMode.HTML
                )
            return
        return await func(client, update, *args, **kwargs)
    return wrapper


def perm_required(perm: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, update, *args, **kwargs):
            uid = _uid(update)
            if not await store.has_perm(uid, perm):
                if isinstance(update, CallbackQuery):
                    await update.answer(
                        G.g(f"Missing permission: {perm}"), show_alert=True
                    )
                else:
                    await update.reply(
                        f"<b>{G.g('Permission Required')}</b>: <code>{perm}</code>",
                        parse_mode=ParseMode.HTML
                    )
                return
            return await func(client, update, *args, **kwargs)
        return wrapper
    return decorator


LINE = G.LINE
