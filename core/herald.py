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

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from core.guardian import auth_required, owner_only
from core import logger
from vault import store
from wire import glyph as G
from wire import panel
from wire.i18n import t as _t, LANGUAGES
import environ


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


def register(app: Client):

    @app.on_message(filters.command(["start", "menu"]) & filters.private)
    @auth_required
    async def cmd_menu(client: Client, msg: Message):
        uid      = msg.from_user.id
        lang     = await _lang(uid)
        pipes    = await store.get_all_pipelines(uid)
        is_owner = uid == environ.OWNER_ID
        name     = msg.from_user.first_name or ""
        text = (
            f"<b>{G.STAR} {_t('TeamDev Auto-Forward', lang)}</b>\n"
            f"{G.LINE}\n\n"
            f"{_t('Welcome back', lang)}, <b>{name}</b>\n\n"
            f"{G.BULLET}  {_t('Pipelines', lang)}: <b>{len(pipes)}</b>\n"
            f"{G.BULLET}  {_t('Engine', lang)}: <b>{_t('Running', lang)}</b>\n\n"
            f"{G.THIN}\n"
            f"  {_t('Select a pipeline or create one below.', lang)}\n"
            f"{G.THIN}"
        )
        await msg.reply(text, parse_mode=ParseMode.HTML,
                        reply_markup=panel.home(pipes, is_owner))
        await logger.emit(uid, "Opened Menu", level="info")

    @app.on_message(filters.command("channels") & filters.private)
    async def cmd_channels(client: Client, msg: Message):
        uid = msg.from_user.id
        lang = await _lang(uid)
        db_channels = await store.get_force_join_channels()
        all_channels = list(dict.fromkeys(environ.FORCE_JOIN + db_channels))
        if not all_channels:
            await msg.reply(
                f"<b>{G.CHANNELS}  {_t('Channels', lang)}</b>\n{G.LINE}\n\n"
                f"<i>{_t('No channels configured.', lang)}</i>",
                parse_mode=ParseMode.HTML
            )
            return
        lines = [f"<b>{G.CHANNELS}  {_t('Join Our Channels', lang)}</b>\n{G.LINE}\n"]
        for ch in all_channels:
            lines.append(f"{G.ARR2}  <code>{ch}</code>")
        lines.append(f"\n<i>{_t('Join all channels above to use this bot.', lang)}</i>")
        await msg.reply(
            "\n".join(lines),
            parse_mode=ParseMode.HTML,
            reply_markup=panel.force_join_channels_kb(all_channels, lang)
        )

    @app.on_message(filters.command("help") & filters.private)
    @auth_required
    async def cmd_help(client: Client, msg: Message):
        uid  = msg.from_user.id
        lang = await _lang(uid)
        text = (
            f"<b>{G.STAR} {_t('TeamDev — Help', lang)}</b>\n{G.LINE}\n\n"

            f"<b>{_t('Concept', lang)}</b>\n"
            f"{_t('Pipeline = 1 source channel → N targets.', lang)}\n"
            f"{_t('Create unlimited pipelines, each independent.', lang)}\n\n"

            f"<b>Commands</b>\n"
            f"<code>/menu</code>       — {_t('Dashboard', lang)}\n"
            f"<code>/pipes</code>      — {_t('List pipelines', lang)}\n"
            f"<code>/new</code>        — {_t('Create pipeline', lang)}\n"
            f"<code>/stats</code>      — {_t('Statistics', lang)}\n"
            f"<code>/ping</code>       — {_t('Check bot latency', lang)}\n"
            f"<code>/health</code>     — {_t('Bot health check', lang)}\n"
            f"<code>/uptime</code>     — {_t('Bot uptime & system stats', lang)}\n"
            f"<code>/backup</code>     — {_t('Export full backup ZIP (owner)', lang)}\n"
            f"<code>/import</code>     — {_t('Import pipeline from JSON', lang)}\n"
            f"<code>/cmds</code>       — {_t('List custom commands', lang)}\n"
            f"<code>/add_cmd</code>    — {_t('Add custom command', lang)}\n"
            f"<code>/del_cmd</code>    — {_t('Delete custom command', lang)}\n"
            f"<code>/cmd_schema</code> — {_t('JSON format guide', lang)}\n"
            f"<code>/lang</code>       — {_t('Change language', lang)}\n\n"

            f"<b>{_t('Pipeline Features', lang)}</b>\n"
            f"{G.BULLET} {_t('1 source, unlimited targets', lang)}\n"
            f"{G.BULLET} {_t('Hide forward tag', lang)}\n"
            f"{G.BULLET} {_t('Media type filter', lang)}\n"
            f"{G.BULLET} {_t('Keyword whitelist + blacklist', lang)}\n"
            f"{G.BULLET} {_t('Caption prepend / append / replace', lang)}\n"
            f"{G.BULLET} {_t('Schedule by hour + timezone', lang)}\n"
            f"{G.BULLET} {_t('Duplicate message filter (7d window)', lang)}\n"
            f"{G.BULLET} {_t('Forward limit with auto-pause', lang)}\n"
            f"{G.BULLET} {_t('Per-pipeline rate limit (msgs/min)', lang)}\n"
            f"{G.BULLET} {_t('Export config as JSON', lang)}\n"
            f"{G.BULLET} {_t('Clone pipeline (copy all settings)', lang)}\n\n"

            f"<b>{_t('Transform Features', lang)}</b>\n"
            f"{G.BULLET} {_t('Regex filter — match by pattern', lang)}\n"
            f"{G.BULLET} {_t('Invert regex — exclude matching', lang)}\n"
            f"{G.BULLET} {_t('Auto-pin forwarded messages', lang)}\n"
            f"{G.BULLET} {_t('Remove inline buttons on forward', lang)}\n"
            f"{G.BULLET} {_t('Strip @mentions from text', lang)}\n"
            f"{G.BULLET} {_t('Strip #hashtags from text', lang)}\n"
            f"{G.BULLET} {_t('Find & Replace — text substitution rules', lang)}\n\n"

            f"<b>{_t('New in v1.3.0', lang)}</b>\n"
            f"{G.BULLET} {_t('Dry Run mode — simulate without forwarding', lang)}\n"
            f"{G.BULLET} {_t('/uptime — bot uptime + system stats', lang)}\n"
            f"{G.BULLET} {_t('/backup — export full ZIP backup (owner)', lang)}\n"
            f"{G.BULLET} {_t('/import — restore pipeline from JSON', lang)}\n\n"

            f"<b>{_t('Anti-Flood', lang)}</b>\n"
            f"{G.BULLET} {_t('Async queue — no burst forwarding', lang)}\n"
            f"{G.BULLET} {_t('Token bucket rate limiter', lang)}\n"
            f"{G.BULLET} {_t('Global FloodWait gate', lang)}\n"
            f"{G.BULLET} {_t('Auto-retry with backoff', lang)}\n\n"

            f"<b>{_t('Custom Commands', lang)}</b>\n"
            f"{G.BULLET} <code>/add_cmd hello Hello World!</code>  — quick add\n"
            f"{G.BULLET} Reply to JSON + <code>/add_cmd</code>  — full JSON import\n"
            f"{G.BULLET} Reply to .json file + <code>/add_cmd</code>  — bulk import\n"
            f"{G.BULLET} Use <code>/cmd_schema</code> for the complete JSON format\n\n"

            f"<b>{_t('Language', lang)}</b>\n"
            f"{G.BULLET} Use <code>/lang</code> to switch: "
            + ", ".join(LANGUAGES.values()) + "\n"
        )
        await msg.reply(text, parse_mode=ParseMode.HTML, reply_markup=panel.back_home())
        
    @app.on_message(filters.command("pipes") & filters.private)
    @auth_required
    async def cmd_pipes(client: Client, msg: Message):
        uid   = msg.from_user.id
        lang  = await _lang(uid)
        pipes = await store.get_all_pipelines(uid)
        if not pipes:
            await msg.reply(
                f"<b>{_t('No pipelines yet.', lang)}</b>\n"
                f"<i>{_t('Use /new to create one.', lang)}</i>",
                parse_mode=ParseMode.HTML, reply_markup=panel.back_home()
            )
            return
        lines = [f"<b>{G.STAR} {_t('Your Pipelines', lang)}</b>\n{G.LINE}\n"]
        for p in pipes:
            status = G.PLAY if p["active"] else G.STOP
            src    = p.get("source") or _t("not set", lang)
            tgts   = len(p.get("targets", []))
            fwd    = p.get("stats", {}).get("forwarded", 0)
            lines.append(
                f"{status}  <b>[{p['pipe_id']}] {G.g(p['name'])}</b>\n"
                f"   {G.SRC} <code>{src}</code>\n"
                f"   {G.TGT} {tgts} {_t('targets', lang)}  "
                f"{G.CHART} {fwd} {_t('fwd', lang)}\n"
            )
        await msg.reply("\n".join(lines), parse_mode=ParseMode.HTML,
                        reply_markup=panel.home(pipes, uid == environ.OWNER_ID))

    @app.on_message(filters.command("new") & filters.private)
    @auth_required
    async def cmd_new(client: Client, msg: Message):
        uid  = msg.from_user.id
        lang = await _lang(uid)
        store.set_session(uid, "await_pipe_name")
        await msg.reply(
            f"<b>{G.ADD}  {_t('New Pipeline', lang)}</b>\n{G.LINE}\n\n"
            f"{_t('Send a name for this pipeline.', lang)}\n"
            f"<i>{_t('Example', lang)}: <code>News Feed</code></i>",
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.command("stats") & filters.private)
    @auth_required
    async def cmd_stats(client: Client, msg: Message):
        uid   = msg.from_user.id
        lang  = await _lang(uid)
        pipes = await store.get_all_pipelines(uid)
        fwd   = sum(p.get("stats", {}).get("forwarded", 0) for p in pipes)
        skip  = sum(p.get("stats", {}).get("skipped",   0) for p in pipes)
        dedup = sum(p.get("stats", {}).get("deduped",   0) for p in pipes)
        err   = sum(p.get("stats", {}).get("errors",    0) for p in pipes)
        actv  = sum(1 for p in pipes if p["active"])
        text  = (
            f"<b>{G.CHART}  {_t('Statistics', lang)}</b>\n{G.LINE}\n\n"
            f"{G.BULLET}  {_t('Pipelines', lang)}: <code>{len(pipes)}</code>  "
            f"(<code>{actv}</code> {_t('active', lang)})\n"
            f"{G.BULLET}  {_t('Forwarded', lang)}: <code>{fwd}</code>\n"
            f"{G.BULLET}  {_t('Skipped', lang)}: <code>{skip}</code>\n"
            f"{G.BULLET}  {_t('Deduped', lang)}: <code>{dedup}</code>\n"
            f"{G.BULLET}  {_t('Errors', lang)}: <code>{err}</code>\n"
        )
        await msg.reply(text, parse_mode=ParseMode.HTML, reply_markup=panel.back_home())

    @app.on_message(filters.command("ping") & filters.private)
    async def cmd_ping(client: Client, msg: Message):
        import time
        uid  = msg.from_user.id
        lang = await _lang(uid)
        t = time.monotonic()
        sent = await msg.reply(f"<b>{G.DOT}</b>", parse_mode=ParseMode.HTML)
        ms = int((time.monotonic() - t) * 1000)
        await sent.edit_text(
            f"<b>{G.CHECK}  {_t('Pong!', lang)}</b>  <code>{ms}ms</code>",
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.command("health") & filters.private)
    @auth_required
    async def cmd_health(client: Client, msg: Message):
        from relay.throttle import _queues
        from vault import store as _store
        import environ as env
        uid  = msg.from_user.id
        lang = await _lang(uid)

        try:
            await _store._db.command("ping")
            db_status = f"{G.CHECK} {_t('Connected', lang)}"
        except Exception:
            db_status = f"{G.CROSS} {_t('Error', lang)}"

        if env.LOG_CHANNEL:
            from core.logger import _log_channel_ok
            lc_status = (
                f"{G.CHECK} {env.LOG_CHANNEL}" if _log_channel_ok
                else f"{G.CROSS} {_t('Error', lang)} ({env.LOG_CHANNEL})"
            )
        else:
            lc_status = f"{G.WARN} {_t('Not set', lang)}"

        total_q  = sum(q.qsize() for q in _queues.values())
        pipes_all = await _store.get_all_pipelines_global()
        active_c  = sum(1 for p in pipes_all if p.get("active"))

        text = (
            f"<b>{G.CHART}  {_t('Bot Health', lang)}</b>\n{G.LINE}\n\n"
            f"{G.BULLET}  {_t('MongoDB', lang)}: {db_status}\n"
            f"{G.BULLET}  {_t('Log Channel', lang)}: {lc_status}\n"
            f"{G.BULLET}  {_t('Active Pipelines', lang)}: <code>{active_c}</code>\n"
            f"{G.BULLET}  {_t('Queue Depth', lang)}: <code>{total_q}</code> {_t('msgs pending', lang)}\n"
            f"{G.BULLET}  {_t('Bot Version', lang)}: <code>v{env.VERSION}</code>\n"
        )
        await msg.reply(text, parse_mode=ParseMode.HTML, reply_markup=panel.back_home())

    @app.on_message(filters.command("admins") & filters.private)
    @owner_only
    async def cmd_admins(client: Client, msg: Message):
        uid    = msg.from_user.id
        lang   = await _lang(uid)
        admins = await store.get_all_admins()
        if not admins:
            await msg.reply(
                f"<b>{_t('No admins added yet.', lang)}</b>",
                parse_mode=ParseMode.HTML, reply_markup=panel.back_owner()
            )
            return
        lines = [f"<b>{G.ADMIN}  {_t('Admins', lang)}</b>\n{G.LINE}\n"]
        for a in admins:
            ban   = f"  {G.BAN}" if a.get("is_banned") else ""
            uname = f"@{a['username']}" if a.get("username") else str(a["user_id"])
            perms = ", ".join(a.get("perms", [])) or _t("none", lang)
            lines.append(
                f"{G.ADMIN}  {uname}{ban}\n"
                f"   <i>{_t('Perms', lang)}: <code>{perms}</code></i>\n"
            )
        await msg.reply("\n".join(lines), parse_mode=ParseMode.HTML,
                        reply_markup=panel.back_owner())

    @app.on_message(filters.command("uptime") & filters.private)
    @auth_required
    async def cmd_uptime(client: Client, msg: Message):
        import time, psutil, os as _os
        uid  = msg.from_user.id
        lang = await _lang(uid)
        try:
            proc       = psutil.Process(_os.getpid())
            start_time = proc.create_time()
            elapsed    = time.time() - start_time
            days       = int(elapsed // 86400)
            hours      = int((elapsed % 86400) // 3600)
            minutes    = int((elapsed % 3600) // 60)
            seconds    = int(elapsed % 60)
            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

            mem        = proc.memory_info()
            mem_mb     = mem.rss / 1024 / 1024
            cpu_pct    = proc.cpu_percent(interval=0.1)

            vm         = psutil.virtual_memory()
            sys_mem    = f"{vm.used / 1024**2:.0f}MB / {vm.total / 1024**2:.0f}MB ({vm.percent}%)"
            disk       = psutil.disk_usage("/")
            sys_disk   = f"{disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB ({disk.percent}%)"
        except Exception as e:
            uptime_str = f"N/A ({e})"
            mem_mb = cpu_pct = 0
            sys_mem = sys_disk = "N/A"

        text = (
            f"<b>{G.CHART}  {_t('Uptime & System', lang)}</b>\n{G.LINE}\n\n"
            f"{G.BULLET}  {_t('Uptime', lang)}: <code>{uptime_str}</code>\n"
            f"{G.BULLET}  {_t('Bot RAM', lang)}: <code>{mem_mb:.1f} MB</code>\n"
            f"{G.BULLET}  {_t('Bot CPU', lang)}: <code>{cpu_pct:.1f}%</code>\n"
            f"{G.THIN}\n"
            f"{G.BULLET}  {_t('System RAM', lang)}: <code>{sys_mem}</code>\n"
            f"{G.BULLET}  {_t('Disk', lang)}: <code>{sys_disk}</code>\n"
            f"{G.BULLET}  {_t('Bot Version', lang)}: <code>v{environ.VERSION}</code>\n"
        )
        await msg.reply(text, parse_mode=ParseMode.HTML, reply_markup=panel.back_home())

    @app.on_message(filters.command("backup") & filters.private)
    @owner_only
    async def cmd_backup(client: Client, msg: Message):
        import zipfile, json as _json, io, datetime as _dt
        uid  = msg.from_user.id
        lang = await _lang(uid)

        wait = await msg.reply(
            f"<b>{G.EXPRT}  {_t('Preparing backup...', lang)}</b>",
            parse_mode=ParseMode.HTML
        )

        pipes = await store.get_all_pipelines_global()
        admins = await store.get_all_admins()
        cmds   = await store.get_all_commands(owner_id=None)

        timestamp = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fname = f"TeamDev_backup_{timestamp}.zip"
        fpath = f"/tmp/{fname}"

        def _serial(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            return str(obj)

        with zipfile.ZipFile(fpath, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("pipelines.json",
                        _json.dumps([{k:v for k,v in p.items() if k != "_id"} for p in pipes],
                                    indent=2, default=_serial))
            zf.writestr("admins.json",
                        _json.dumps([{k:v for k,v in a.items() if k != "_id"} for a in admins],
                                    indent=2, default=_serial))
            zf.writestr("commands.json",
                        _json.dumps([{k:v for k,v in c.items() if k != "_id"} for c in cmds],
                                    indent=2, default=_serial))
            zf.writestr("meta.json",
                        _json.dumps({
                            "exported_at": timestamp,
                            "version": environ.VERSION,
                            "pipelines": len(pipes),
                            "admins": len(admins),
                            "commands": len(cmds),
                        }, indent=2))

        import os as _os
        await wait.delete()
        await msg.reply_document(
            document=fpath,
            caption=(
                f"<b>{G.EXPRT}  {_t('Full Backup', lang)}</b>\n{G.LINE}\n\n"
                f"{G.BULLET}  {_t('Pipelines', lang)}: <code>{len(pipes)}</code>\n"
                f"{G.BULLET}  {_t('Admins', lang)}: <code>{len(admins)}</code>\n"
                f"{G.BULLET}  {_t('Commands', lang)}: <code>{len(cmds)}</code>\n"
                f"\n<i>{_t('Keep this file safe.', lang)}</i>"
            ),
            parse_mode=ParseMode.HTML
        )
        _os.remove(fpath)
        await logger.emit(uid, "Full Backup Exported", f"pipes={len(pipes)}", level="owner")

    @app.on_message(filters.command("import") & filters.private)
    @owner_only
    async def cmd_import(client: Client, msg: Message):
        uid  = msg.from_user.id
        lang = await _lang(uid)
        await msg.reply(
            f"<b>{G.IMPRT}  {_t('Import Pipeline', lang)}</b>\n{G.LINE}\n\n"
            f"{_t('Reply to a pipeline JSON file (exported from this bot) with /import', lang)}\n\n"
            f"<i>{_t('This will create a new pipeline copying all settings. It starts inactive.', lang)}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_home()
        )

    @app.on_message(
        filters.private & filters.document &
        filters.create(lambda _, __, m: (
            m.document and m.document.file_name.endswith(".json") and
            m.caption and m.caption.strip().startswith("/import")
        ))
    )
    @owner_only
    async def cmd_import_doc(client: Client, msg: Message):
        import json as _json, io
        uid  = msg.from_user.id
        lang = await _lang(uid)
        try:
            file_bytes = await client.download_media(msg.document.file_id, in_memory=True)
            data = _json.loads(bytes(file_bytes.getbuffer()))
        except Exception as e:
            await msg.reply(
                f"<b>{G.WARN}  {_t('Parse Error', lang)}</b>\n<code>{e}</code>",
                parse_mode=ParseMode.HTML
            )
            return

        if isinstance(data, list):
            pipelines_to_import = data
        elif isinstance(data, dict) and "pipe_id" in data:
            pipelines_to_import = [data]
        else:
            await msg.reply(
                f"<b>{G.WARN}  {_t('Invalid format. Expected a pipeline JSON export.', lang)}</b>",
                parse_mode=ParseMode.HTML
            )
            return

        results = []
        for pipe_data in pipelines_to_import:
            try:
                name = pipe_data.get("name", "Imported Pipeline")
                new_pipe = await store.create_pipeline(uid, name)
                pid = new_pipe["pipe_id"]
                safe_keys = [
                    "source", "targets", "hide_tag", "media_filter", "delay",
                    "keywords", "blacklist", "caption_mode", "caption_text",
                    "schedule", "dedup", "fwd_limit", "rate_limit", "watermark",
                    "min_length", "auto_delete", "transform", "inline_buttons",
                    "find_replace", "strip_opts",
                ]
                updates = {k: pipe_data[k] for k in safe_keys if k in pipe_data}
                updates["active"] = False
                await store.update_pipeline(uid, pid, **updates)
                results.append(f"{G.CHECK} <b>{name}</b> → <code>#{pid}</code>")
            except Exception as e:
                results.append(f"{G.CROSS} Failed: <code>{e}</code>")

        await msg.reply(
            f"<b>{G.IMPRT}  {_t('Import Complete', lang)}</b>\n{G.LINE}\n\n"
            + "\n".join(results) +
            f"\n\n<i>{_t('All imported pipelines start inactive — review and activate.', lang)}</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.back_home()
        )
        await logger.emit(uid, "Pipeline Imported", f"count={len(results)}", level="pipe")
