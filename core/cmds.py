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

import json
import html
import logging
import re as _re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton as IBtn
)
from core.guardian import auth_required
from core import logger
from vault import store
from wire import glyph as G
from wire.i18n import t as _t, LANGUAGES, make_lang_buttons

log = logging.getLogger("nexus.cmds")

BUILTINS = {
    "start", "menu", "help", "pipes", "new", "stats", "admins",
    "add_cmd", "del_cmd", "cmds", "cmd_schema", "channels",
    "ping", "health", "lang",
}


def escape(text: str) -> str:
    return html.escape(str(text))


async def _lang(uid: int) -> str:
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


def _build_keyboard(buttons: list) -> InlineKeyboardMarkup | None:
    if not buttons:
        return None
    rows = []
    for row in buttons:
        if not isinstance(row, list):
            row = [row]
        r = []
        for btn in row:
            if not isinstance(btn, dict):
                continue
            text = str(btn.get("text", "Button"))
            if "url" in btn:
                r.append(IBtn(text, url=str(btn["url"])))
            elif "callback" in btn:
                r.append(IBtn(text, callback_data=str(btn["callback"])[:64]))
        if r:
            rows.append(r)
    return InlineKeyboardMarkup(rows) if rows else None


def validate_command_payload(data: dict) -> tuple[bool, str]:
    cmd = data.get("command", "")
    if not cmd:
        return False, "Missing <code>command</code> field."
    if not _re.match(r"^[a-z0-9_]{1,32}$", cmd.lstrip("/")):
        return False, (
            f"Invalid command name <code>{escape(cmd)}</code>.\n"
            "Only lowercase letters, digits, underscores. Max 32 chars."
        )
    if cmd.lstrip("/") in BUILTINS:
        return False, f"<code>/{escape(cmd.lstrip('/'))}</code> is a reserved built-in command."

    text = data.get("text", "")
    if not text and not data.get("photo") and not data.get("video"):
        return False, "Command must have at least a <code>text</code>, <code>photo</code>, or <code>video</code>."

    buttons = data.get("buttons", [])
    if buttons and not isinstance(buttons, list):
        return False, "<code>buttons</code> must be a JSON array."
    for i, row in enumerate(buttons):
        if not isinstance(row, list):
            return False, f"<code>buttons[{i}]</code> must be a list (row of buttons)."
        for j, btn in enumerate(row):
            if not isinstance(btn, dict):
                return False, f"<code>buttons[{i}][{j}]</code> must be an object."
            if "text" not in btn:
                return False, f"<code>buttons[{i}][{j}]</code> missing <code>text</code>."
            if "url" not in btn and "callback" not in btn:
                return False, f"<code>buttons[{i}][{j}]</code> needs <code>url</code> or <code>callback</code>."
            if "url" in btn:
                url = str(btn["url"])
                if not url.startswith(("http://", "https://", "tg://")):
                    return False, (
                        f"<code>buttons[{i}][{j}].url</code> must start with "
                        "<code>https://</code>, <code>http://</code>, or <code>tg://</code>."
                    )
    return True, ""


async def dispatch_custom_command(client: Client, msg: Message):
    """
    Dispatch a custom command.
    
    BUG FIX: When using filters.create(), Pyrogram does NOT set msg.command
    because it only populates msg.command for handlers registered with
    filters.command(). We therefore parse the command name directly from
    msg.text to fix /add_cmd hello → /hello not working.
    """
    if not msg.text:
        return

    raw = msg.text.strip()
    if not raw.startswith("/"):
        return

    cmd_part = raw.split()[0].lstrip("/")
    if "@" in cmd_part:
        cmd_part = cmd_part.split("@")[0]
    cmd_name = cmd_part.lower()

    if not cmd_name or cmd_name in BUILTINS:
        return

    cmd = await store.get_command(cmd_name)
    if not cmd:
        return
    if not cmd.get("enabled", True):
        return

    payload  = cmd.get("payload", {})
    text     = payload.get("text", "")
    photo    = payload.get("photo")
    video    = payload.get("video")
    buttons  = payload.get("buttons", [])
    keyboard = _build_keyboard(buttons)

    try:
        if photo:
            await msg.reply_photo(
                photo        = photo,
                caption      = text or None,
                parse_mode   = ParseMode.HTML,
                reply_markup = keyboard,
            )
        elif video:
            await msg.reply_video(
                video        = video,
                caption      = text or None,
                parse_mode   = ParseMode.HTML,
                reply_markup = keyboard,
            )
        else:
            if not text:
                return
            await msg.reply(
                text,
                parse_mode   = ParseMode.HTML,
                reply_markup = keyboard,
            )
        await store.bump_cmd_use(cmd_name)
        log.info(f"[cmds] /{cmd_name} dispatched to uid={msg.from_user.id}")

    except Exception as e:
        log.error(f"[cmds] dispatch /{cmd_name} error: {e}")


CMD_SCHEMA_EXAMPLE = {
    "command": "hello",
    "text": "<b>Hello!</b>\nWelcome!\n<i>This is a custom command.</i>",
    "parse_mode": "html",
    "photo": None,
    "video": None,
    "enabled": True,
    "buttons": [
        [
            {"text": "Visit Website", "url": "https://example.com"},
            {"text": "Support",       "url": "https://t.me/support"}
        ],
        [
            {"text": "Ping Bot", "callback": "ping"}
        ]
    ]
}


async def _import_commands(msg: Message, uid: int, data, lang: str = "en"):
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        await msg.reply(
            f"<b>{G.WARN}  {_t('Invalid Format', lang)}</b>\n{G.LINE}\n\n"
            "Expected a JSON object or array.",
            parse_mode=ParseMode.HTML
        )
        return

    ok = fail = 0
    errors = []
    for item in data:
        if not isinstance(item, dict):
            fail += 1
            errors.append("Non-object entry skipped.")
            continue
        valid, err = validate_command_payload(item)
        if not valid:
            fail += 1
            errors.append(f"/{item.get('command','?')}: {err}")
            continue
        cmd  = item["command"].lstrip("/").lower()
        payload = {
            "text":       item.get("text", ""),
            "parse_mode": item.get("parse_mode", "html"),
            "photo":      item.get("photo"),
            "video":      item.get("video"),
            "buttons":    item.get("buttons", []),
            "enabled":    item.get("enabled", True),
        }
        await store.set_command(uid, cmd, payload)
        ok += 1

    await logger.emit(uid, "Commands Imported", f"ok={ok} fail={fail}", level="info")

    lines = [
        f"<b>{G.OK}  {_t('Import Complete', lang)}</b>\n{G.LINE}\n\n"
        f"{G.CHECK}  {_t('Imported', lang)}: <b>{ok}</b>\n"
        f"{G.CROSS}  {_t('Failed', lang)}: <b>{fail}</b>"
    ]
    if errors:
        lines.append(f"\n{G.THIN}\n<b>{_t('Errors', lang)}:</b>")
        for e in errors[:5]:
            lines.append(f"• {e}")
        if len(errors) > 5:
            lines.append(f"<i>...and {len(errors)-5} more</i>")

    await msg.reply(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[
            IBtn(f"{_t('Manage Commands', lang)}", callback_data="cmd_list")
        ]])
    )


def register(app: Client):

    @app.on_message(filters.command("lang") & filters.private)
    async def cmd_lang(client: Client, msg: Message):
        uid  = msg.from_user.id
        try:
            lang = await _lang(uid)
        except Exception:
            lang = "en"
        rows = []
        for label, cb in make_lang_buttons():
            rows.append([IBtn(label, callback_data=cb)])
        rows.append([IBtn(f"{G.BACK}  {_t('Back', lang)}", callback_data="home")])
        await msg.reply(
            f"<b>{G.GEAR}  {_t('Select your language:', lang)}</b>\n{G.LINE}\n\n"
            f"<i>{_t('Current language', lang)}: <b>{LANGUAGES.get(lang, lang)}</b></i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(rows),
        )

    @app.on_message(filters.command("add_cmd") & filters.private)
    @auth_required
    async def cmd_add(client: Client, msg: Message):
        uid  = msg.from_user.id
        lang = await _lang(uid)
        args = msg.text.split(None, 2)

        if msg.reply_to_message and msg.reply_to_message.document:
            doc = msg.reply_to_message.document
            if not (doc.file_name or "").endswith(".json"):
                await msg.reply(
                    f"<b>{G.WARN}  {_t('Wrong File Type', lang)}</b>\n{G.LINE}\n\n"
                    "Reply to a <code>.json</code> file.",
                    parse_mode=ParseMode.HTML
                )
                return
            try:
                path = await client.download_media(doc, in_memory=True)
                raw  = bytes(path.getbuffer()).decode("utf-8")
            except Exception as e:
                await msg.reply(
                    f"<b>{G.WARN}  {_t('Download Failed', lang)}</b>\n<code>{escape(str(e))}</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                await msg.reply(
                    f"<b>{G.WARN}  {_t('Invalid JSON', lang)}</b>\n{G.LINE}\n\n<code>{escape(str(e))}</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            await _import_commands(msg, uid, data, lang)
            return

        if msg.reply_to_message and msg.reply_to_message.text:
            raw = msg.reply_to_message.text.strip()
            if raw.startswith("{") or raw.startswith("["):
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError as e:
                    await msg.reply(
                        f"<b>{G.WARN}  {_t('Invalid JSON', lang)}</b>\n{G.LINE}\n\n<code>{escape(str(e))}</code>",
                        parse_mode=ParseMode.HTML
                    )
                    return
                await _import_commands(msg, uid, data, lang)
                return

        if len(args) >= 3:
            cmd_name = args[1].lstrip("/").lower()
            text_val = args[2]
            fake_payload = {"command": cmd_name, "text": text_val}
            valid, err = validate_command_payload(fake_payload)
            if not valid:
                await msg.reply(
                    f"<b>{G.WARN}  {_t('Validation Failed', lang)}</b>\n{G.LINE}\n\n{err}",
                    parse_mode=ParseMode.HTML
                )
                return
            payload = {
                "text": text_val, "parse_mode": "html",
                "photo": None, "video": None, "buttons": [], "enabled": True,
            }
            await store.set_command(uid, cmd_name, payload)
            await logger.emit(uid, "Command Added", f"/{cmd_name}", level="info")
            await msg.reply(
                f"<b>{G.OK}  {_t('Command Added', lang)}</b>\n{G.LINE}\n\n"
                f"{G.CMD}  <code>/{escape(cmd_name)}</code>\n\n"
                f"<i>{_t('Try it:', lang)} <code>/{escape(cmd_name)}</code></i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    IBtn(f"{_t('Manage Commands', lang)}", callback_data="cmd_list")
                ]])
            )
            return

        await msg.reply(
            f"<b>{G.ADD}  {_t('Add Custom Command', lang)}</b>\n{G.LINE}\n\n"
            f"<b>Option 1 — Simple text:</b>\n"
            f"<code>/add_cmd hello &lt;b&gt;Hello World!&lt;/b&gt;</code>\n\n"
            f"<b>Option 2 — Full JSON (reply to JSON message):</b>\n"
            f"<code>/add_cmd</code>  <i>(as reply to your JSON)</i>\n\n"
            f"<b>Option 3 — Bulk import (reply to .json file):</b>\n"
            f"<code>/add_cmd</code>  <i>(as reply to the file)</i>\n\n"
            f"{G.THIN}\n"
            f"<b>JSON fields:</b>\n"
            f"<code>command</code> — name (a-z, 0-9, underscore, max 32)\n"
            f"<code>text</code>    — HTML message body\n"
            f"<code>photo</code>   — file_id or URL (optional)\n"
            f"<code>video</code>   — file_id or URL (optional)\n"
            f"<code>buttons</code> — array of button rows (optional)\n"
            f"<code>enabled</code> — true / false\n\n"
            f"<i>Use /cmd_schema for the complete JSON example.</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                IBtn(f"[ ] {_t('View Schema', lang)}", callback_data="cmd_schema")
            ]])
        )

    @app.on_message(filters.command("del_cmd") & filters.private)
    @auth_required
    async def cmd_del(client: Client, msg: Message):
        uid  = msg.from_user.id
        lang = await _lang(uid)
        args = msg.text.split()
        if len(args) < 2:
            await msg.reply(
                f"<b>{_t('Usage', lang)}</b>: <code>/del_cmd command_name</code>",
                parse_mode=ParseMode.HTML
            )
            return
        cmd_name = args[1].lstrip("/").lower()
        deleted  = await store.delete_command(cmd_name)
        if deleted:
            await logger.emit(uid, "Command Deleted", f"/{cmd_name}", level="info")
            await msg.reply(
                f"<b>{G.OK}  {_t('Command Deleted', lang)}</b>\n{G.LINE}\n\n"
                f"<code>/{escape(cmd_name)}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            await msg.reply(
                f"<b>{G.WARN}  {_t('Not Found', lang)}</b>\n{G.LINE}\n\n"
                f"<code>/{escape(cmd_name)}</code>\n\n"
                f"<i>Use /cmds to see all commands.</i>",
                parse_mode=ParseMode.HTML
            )

    @app.on_message(filters.command("cmds") & filters.private)
    @auth_required
    async def cmd_list_msg(client: Client, msg: Message):
        import environ
        uid  = msg.from_user.id
        lang = await _lang(uid)
        cmds = await store.get_all_commands(uid if uid != environ.OWNER_ID else None)
        if not cmds:
            await msg.reply(
                f"<b>{_t('No Custom Commands', lang)}</b>\n{G.LINE}\n\n"
                f"<i>{_t('Use /add_cmd to create one.', lang)}</i>",
                parse_mode=ParseMode.HTML
            )
            return
        lines = [f"<b>{G.CMD}  {_t('Custom Commands', lang)}</b>  ({len(cmds)})\n{G.LINE}\n"]
        for c in cmds:
            state  = G.CHECK if c.get("enabled") else G.CROSS
            uses   = c.get("use_count", 0)
            lines.append(f"{state}  <code>/{escape(c['command'])}</code>  <i>({uses}x)</i>")
        await msg.reply(
            "\n".join(lines),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                IBtn(f"{_t('Manage in Panel', lang)}", callback_data="cmd_list")
            ]])
        )

    @app.on_message(filters.command("cmd_schema") & filters.private)
    @auth_required
    async def cmd_schema_handler(client: Client, msg: Message):
        uid  = msg.from_user.id
        lang = await _lang(uid)
        schema_text = json.dumps(CMD_SCHEMA_EXAMPLE, indent=2)
        await msg.reply(
            f"<b>{G.CMD}  {_t('JSON Command Schema', lang)}</b>\n{G.LINE}\n\n"
            f"<pre>{escape(schema_text)}</pre>\n\n"
            f"<b>{_t('Bulk import:', lang)}</b>\n"
            f"Wrap multiple objects in an array:\n"
            f"<code>[{{...}}, {{...}}]</code>\n\n"
            f"<b>{_t('Button format:', lang)}</b>\n"
            f'<code>[[{{"text":"Label","url":"https://..."}}]]</code>',
            parse_mode=ParseMode.HTML
        )

    def _is_custom_cmd_filter(_, __, msg: Message) -> bool:
        if not msg.text:
            return False
        raw = msg.text.strip()
        if not raw.startswith("/"):
            return False
        cmd_part = raw.split()[0].lstrip("/")
        if "@" in cmd_part:
            cmd_part = cmd_part.split("@")[0]
        cmd_name = cmd_part.lower()
        return bool(cmd_name) and cmd_name not in BUILTINS

    custom_cmd_filter = filters.create(_is_custom_cmd_filter)

    @app.on_message(custom_cmd_filter & filters.private, group=1)
    async def dynamic_dispatch(client: Client, msg: Message):
        await dispatch_custom_command(client, msg)
