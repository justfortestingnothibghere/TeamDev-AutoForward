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
import asyncio
import os
import sys
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton as IBtn
from core.guardian import auth_required, owner_only
from core import logger
from vault import store
from vault.store import Perm, ALL_PERMS
from wire import glyph as G
from wire import panel
from wire.i18n import t as _t, LANGUAGES, make_lang_buttons, set_user_lang_cache
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

async def _render_home(cq: CallbackQuery):
    uid    = cq.from_user.id
    pipes  = await store.get_all_pipelines(uid)
    is_own = uid == environ.OWNER_ID
    text   = (
        f"<b>{G.STAR}  {G.g('Nexus Auto-Forward')}</b>\n{G.LINE}\n\n"
        f"{G.BULLET}  {G.g('Pipelines')}: <b>{len(pipes)}</b>\n"
        f"{G.BULLET}  {G.g('Engine running.')}\n\n"
        f"{G.THIN}\n  {G.g('Select or create a pipeline.')}\n{G.THIN}"
    )
    await cq.message.edit_text(text, parse_mode=ParseMode.HTML,
                               reply_markup=panel.home(pipes, is_own))


async def _render_pipe(cq: CallbackQuery, pid: int):
    uid  = cq.from_user.id
    pipe = await store.get_pipeline(uid, pid)
    if not pipe:
        await cq.answer(G.g("Pipeline not found."), show_alert=True)
        return

    src     = pipe.get("source") or f"<i>{G.g('not set')}</i>"
    tgts    = pipe.get("targets", [])
    tgt_str = ", ".join(f"<code>{t}</code>" for t in tgts) if tgts else f"<i>{G.g('none')}</i>"
    status  = f"{G.PLAY}  {G.g('Active')}" if pipe["active"] else f"{G.STOP}  {G.g('Inactive')}"
    stats   = pipe.get("stats", {})
    sched   = pipe.get("schedule", {})
    sch_str = (
        f"{sched.get('start_hour',0):02d}:00 — {sched.get('end_hour',23):02d}:00  [{sched.get('tz','UTC')}]"
        if sched.get("enabled") else G.g("off")
    )
    lim     = pipe.get("fwd_limit", 0)
    rpm     = pipe.get("rate_limit", environ.RATE_LIMIT)

    text = (
        f"<b>{G.PIPE}  {G.g(pipe['name'])}</b>  <code>#{pid}</code>\n{G.LINE}\n\n"
        f"{G.BULLET}  {G.g('Status')}: {status}\n"
        f"{G.BULLET}  {G.g('Source')}: <code>{src}</code>\n"
        f"{G.BULLET}  {G.g('Targets')}: {tgt_str}\n"
        f"{G.THIN}\n"
        f"<code>media={pipe.get('media_filter','all').upper()}  "
        f"delay={pipe.get('delay',1.5)}s  "
        f"rate={rpm}/min  "
        f"hide={'on' if pipe.get('hide_tag') else 'off'}  "
        f"dedup={'on' if pipe.get('dedup') else 'off'}</code>\n"
        f"<code>schedule={sch_str}</code>\n"
        f"<code>limit={lim if lim else 'off'}</code>\n"
        f"{G.THIN}\n"
        f"{G.g('fwd')} <code>{stats.get('forwarded',0)}</code>  "
        f"{G.g('skip')} <code>{stats.get('skipped',0)}</code>  "
        f"{G.g('dedup')} <code>{stats.get('deduped',0)}</code>  "
        f"{G.g('err')} <code>{stats.get('errors',0)}</code>\n"
        f"{G.LINE}"
    )
    await cq.message.edit_text(text, parse_mode=ParseMode.HTML,
                               reply_markup=panel.pipe_detail(pipe))


def register(app: Client):

    @app.on_callback_query(filters.regex(r"^set_lang:(\w+)$"))
    async def cb_set_lang(c, cq: CallbackQuery):
        uid      = cq.from_user.id
        new_lang = cq.matches[0].group(1)
        if new_lang not in LANGUAGES:
            await cq.answer("Unknown language.", show_alert=True)
            return
        try:
            await store.set_user_lang(uid, new_lang)
        except Exception:
            pass
        set_user_lang_cache(uid, new_lang)
        await cq.answer(_t("Language changed!", new_lang), show_alert=False)
        rows = []
        for label, cb in make_lang_buttons():
            rows.append([IBtn(label, callback_data=cb)])
        rows.append([IBtn(f"{G.BACK}  {_t('Back', new_lang)}", callback_data="home")])
        try:
            await cq.message.edit_text(
                f"<b>{G.GEAR}  {_t('Select your language:', new_lang)}</b>\n{G.LINE}\n\n"
                f"<i>{_t('Current language', new_lang)}: <b>{LANGUAGES.get(new_lang, new_lang)}</b></i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(rows),
            )
        except Exception:
            pass

    @app.on_callback_query(filters.regex("^noop$"))
    async def cb_noop(c, cq: CallbackQuery):
        await cq.answer()

    @app.on_callback_query(filters.regex("^home$"))
    @auth_required
    async def cb_home(c, cq: CallbackQuery):
        await _render_home(cq); await cq.answer()

    @app.on_callback_query(filters.regex("^help$"))
    @auth_required
    async def cb_help(c, cq: CallbackQuery):
        uid  = cq.from_user.id
        lang = await _lang(uid)
        text = (
            f"<b>{G.STAR}  {_t('Nexus — Help', lang)}</b>\n{G.LINE}\n\n"

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
            f"{G.BULLET} {_t('Remove inline buttons on forward', lang)}\n\n"

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
        await cq.message.edit_text(text, parse_mode=ParseMode.HTML,
                                   reply_markup=panel.back_home())
        await cq.answer()

    @app.on_callback_query(filters.regex("^global_stats$"))
    @auth_required
    async def cb_global_stats(c, cq: CallbackQuery):
        uid = cq.from_user.id
        if uid == environ.OWNER_ID:
            s = await store.global_stats()
            text = (
                f"<b>{G.CHART}  {G.g('Global Statistics')}</b>\n{G.LINE}\n\n"
                f"{G.BULLET}  {G.g('Pipelines')}: <code>{s['total_pipes']}</code> "
                f"(<code>{s['active_pipes']}</code> {G.g('active')})\n"
                f"{G.BULLET}  {G.g('Users')}: <code>{s['total_users']}</code>\n"
                f"{G.BULLET}  {G.g('Admins')}: <code>{s['total_admins']}</code>\n"
                f"{G.BULLET}  {G.g('Commands')}: <code>{s['total_cmds']}</code>\n"
                f"{G.THIN}\n"
                f"{G.BULLET}  {G.g('Forwarded')}: <code>{s['forwarded']}</code>\n"
                f"{G.BULLET}  {G.g('Skipped')}: <code>{s['skipped']}</code>\n"
                f"{G.BULLET}  {G.g('Deduped')}: <code>{s['deduped']}</code>\n"
                f"{G.BULLET}  {G.g('Errors')}: <code>{s['errors']}</code>\n"
            )
            kb = panel.back_owner()
        else:
            pipes = await store.get_all_pipelines(uid)
            text  = (
                f"<b>{G.CHART}  {G.g('Your Stats')}</b>\n{G.LINE}\n\n"
                f"{G.BULLET}  {G.g('Pipelines')}: <code>{len(pipes)}</code>\n"
                f"{G.BULLET}  {G.g('Forwarded')}: <code>"
                f"{sum(p.get('stats',{}).get('forwarded',0) for p in pipes)}</code>\n"
            )
            kb = panel.back_home()
        await cq.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
        await cq.answer()

    @app.on_callback_query(filters.regex("^queue_status$"))
    @owner_only
    async def cb_queue_status(c, cq: CallbackQuery):
        from relay.throttle import _queues
        lines = [f"<b>{G.QUEUE}  {G.g('Queue Status')}</b>\n{G.LINE}\n"]
        if not _queues:
            lines.append(f"<i>{G.g('No active queues.')}</i>")
        else:
            for pid, q in _queues.items():
                lines.append(f"{G.BULLET}  pipe <code>{pid}</code>: "
                             f"<code>{q.qsize()}</code> {G.g('queued')}")
        await cq.message.edit_text("\n".join(lines), parse_mode=ParseMode.HTML,
                                   reply_markup=panel.back_owner())
        await cq.answer()

    @app.on_callback_query(filters.regex("^pipe_new$"))
    @auth_required
    async def cb_pipe_new(c, cq: CallbackQuery):
        store.set_session(cq.from_user.id, "await_pipe_name")
        await cq.message.edit_text(
            f"<b>{G.ADD}  {G.g('New Pipeline')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the pipeline name.')}\n<i>Example: <code>News Feed</code></i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_home()
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_view:(\d+)$"))
    @auth_required
    async def cb_pipe_view(c, cq: CallbackQuery):
        await _render_pipe(cq, int(cq.matches[0].group(1)))
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_toggle:(\d+)$"))
    @auth_required
    async def cb_toggle(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        uid  = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        if not pipe.get("source"):
            await cq.answer(G.g("Set source channel first!"), show_alert=True); return
        if not pipe.get("targets"):
            await cq.answer(G.g("Add at least one target first!"), show_alert=True); return
        updated = await store.toggle_pipeline(uid, pid)
        action  = "Pipeline Activated" if updated["active"] else "Pipeline Deactivated"
        if not updated["active"]:
            from relay.throttle import drop_queue
            drop_queue(pid)
        await logger.emit(uid, action, f"Pipe #{pid} — {pipe['name']}", level="pipe")
        await _render_pipe(cq, pid)
        await cq.answer(G.g(action))

    @app.on_callback_query(filters.regex(r"^pipe_source:(\d+)$"))
    @auth_required
    async def cb_source(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_source", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.SRC}  {G.g('Set Source Channel')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the source channel')} <b>{G.g('@username')}</b> {G.g('or t.me link.')}\n\n"
            f"{G.WARN} {G.g('Username only — numeric IDs not supported.')}\n\n"
            f"<i>{G.g('Examples')}:</i>\n<code>@mychannel</code>\n<code>https://t.me/mychannel</code>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_targets:(\d+)$"))
    @auth_required
    async def cb_targets(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        tgt_str = "\n".join(f"  {G.BULLET}  <code>{t}</code>" for t in pipe.get("targets",[]))
        await cq.message.edit_text(
            f"<b>{G.TGT}  {G.g('Targets')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"{tgt_str or '<i>' + G.g('none yet') + '</i>'}\n{G.THIN}\n"
            f"<i>{G.g('Unlimited targets supported.')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.targets_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^tgt_add:(\d+)$"))
    @auth_required
    async def cb_tgt_add(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_target", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.ADD}  {G.g('Add Target')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the target channel or group')} <b>{G.g('@username')}</b> {G.g('or t.me link.')}\n\n"
            f"{G.WARN} {G.g('Username only — numeric IDs not supported.')}\n\n"
            f"<i>{G.g('Examples')}:</i>\n<code>@mygroup</code>\n<code>https://t.me/mygroup</code>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^tgt_remove:(\d+):(.+)$"))
    @auth_required
    async def cb_tgt_remove(c, cq: CallbackQuery):
        pid    = int(cq.matches[0].group(1))
        target = cq.matches[0].group(2)
        uid    = cq.from_user.id
        pipe   = await store.remove_target(uid, pid, target)
        tgt_str= "\n".join(f"  {G.BULLET}  <code>{t}</code>" for t in pipe.get("targets",[]))
        await cq.message.edit_text(
            f"<b>{G.TGT}  {G.g('Targets')}</b>\n{G.LINE}\n\n"
            f"{tgt_str or '<i>' + G.g('none') + '</i>'}",
            parse_mode=ParseMode.HTML, reply_markup=panel.targets_menu(pipe)
        )
        await logger.emit(uid, "Target Removed", f"Pipe #{pid} — {target}", level="pipe")
        await cq.answer(G.g("Removed"))

    @app.on_callback_query(filters.regex(r"^pipe_settings:(\d+)$"))
    @auth_required
    async def cb_settings(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        await cq.message.edit_text(
            f"<b>{G.GEAR}  {G.g('Settings')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"{G.g('Configure forwarding behaviour.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.pipe_settings(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^ps_hidetag:(\d+)$"))
    @auth_required
    async def cb_hidetag(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        pipe = await store.update_pipeline(uid, pid, hide_tag=not pipe.get("hide_tag", True))
        await cq.message.edit_reply_markup(reply_markup=panel.pipe_settings(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^ps_dedup:(\d+)$"))
    @auth_required
    async def cb_dedup(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        pipe = await store.update_pipeline(uid, pid, dedup=not pipe.get("dedup", True))
        await cq.message.edit_reply_markup(reply_markup=panel.pipe_settings(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^ps_media:(\d+)$"))
    @auth_required
    async def cb_media_menu(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        await cq.message.edit_text(
            f"<b>{G.g('Media Filter')}</b>\n{G.LINE}\n\n"
            f"{G.g('Select which content types to forward.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.media_filter_kb(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^ps_mf_set:(\d+):(\w+)$"))
    @auth_required
    async def cb_mf_set(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); mf = cq.matches[0].group(2)
        pipe = await store.update_pipeline(cq.from_user.id, pid, media_filter=mf)
        await cq.message.edit_reply_markup(reply_markup=panel.media_filter_kb(pipe))
        await cq.answer(G.g(f"Set: {mf.upper()}"))

    @app.on_callback_query(filters.regex(r"^ps_delay:(\d+)$"))
    @auth_required
    async def cb_delay(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_delay", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.RATE}  {G.g('Set Delay')}</b>\n{G.LINE}\n\n"
            f"{G.g('Seconds between each target forward.')}\n"
            f"<i>{G.g('Minimum recommended: 1.0 — prevents flood.')}</i>\n"
            f"<i>0 = instant (not recommended)</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^ps_ratelimit:(\d+)$"))
    @auth_required
    async def cb_ratelimit(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_ratelimit", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.RATE}  {G.g('Set Rate Limit')}</b>\n{G.LINE}\n\n"
            f"{G.g('Maximum messages forwarded per minute for this pipeline.')}\n"
            f"<i>{G.g('Default')}: <code>{environ.RATE_LIMIT}</code>  "
            f"{G.g('Recommended max')}: <code>20</code></i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^ps_limit:(\d+)$"))
    @auth_required
    async def cb_limit(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_limit", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.LIMIT}  {G.g('Forward Limit')}</b>\n{G.LINE}\n\n"
            f"{G.g('Pipeline auto-pauses after this many forwards.')}\n"
            f"<i>{G.g('Send')} <code>0</code> {G.g('to disable.')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_stats:(\d+)$"))
    @auth_required
    async def cb_pipe_stats(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        s    = pipe.get("stats", {})
        text = (
            f"<b>{G.CHART}  {G.g('Stats')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"{G.BULLET}  {G.g('Forwarded')}: <code>{s.get('forwarded',0)}</code>\n"
            f"{G.BULLET}  {G.g('Skipped')}: <code>{s.get('skipped',0)}</code>\n"
            f"{G.BULLET}  {G.g('Deduped')}: <code>{s.get('deduped',0)}</code>\n"
            f"{G.BULLET}  {G.g('Errors')}: <code>{s.get('errors',0)}</code>\n"
            f"{G.THIN}\n"
            f"{G.BULLET}  {G.g('Limit')}: <code>{pipe.get('fwd_limit',0) or G.g('off')}</code>\n"
            f"{G.BULLET}  {G.g('Created')}: <code>{str(pipe.get('created_at',''))[:10]}</code>\n"
        )
        await cq.message.edit_text(text, parse_mode=ParseMode.HTML,
                                   reply_markup=panel.pipe_stats_kb(pid))
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_stats_reset:(\d+)$"))
    @auth_required
    async def cb_stats_reset(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        await store.reset_stats(cq.from_user.id, pid)
        await _render_pipe(cq, pid)
        await cq.answer(G.g("Stats reset!"))

    @app.on_callback_query(filters.regex(r"^pipe_filters:(\d+)$"))
    @auth_required
    async def cb_filters(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        await cq.message.edit_text(
            f"<b>{G.KEY}  {G.g('Filters')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"<b>{G.g('Keywords')}</b>: {G.g('forward only matching messages')}\n"
            f"<b>{G.g('Blacklist')}</b>: {G.g('skip messages with these words')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.filters_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_keywords:(\d+)$"))
    @auth_required
    async def cb_keywords(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        kws  = pipe.get("keywords", [])
        kstr = "\n".join(f"  {G.BULLET}  <code>{k}</code>" for k in kws) or f"<i>{G.g('none — forwarding all')}</i>"
        await cq.message.edit_text(
            f"<b>{G.KEY}  {G.g('Keywords')}</b>\n{G.LINE}\n\n{kstr}",
            parse_mode=ParseMode.HTML, reply_markup=panel.keywords_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^kw_add:(\d+)$"))
    @auth_required
    async def cb_kw_add(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_keyword", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.KEY}  {G.g('Add Keyword')}</b>\n{G.LINE}\n\n{G.g('Send keyword or phrase.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^kw_rm:(\d+):(.+)$"))
    @auth_required
    async def cb_kw_rm(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); kw = cq.matches[0].group(2)
        uid  = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        kws  = [k for k in pipe.get("keywords",[]) if k != kw]
        pipe = await store.update_pipeline(uid, pid, keywords=kws)
        kstr = "\n".join(f"  {G.BULLET}  <code>{k}</code>" for k in pipe.get("keywords",[])) or f"<i>{G.g('none')}</i>"
        await cq.message.edit_text(
            f"<b>{G.KEY}  {G.g('Keywords')}</b>\n{G.LINE}\n\n{kstr}",
            parse_mode=ParseMode.HTML, reply_markup=panel.keywords_menu(pipe)
        )
        await cq.answer(G.g("Removed"))

    @app.on_callback_query(filters.regex(r"^kw_clear:(\d+)$"))
    @auth_required
    async def cb_kw_clear(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.clear_keywords(cq.from_user.id, pid)
        await cq.message.edit_text(
            f"<b>{G.KEY}  {G.g('Keywords')}</b>\n{G.LINE}\n\n<i>{G.g('All cleared.')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.keywords_menu(pipe)
        )
        await cq.answer(G.g("Cleared"))

    @app.on_callback_query(filters.regex(r"^pipe_blacklist:(\d+)$"))
    @auth_required
    async def cb_blacklist(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        bls  = pipe.get("blacklist", [])
        bstr = "\n".join(f"  {G.CROSS}  <code>{b}</code>" for b in bls) or f"<i>{G.g('none')}</i>"
        await cq.message.edit_text(
            f"<b>{G.BAN}  {G.g('Blacklist')}</b>\n{G.LINE}\n\n{bstr}",
            parse_mode=ParseMode.HTML, reply_markup=panel.blacklist_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^bl_add:(\d+)$"))
    @auth_required
    async def cb_bl_add(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_blacklist", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.BAN}  {G.g('Add Blacklist Word')}</b>\n{G.LINE}\n\n{G.g('Send word to blacklist.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^bl_rm:(\d+):(.+)$"))
    @auth_required
    async def cb_bl_rm(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); word = cq.matches[0].group(2)
        uid  = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        bl   = [b for b in pipe.get("blacklist",[]) if b != word]
        pipe = await store.update_pipeline(uid, pid, blacklist=bl)
        bstr = "\n".join(f"  {G.CROSS}  <code>{b}</code>" for b in pipe.get("blacklist",[])) or f"<i>{G.g('none')}</i>"
        await cq.message.edit_text(
            f"<b>{G.BAN}  {G.g('Blacklist')}</b>\n{G.LINE}\n\n{bstr}",
            parse_mode=ParseMode.HTML, reply_markup=panel.blacklist_menu(pipe)
        )
        await cq.answer(G.g("Removed"))

    @app.on_callback_query(filters.regex(r"^bl_clear:(\d+)$"))
    @auth_required
    async def cb_bl_clear(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.clear_blacklist(cq.from_user.id, pid)
        await cq.message.edit_text(
            f"<b>{G.BAN}  {G.g('Blacklist')}</b>\n{G.LINE}\n\n<i>{G.g('All cleared.')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.blacklist_menu(pipe)
        )
        await cq.answer(G.g("Cleared"))

    @app.on_callback_query(filters.regex(r"^pipe_caption:(\d+)$"))
    @auth_required
    async def cb_caption(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        mode = pipe.get("caption_mode","original")
        txt  = pipe.get("caption_text","") or f"<i>{G.g('not set')}</i>"
        await cq.message.edit_text(
            f"<b>{G.CAP}  {G.g('Caption Editor')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"<b>{G.g('Mode')}</b>: <code>{mode.upper()}</code>\n"
            f"<b>{G.g('Text')}</b>: {txt}\n\n"
            f"{G.THIN}\n"
            f"<code>original</code> — {G.g('keep original')}\n"
            f"<code>prepend</code>  — {G.g('add before')}\n"
            f"<code>append</code>   — {G.g('add after')}\n"
            f"<code>replace</code>  — {G.g('replace entirely')}\n",
            parse_mode=ParseMode.HTML, reply_markup=panel.caption_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^cap_mode:(\d+):(\w+)$"))
    @auth_required
    async def cb_cap_mode(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); mode = cq.matches[0].group(2)
        pipe = await store.update_pipeline(cq.from_user.id, pid, caption_mode=mode)
        await cq.message.edit_reply_markup(reply_markup=panel.caption_menu(pipe))
        await cq.answer(G.g(f"Mode: {mode.upper()}"))

    @app.on_callback_query(filters.regex(r"^cap_edit:(\d+)$"))
    @auth_required
    async def cb_cap_edit(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_caption", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.EDIT}  {G.g('Edit Caption Text')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send your caption text. Supports HTML formatting.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_schedule:(\d+)$"))
    @auth_required
    async def cb_schedule(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        await cq.message.edit_text(
            f"<b>{G.SCHED}  {G.g('Schedule')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"{G.g('Pipeline only forwards within the set time window.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.schedule_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^sched_toggle:(\d+)$"))
    @auth_required
    async def cb_sched_toggle(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        sched = pipe.get("schedule", {})
        sched["enabled"] = not sched.get("enabled", False)
        pipe  = await store.update_pipeline(uid, pid, schedule=sched)
        await cq.message.edit_reply_markup(reply_markup=panel.schedule_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^sched_start:(\d+)$"))
    @auth_required
    async def cb_sched_start(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_sched_start", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.SCHED}  {G.g('Start Hour')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send hour 0–23. Example:')} <code>9</code>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^sched_end:(\d+)$"))
    @auth_required
    async def cb_sched_end(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_sched_end", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.SCHED}  {G.g('End Hour')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send hour 0–23. Example:')} <code>22</code>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^sched_tz:(\d+)$"))
    @auth_required
    async def cb_sched_tz(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_sched_tz", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>[ TZ ]  {G.g('Timezone')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send timezone string.')}\n"
            f"<i>Examples: <code>Asia/Kolkata</code>  <code>UTC</code>  <code>America/New_York</code></i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_export:(\d+)$"))
    @auth_required
    async def cb_export(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        export = {k: v for k, v in pipe.items() if k != "_id"}
        for key in ("created_at", "updated_at"):
            if key in export and hasattr(export[key], "isoformat"):
                export[key] = export[key].isoformat()
        data  = json.dumps(export, indent=2, default=str)
        fname = f"pipe_{pid}_{pipe['name'].replace(' ','_')}.json"
        fpath = f"/tmp/{fname}"
        with open(fpath, "w") as f:
            f.write(data)
        await cq.message.reply_document(
            document=fpath,
            caption=f"<b>{G.EXPRT}  {G.g('Pipeline Export')}</b> — <code>{G.g(pipe['name'])}</code>",
            parse_mode=ParseMode.HTML
        )
        os.remove(fpath)
        await logger.emit(uid, "Pipeline Exported", f"Pipe #{pid}", level="info")
        await cq.answer(G.g("Exported"))

    @app.on_callback_query(filters.regex(r"^pipe_delete_ask:(\d+)$"))
    @auth_required
    async def cb_delete_ask(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        await cq.message.edit_text(
            f"<b>{G.WARN}  {G.g('Delete Pipeline')}</b>\n{G.LINE}\n\n"
            f"{G.g('Delete')} <b>{G.g(pipe['name'])}</b>?\n"
            f"<i>{G.g('This cannot be undone.')}</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.confirm_kb(f"pipe_delete_confirm:{pid}", "home")
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_delete_confirm:(\d+)$"))
    @auth_required
    async def cb_delete_confirm(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        name = pipe["name"] if pipe else str(pid)
        await store.delete_pipeline(uid, pid)
        from relay.throttle import drop_queue
        drop_queue(pid)
        await logger.emit(uid, "Pipeline Deleted", f"#{pid} — {name}", level="warn")
        pipes  = await store.get_all_pipelines(uid)
        is_own = uid == environ.OWNER_ID
        await cq.message.edit_text(
            f"<b>{G.OK}  {G.g('Deleted')}</b>\n{G.LINE}\n\n{G.g('Pipeline removed.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.home(pipes, is_own)
        )
        await cq.answer(G.g("Deleted"))

    @app.on_callback_query(filters.regex("^cmd_list$"))
    @auth_required
    async def cb_cmd_list(c, cq: CallbackQuery):
        uid  = cq.from_user.id
        cmds = await store.get_all_commands(uid if uid != environ.OWNER_ID else None)
        await cq.message.edit_text(
            f"<b>{G.CMD}  {G.g('Custom Commands')}</b>\n{G.LINE}\n\n"
            f"{G.g('Total')}: <b>{len(cmds)}</b>\n{G.THIN}",
            parse_mode=ParseMode.HTML, reply_markup=panel.cmd_list_kb(cmds)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^cmd_schema$"))
    @auth_required
    async def cb_cmd_schema(c, cq: CallbackQuery):
        from core.cmds import CMD_SCHEMA_EXAMPLE
        import json, html
        schema_text = json.dumps(CMD_SCHEMA_EXAMPLE, indent=2)
        await cq.message.edit_text(
            f"<b>{G.CMD}  {G.g('JSON Schema')}</b>\n{G.LINE}\n\n"
            f"<pre>{html.escape(schema_text)}</pre>\n\n"
            f"<i>{G.g('Wrap multiple in an array for bulk import.')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_cmds()
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^cmd_manage:(.+)$"))
    @auth_required
    async def cb_cmd_manage(c, cq: CallbackQuery):
        name = cq.matches[0].group(1)
        cmd  = await store.get_command(name)
        if not cmd: await cq.answer(G.g("Not found"), show_alert=True); return
        payload = cmd.get("payload", {})
        has_photo = G.CHECK if payload.get("photo") else G.CROSS
        has_video = G.CHECK if payload.get("video") else G.CROSS
        btns  = len(payload.get("buttons", []))
        await cq.message.edit_text(
            f"<b>{G.CMD}  /{cmd['command']}</b>\n{G.LINE}\n\n"
            f"<b>{G.g('Status')}</b>: <code>{'enabled' if cmd.get('enabled') else 'disabled'}</code>\n"
            f"<b>{G.g('Used')}</b>: <code>{cmd.get('use_count',0)}x</code>\n"
            f"<b>{G.g('Photo')}</b>: {has_photo}  "
            f"<b>{G.g('Video')}</b>: {has_video}  "
            f"<b>{G.g('Buttons')}</b>: <code>{btns}</code>\n"
            f"{G.THIN}\n"
            f"<b>{G.g('Text')}</b>:\n{payload.get('text','') or '<i>' + G.g('none') + '</i>'}",
            parse_mode=ParseMode.HTML, reply_markup=panel.cmd_manage_kb(cmd)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^cmd_toggle:(.+)$"))
    @auth_required
    async def cb_cmd_toggle(c, cq: CallbackQuery):
        name = cq.matches[0].group(1)
        cmd  = await store.toggle_command(name)
        if not cmd: await cq.answer(); return
        await cq.message.edit_reply_markup(reply_markup=panel.cmd_manage_kb(cmd))
        state = G.g("Enabled") if cmd.get("enabled") else G.g("Disabled")
        await cq.answer(G.g(state))

    @app.on_callback_query(filters.regex(r"^cmd_delete_ask:(.+)$"))
    @auth_required
    async def cb_cmd_delete_ask(c, cq: CallbackQuery):
        name = cq.matches[0].group(1)
        await cq.message.edit_text(
            f"<b>{G.WARN}  {G.g('Delete Command')}</b>\n{G.LINE}\n\n"
            f"<code>/{name}</code> {G.g('will be removed.')}\n"
            f"<i>{G.g('Cannot be undone.')}</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.confirm_kb(f"cmd_delete_confirm:{name}", "cmd_list")
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^cmd_delete_confirm:(.+)$"))
    @auth_required
    async def cb_cmd_delete_confirm(c, cq: CallbackQuery):
        name = cq.matches[0].group(1)
        await store.delete_command(name)
        await logger.emit(cq.from_user.id, "Command Deleted", f"/{name}", level="info")
        cmds = await store.get_all_commands()
        await cq.message.edit_text(
            f"<b>{G.OK}  {G.g('Deleted')}</b>: <code>/{name}</code>",
            parse_mode=ParseMode.HTML, reply_markup=panel.cmd_list_kb(cmds)
        )
        await cq.answer(G.g("Deleted"))

    @app.on_callback_query(filters.regex("^cmd_add_prompt$"))
    @auth_required
    async def cb_cmd_add_prompt(c, cq: CallbackQuery):
        await cq.message.edit_text(
            f"<b>{G.ADD}  {G.g('Add Command')}</b>\n{G.LINE}\n\n"
            f"<b>{G.g('Option 1 — Simple')}</b>\n"
            f"Send: <code>/add_cmd name &lt;b&gt;Your text&lt;/b&gt;</code>\n\n"
            f"<b>{G.g('Option 2 — Full JSON')}</b>\n"
            f"Send: <code>/add_cmd</code> (reply to a JSON message)\n\n"
            f"<b>{G.g('Option 3 — Bulk Import')}</b>\n"
            f"Send: <code>/add_cmd</code> (reply to a .json file)\n\n"
            f"<i>Use /cmd_schema to see the JSON format.</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_cmds()
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^owner_panel$"))
    @owner_only
    async def cb_owner_panel(c, cq: CallbackQuery):
        await cq.message.edit_text(
            f"<b>{G.CROWN}  {G.g('Owner Panel')}</b>\n{G.LINE}\n\n"
            f"{G.g('Full bot control. Be careful.')}\n{G.THIN}",
            parse_mode=ParseMode.HTML, reply_markup=panel.owner_panel()
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^admin_list$"))
    @owner_only
    async def cb_admin_list(c, cq: CallbackQuery):
        admins = await store.get_all_admins()
        await cq.message.edit_text(
            f"<b>{G.ADMIN}  {G.g('Admin Management')}</b>\n{G.LINE}\n\n"
            f"{G.g('Total')}: <b>{len(admins)}</b>\n{G.THIN}",
            parse_mode=ParseMode.HTML, reply_markup=panel.admin_list_kb(admins)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^admin_add_prompt$"))
    @owner_only
    async def cb_admin_add_prompt(c, cq: CallbackQuery):
        store.set_session(cq.from_user.id, "await_admin_id")
        await cq.message.edit_text(
            f"<b>{G.ADD}  {G.g('Add Admin')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the Telegram user ID.')}\n<i>Example: <code>123456789</code></i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_owner()
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^admin_manage:(\d+)$"))
    @owner_only
    async def cb_admin_manage(c, cq: CallbackQuery):
        uid   = int(cq.matches[0].group(1))
        admin = await store.get_admin(uid)
        if not admin: await cq.answer(G.g("Not found"), show_alert=True); return
        uname = f"@{admin.get('username')}" if admin.get("username") else str(uid)
        await cq.message.edit_text(
            f"<b>{G.ADMIN}  {G.g('Manage Admin')}</b> — {uname}\n{G.LINE}\n\n"
            f"{G.g('Toggle permissions or ban/unban.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.admin_manage_kb(admin)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^admin_perm_toggle:(\d+):(\w+)$"))
    @owner_only
    async def cb_perm_toggle(c, cq: CallbackQuery):
        uid   = int(cq.matches[0].group(1)); perm = cq.matches[0].group(2)
        admin = await store.get_admin(uid)
        if not admin: await cq.answer(); return
        perms = admin.get("perms", [])
        if perm in perms: perms.remove(perm)
        else: perms.append(perm)
        admin = await store.update_admin_perms(uid, perms)
        await cq.message.edit_reply_markup(reply_markup=panel.admin_manage_kb(admin))
        await logger.emit(cq.from_user.id, "Admin Perms Updated", f"uid={uid} {perms}", level="admin")
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^admin_ban_toggle:(\d+)$"))
    @owner_only
    async def cb_ban_toggle(c, cq: CallbackQuery):
        uid   = int(cq.matches[0].group(1))
        admin = await store.get_admin(uid)
        if not admin: await cq.answer(); return
        if admin.get("is_banned"):
            await store.unban_admin(uid); action = "Admin Unbanned"
        else:
            await store.ban_admin(uid);   action = "Admin Banned"
        admin = await store.get_admin(uid)
        await cq.message.edit_reply_markup(reply_markup=panel.admin_manage_kb(admin))
        await logger.emit(cq.from_user.id, action, f"uid={uid}", level="admin")
        await cq.answer(G.g(action))

    @app.on_callback_query(filters.regex(r"^admin_remove_ask:(\d+)$"))
    @owner_only
    async def cb_admin_remove_ask(c, cq: CallbackQuery):
        uid = int(cq.matches[0].group(1))
        await cq.message.edit_text(
            f"<b>{G.WARN}  {G.g('Remove Admin')}</b>\n{G.LINE}\n\n"
            f"{G.g('Remove admin')} <code>{uid}</code>?\n"
            f"<i>{G.g('They will lose all access.')}</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.confirm_kb(f"admin_remove_confirm:{uid}", "admin_list")
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^admin_remove_confirm:(\d+)$"))
    @owner_only
    async def cb_admin_remove_confirm(c, cq: CallbackQuery):
        uid = int(cq.matches[0].group(1))
        await store.remove_admin(uid)
        admins = await store.get_all_admins()
        await logger.emit(cq.from_user.id, "Admin Removed", f"uid={uid}", level="admin")
        await cq.message.edit_text(
            f"<b>{G.OK}  {G.g('Admin Removed')}</b>",
            parse_mode=ParseMode.HTML, reply_markup=panel.admin_list_kb(admins)
        )
        await cq.answer(G.g("Removed"))

    @app.on_callback_query(filters.regex("^activity_log$"))
    @owner_only
    async def cb_activity_log(c, cq: CallbackQuery):
        logs = await store.get_activity_log(limit=15)
        if not logs:
            await cq.message.edit_text(
                f"<b>{G.LOG}  {G.g('Activity Log')}</b>\n{G.LINE}\n\n"
                f"<i>{G.g('No activity yet.')}</i>",
                parse_mode=ParseMode.HTML, reply_markup=panel.back_owner()
            )
            await cq.answer(); return
        lines = [f"<b>{G.LOG}  {G.g('Activity Log')}</b> ({G.g('last 15')})\n{G.LINE}\n"]
        for l in logs:
            ts  = str(l.get("ts",""))[:16].replace("T"," ")
            uid = l.get("user_id","?")
            act = G.g(l.get("action",""))
            det = l.get("detail","")
            lines.append(f"<code>{ts}</code> <code>{uid}</code>\n{G.ARR}  {act}  {det}\n")
        await cq.message.edit_text("\n".join(lines), parse_mode=ParseMode.HTML,
                                   reply_markup=panel.back_owner())
        await cq.answer()

    @app.on_callback_query(filters.regex("^broadcast_prompt$"))
    @owner_only
    async def cb_broadcast_prompt(c, cq: CallbackQuery):
        store.set_session(cq.from_user.id, "await_broadcast")
        await cq.message.edit_text(
            f"<b>{G.BROAD}  {G.g('Broadcast')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send your broadcast message. Supports HTML formatting.')}\n"
            f"<i>{G.g('Will be sent to all admins.')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_owner()
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^all_pipelines$"))
    @owner_only
    async def cb_all_pipelines(c, cq: CallbackQuery):
        pipes = await store.get_all_pipelines_global()
        if not pipes:
            await cq.message.edit_text(
                f"<b>{G.g('No pipelines.')}</b>",
                parse_mode=ParseMode.HTML, reply_markup=panel.back_owner()
            )
            await cq.answer(); return
        lines = [f"<b>{G.CIRCLE}  {G.g('All Pipelines')}</b>\n{G.LINE}\n"]
        for p in pipes:
            st = G.PLAY if p["active"] else G.STOP
            lines.append(
                f"{st}  <b>[{p['pipe_id']}]</b> {G.g(p['name'])}\n"
                f"   <code>{p['owner']}</code>  "
                f"{G.SRC} <code>{p.get('source','—')}</code>  "
                f"{G.CHART} <code>{p.get('stats',{}).get('forwarded',0)}</code>\n"
            )
        await cq.message.edit_text("\n".join(lines), parse_mode=ParseMode.HTML,
                                   reply_markup=panel.back_owner())
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_buttons:(\d+)$"))
    @auth_required
    async def cb_pipe_buttons(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        btns = pipe.get("inline_buttons", [])
        lines = [
            f"<b>{G.LINK}  {G.g('Inline Buttons')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"{G.g('Buttons attached to every forwarded message.')}\n"
            f"{G.g('URL buttons only — opens link when tapped.')}\n"
            f"{G.THIN}\n"
            f"{G.g('Count')}: <b>{len(btns)}</b>"
        ]
        await cq.message.edit_text(
            "\n".join(lines), parse_mode=ParseMode.HTML,
            reply_markup=panel.inline_buttons_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pbtn_add:(\d+)$"))
    @auth_required
    async def cb_pbtn_add(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_btn_text", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.ADD}  {G.g('Add Button — Step 1/2')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the button label text.')}\n\n"
            f"<i>{G.g('Example:')} <code>Visit Website</code></i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pbtn_remove:(\d+):(\d+)$"))
    @auth_required
    async def cb_pbtn_remove(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        idx = int(cq.matches[0].group(2))
        uid = cq.from_user.id
        pipe = await store.remove_inline_button(uid, pid, idx)
        if not pipe: await cq.answer(); return
        await cq.message.edit_reply_markup(reply_markup=panel.inline_buttons_menu(pipe))
        await cq.answer(G.g("Removed"))

    @app.on_callback_query(filters.regex(r"^pbtn_clear:(\d+)$"))
    @auth_required
    async def cb_pbtn_clear(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.clear_inline_buttons(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        await cq.message.edit_reply_markup(reply_markup=panel.inline_buttons_menu(pipe))
        await cq.answer(G.g("Cleared"))

    @app.on_callback_query(filters.regex("^pause_all_ask$"))
    @owner_only
    async def cb_pause_all_ask(c, cq: CallbackQuery):
        await cq.message.edit_text(
            f"<b>{G.WARN}  {G.g('Pause All Pipelines')}</b>\n{G.LINE}\n\n"
            f"{G.g('This will deactivate ALL active pipelines globally.')}\n"
            f"<i>{G.g('Are you sure?')}</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.confirm_kb("pause_all_confirm", "owner_panel")
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^pause_all_confirm$"))
    @owner_only
    async def cb_pause_all_confirm(c, cq: CallbackQuery):
        pipes = await store.get_active_pipelines()
        count = 0
        for p in pipes:
            await store.update_pipeline(p["owner"], p["pipe_id"], active=False)
            from relay.throttle import drop_queue
            drop_queue(p["pipe_id"])
            count += 1
        await logger.emit(cq.from_user.id, "All Pipelines Paused", f"count={count}", level="owner")
        await cq.message.edit_text(
            f"<b>{G.OK}  {G.g('All Pipelines Paused')}</b>\n{G.LINE}\n\n"
            f"{G.STOP}  {G.g('Paused')}: <b>{count}</b> {G.g('pipelines')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_owner()
        )
        await cq.answer(G.g("Done"))

    @app.on_callback_query(filters.regex(r"^pipe_rename:(\d+)$"))
    @auth_required
    async def cb_pipe_rename(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_pipe_rename", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.EDIT}  {G.g('Rename Pipeline')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the new name for this pipeline.')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^cmd_test:(.+)$"))
    @auth_required
    async def cb_cmd_test(c, cq: CallbackQuery):
        name = cq.matches[0].group(1)
        cmd  = await store.get_command(name)
        if not cmd:
            await cq.answer(G.g("Command not found"), show_alert=True); return
        payload  = cmd.get("payload", {})
        text     = payload.get("text", "")
        photo    = payload.get("photo")
        video    = payload.get("video")
        buttons  = payload.get("buttons", [])
        from core.cmds import _build_keyboard
        keyboard = _build_keyboard(buttons)
        await cq.answer(G.g("Sending preview..."))
        try:
            if photo:
                await cq.message.reply_photo(photo=photo, caption=text or None,
                    parse_mode=ParseMode.HTML, reply_markup=keyboard)
            elif video:
                await cq.message.reply_video(video=video, caption=text or None,
                    parse_mode=ParseMode.HTML, reply_markup=keyboard)
            else:
                await cq.message.reply(text or G.g("(empty)"),
                    parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except Exception as e:
            await cq.message.reply(
                f"<b>{G.WARN}  {G.g('Preview Failed')}</b>\n<code>{e}</code>",
                parse_mode=ParseMode.HTML
            )

    @app.on_callback_query(filters.regex("^bot_restart_ask$"))
    @owner_only
    async def cb_restart_ask(c, cq: CallbackQuery):
        await cq.message.edit_text(
            f"<b>{G.RELOAD}  {G.g('Restart Bot')}</b>\n{G.LINE}\n\n"
            f"<i>{G.g('Are you sure?')}</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.confirm_kb("bot_restart_confirm", "owner_panel")
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^bot_restart_confirm$"))
    @owner_only
    async def cb_restart_confirm(c, cq: CallbackQuery):
        await cq.message.edit_text(
            f"<b>{G.RELOAD}  {G.g('Restarting...')}</b>",
            parse_mode=ParseMode.HTML
        )
        await logger.emit(cq.from_user.id, "Bot Restarted", level="owner")
        await cq.answer()
        await asyncio.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @app.on_callback_query(filters.regex(r"^ps_minlen:(\d+)$"))
    @auth_required
    async def cb_minlen(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_minlen", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>[ ]  {G.g('Min Message Length')}</b>\n{G.LINE}\n\n"
            f"{G.g('Skip messages shorter than N characters.')}\n"
            f"<i>{G.g('Send')} <code>0</code> {G.g('to disable.')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^ps_autodel:(\d+)$"))
    @auth_required
    async def cb_autodel(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_autodel", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>[ ]  {G.g('Auto-Delete')}</b>\n{G.LINE}\n\n"
            f"{G.g('Delete forwarded messages after N minutes.')}\n"
            f"<i>{G.g('Send')} <code>0</code> {G.g('to disable.')}</i>\n"
            f"<i>{G.g('Example:')} <code>60</code> = {G.g('delete after 1 hour')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^ps_watermark:(\d+)$"))
    @auth_required
    async def cb_watermark(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        wm = pipe.get("watermark", "") or G.g("not set")
        store.set_session(cq.from_user.id, "await_watermark", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>[ ]  {G.g('Watermark')}</b>\n{G.LINE}\n\n"
            f"{G.g('Current:')} <code>{wm}</code>\n\n"
            f"{G.g('Send a watermark text. It will be prepended to every caption.')}\n"
            f"<i>{G.g('Send')} <code>-</code> {G.g('to clear.')}</i>\n"
            f"<i>{G.g('Supports HTML: <b>bold</b>, <i>italic</i>')}</i>",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_clone_ask:(\d+)$"))
    @auth_required
    async def cb_clone_ask(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        store.set_session(cq.from_user.id, "await_clone_name", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.CLONE}  {G.g('Clone Pipeline')}</b>\n{G.LINE}\n\n"
            f"{G.g('Cloning:')} <b>{G.g(pipe['name'])}</b>\n\n"
            f"{G.g('Send a name for the new cloned pipeline:')}",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^pipe_transform:(\d+)$"))
    @auth_required
    async def cb_transform(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        t = pipe.get("transform", {})
        pattern = t.get("regex_pattern", "") or G.g("none")
        await cq.message.edit_text(
            f"<b>{G.TRANSFORM}  {G.g('Transform')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"{G.BULLET}  {G.g('Regex Filter')}: <code>{'on' if t.get('regex_enabled') else 'off'}</code>\n"
            f"{G.BULLET}  {G.g('Pattern')}: <code>{pattern}</code>\n"
            f"{G.BULLET}  {G.g('Invert Filter')}: <code>{'on' if t.get('invert_filter') else 'off'}</code>\n"
            f"{G.BULLET}  {G.g('Pin Forwarded')}: <code>{'on' if t.get('pin_forwarded') else 'off'}</code>\n"
            f"{G.BULLET}  {G.g('Silent Pin')}: <code>{'on' if t.get('silent_pin') else 'off'}</code>\n"
            f"{G.BULLET}  {G.g('Remove Buttons')}: <code>{'on' if t.get('remove_buttons') else 'off'}</code>\n",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.transform_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^tr_regex_toggle:(\d+)$"))
    @auth_required
    async def cb_tr_regex_toggle(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        t = pipe.get("transform", {})
        t["regex_enabled"] = not t.get("regex_enabled", False)
        pipe = await store.update_pipeline(uid, pid, transform=t)
        await cq.message.edit_reply_markup(reply_markup=panel.transform_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^tr_regex_set:(\d+)$"))
    @auth_required
    async def cb_tr_regex_set(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_regex", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.REGEX}  {G.g('Regex Pattern')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send a regex pattern. Only matching messages will forward.')}\n\n"
            f"<i>Examples:\n"
            f"<code>\\bBTC\\b</code> — match BTC word\n"
            f"<code>^#breaking</code> — hashtag at start\n"
            f"<code>\\d{{4,}}</code> — 4+ digit numbers</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^tr_invert:(\d+)$"))
    @auth_required
    async def cb_tr_invert(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        t = pipe.get("transform", {})
        t["invert_filter"] = not t.get("invert_filter", False)
        pipe = await store.update_pipeline(uid, pid, transform=t)
        await cq.message.edit_reply_markup(reply_markup=panel.transform_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^tr_pin_toggle:(\d+)$"))
    @auth_required
    async def cb_tr_pin(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        t = pipe.get("transform", {})
        t["pin_forwarded"] = not t.get("pin_forwarded", False)
        pipe = await store.update_pipeline(uid, pid, transform=t)
        await cq.message.edit_reply_markup(reply_markup=panel.transform_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^tr_silent_toggle:(\d+)$"))
    @auth_required
    async def cb_tr_silent(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        t = pipe.get("transform", {})
        t["silent_pin"] = not t.get("silent_pin", True)
        pipe = await store.update_pipeline(uid, pid, transform=t)
        await cq.message.edit_reply_markup(reply_markup=panel.transform_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^tr_rmbtn_toggle:(\d+)$"))
    @auth_required
    async def cb_tr_rmbtn(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        t = pipe.get("transform", {})
        t["remove_buttons"] = not t.get("remove_buttons", False)
        pipe = await store.update_pipeline(uid, pid, transform=t)
        await cq.message.edit_reply_markup(reply_markup=panel.transform_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^ps_dryrun:(\d+)$"))
    @auth_required
    async def cb_dryrun(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        pipe = await store.update_pipeline(uid, pid, dry_run=not pipe.get("dry_run", False))
        await cq.message.edit_reply_markup(reply_markup=panel.pipe_settings(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^tr_strip_mentions:(\d+)$"))
    @auth_required
    async def cb_strip_mentions(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        opts = pipe.get("strip_opts", {})
        opts["mentions"] = not opts.get("mentions", False)
        pipe = await store.update_pipeline(uid, pid, strip_opts=opts)
        await cq.message.edit_reply_markup(reply_markup=panel.transform_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^tr_strip_hashtags:(\d+)$"))
    @auth_required
    async def cb_strip_hashtags(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1)); uid = cq.from_user.id
        pipe = await store.get_pipeline(uid, pid)
        if not pipe: await cq.answer(); return
        opts = pipe.get("strip_opts", {})
        opts["hashtags"] = not opts.get("hashtags", False)
        pipe = await store.update_pipeline(uid, pid, strip_opts=opts)
        await cq.message.edit_reply_markup(reply_markup=panel.transform_menu(pipe))
        await cq.answer(G.g("Updated"))

    @app.on_callback_query(filters.regex(r"^pipe_findreplace:(\d+)$"))
    @auth_required
    async def cb_findreplace(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.get_pipeline(cq.from_user.id, pid)
        if not pipe: await cq.answer(); return
        rules = pipe.get("find_replace", [])
        lines = [
            f"<b>{G.EDIT}  {G.g('Find & Replace')}</b> — <code>{G.g(pipe['name'])}</code>\n{G.LINE}\n\n"
            f"{G.g('Rules')}: <b>{len(rules)}</b>\n{G.THIN}\n"
        ]
        for r in rules:
            find_str    = r.get("find", "")
            replace_str = r.get("replace", "")
            lines.append(f"{G.ARR}  <code>{find_str}</code> → <code>{replace_str or '(delete)'}</code>\n")
        await cq.message.edit_text(
            "\n".join(lines), parse_mode=ParseMode.HTML,
            reply_markup=panel.findreplace_menu(pipe)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^fr_add:(\d+)$"))
    @auth_required
    async def cb_fr_add(c, cq: CallbackQuery):
        pid = int(cq.matches[0].group(1))
        store.set_session(cq.from_user.id, "await_fr_find", pipe_id=pid)
        await cq.message.edit_text(
            f"<b>{G.EDIT}  {G.g('Add Find & Replace — Step 1/2')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the text to FIND (exact match, case-sensitive).')}",
            parse_mode=ParseMode.HTML, reply_markup=panel.back_pipe(pid)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^fr_clear:(\d+)$"))
    @auth_required
    async def cb_fr_clear(c, cq: CallbackQuery):
        pid  = int(cq.matches[0].group(1))
        pipe = await store.clear_find_replace(cq.from_user.id, pid)
        await cq.message.edit_reply_markup(reply_markup=panel.findreplace_menu(pipe))
        await cq.answer(G.g("Cleared"))

    @app.on_callback_query(filters.regex(r"^fr_rm:(\d+):(.+)$"))
    @auth_required
    async def cb_fr_rm(c, cq: CallbackQuery):
        pid      = int(cq.matches[0].group(1))
        find_str = cq.matches[0].group(2)
        uid      = cq.from_user.id
        pipe     = await store.remove_find_replace(uid, pid, find_str)
        if not pipe: await cq.answer(); return
        await cq.message.edit_reply_markup(reply_markup=panel.findreplace_menu(pipe))
        await cq.answer(G.g("Removed"))

    @app.on_callback_query(filters.regex("^fj_manage$"))
    @owner_only
    async def cb_fj_manage(c, cq: CallbackQuery):
        channels = await store.get_force_join_channels()
        env_chs  = environ.FORCE_JOIN
        all_chs  = list(dict.fromkeys(env_chs + channels))
        note = ""
        if env_chs:
            note = f"\n<i>{G.g('Env channels are always active:')} <code>{', '.join(env_chs)}</code></i>"
        await cq.message.edit_text(
            f"<b>{G.CHANNELS}  {G.g('Force-Join Channels')}</b>\n{G.LINE}\n\n"
            f"{G.g('Users must join these channels to use the bot.')}\n"
            f"{G.g('Total')}: <b>{len(all_chs)}</b>{note}\n{G.THIN}",
            parse_mode=ParseMode.HTML,
            reply_markup=panel.owner_channels_kb(channels)
        )
        await cq.answer()

    @app.on_callback_query(filters.regex("^fj_add_prompt$"))
    @owner_only
    async def cb_fj_add_prompt(c, cq: CallbackQuery):
        store.set_session(cq.from_user.id, "await_fj_channel")
        await cq.message.edit_text(
            f"<b>{G.ADD}  {G.g('Add Force-Join Channel')}</b>\n{G.LINE}\n\n"
            f"{G.g('Send the channel username or ID.')}\n\n"
            f"<i>Examples:\n<code>@mychannel</code>\n<code>-1001234567890</code></i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[IBtn(f"{G.BACK}  {G.g('Back')}", callback_data="fj_manage")]])
        )
        await cq.answer()

    @app.on_callback_query(filters.regex(r"^fj_remove:(.+)$"))
    @owner_only
    async def cb_fj_remove(c, cq: CallbackQuery):
        ch = cq.matches[0].group(1)
        channels = await store.remove_force_join_channel(ch)
        await logger.emit(cq.from_user.id, "Force-Join Removed", ch, level="admin")
        await cq.message.edit_reply_markup(reply_markup=panel.owner_channels_kb(channels))
        await cq.answer(G.g("Removed"))

    @app.on_callback_query(filters.regex("^fj_check$"))
    @auth_required
    async def cb_fj_check(c, cq: CallbackQuery):
        uid = cq.from_user.id
        from core.guardian import _check_force_join
        missing = await _check_force_join(c, uid)
        if missing:
            await cq.answer(G.g("Still not joined!"), show_alert=True)
        else:
            pipes   = await store.get_all_pipelines(uid)
            is_own  = uid == environ.OWNER_ID
            name    = cq.from_user.first_name or ""
            text = (
                f"<b>{G.STAR}  {G.g('Nexus Auto-Forward')}</b>\n{G.LINE}\n\n"
                f"{G.CHECK}  {G.g('All channels joined!')}\n\n"
                f"{G.g('Welcome')}, <b>{name}</b>\n"
                f"{G.BULLET}  {G.g('Pipelines')}: <b>{len(pipes)}</b>\n"
            )
            await cq.message.edit_text(text, parse_mode=ParseMode.HTML,
                                        reply_markup=panel.home(pipes, is_own))
            await cq.answer(G.g("Access granted!"))

    @app.on_message(
        filters.private & filters.text &
        ~filters.command([
            "start","menu","help","pipes","new","stats","admins",
            "add_cmd","del_cmd","cmds","cmd_schema","channels",
            "ping","health","lang","uptime","backup","import",
        ])
    )
    @auth_required
    async def on_text(client: Client, msg: Message):
        uid     = msg.from_user.id
        session = store.get_session(uid)
        if not session: return

        state = session["state"]
        data  = session.get("data", {})
        text  = msg.text.strip()
        store.clear_session(uid)

        async def reply(t, kb=None):
            await msg.reply(t, parse_mode=ParseMode.HTML, reply_markup=kb)

        if state == "await_pipe_name":
            pipe  = await store.create_pipeline(uid, text)
            await reply(
                f"<b>{G.OK}  {G.g('Pipeline Created!')}</b>\n{G.LINE}\n\n"
                f"<b>{G.g(pipe['name'])}</b>  <code>#{pipe['pipe_id']}</code>\n\n"
                f"<i>{G.g('Now set a source and targets.')}</i>",
                panel.pipe_detail(pipe)
            )
            await logger.emit(uid, "Pipeline Created", pipe["name"], level="pipe")

        elif state == "await_source":
            pid = data["pipe_id"]
            await reply(f"<b>{G.g('Checking...')}</b> <i>Validating channel, please wait.</i>")
            from core.validator import validate_source
            result = await validate_source(client, uid, text)
            if not result.ok:
                store.set_session(uid, "await_source", pipe_id=pid)
                await reply(
                    f"<b>{G.WARN}  {G.g('Invalid Source')}</b>\n{G.LINE}\n\n"
                    f"{result.error}\n\n<i>{G.g('Please try again.')}</i>",
                    panel.back_pipe(pid)
                )
                return
            normalised = result.username
            pipe = await store.update_pipeline(uid, pid, source=normalised)
            await reply(
                f"<b>{G.OK}  {G.g('Source Set')}</b>\n{G.LINE}\n\n"
                f"{G.SRC}  <b>{result.chat_title}</b>  <code>{normalised}</code>\n\n"
                f"{G.CHECK} {G.g('Membership verified.')}",
                panel.pipe_detail(pipe)
            )
            await logger.emit(uid, "Source Set", f"Pipe #{pid} -> {result.chat_title} ({normalised})", level="pipe")

        elif state == "await_target":
            pid = data["pipe_id"]
            await reply(f"<b>{G.g('Checking...')}</b> <i>Verifying bot admin status, please wait.</i>")
            from core.validator import validate_target
            result = await validate_target(client, text)
            if not result.ok:
                store.set_session(uid, "await_target", pipe_id=pid)
                await reply(
                    f"<b>{G.WARN}  {G.g('Invalid Target')}</b>\n{G.LINE}\n\n"
                    f"{result.error}\n\n<i>{G.g('Please try again.')}</i>",
                    panel.back_pipe(pid)
                )
                return
            normalised = result.username
            pipe = await store.add_target(uid, pid, normalised)
            await reply(
                f"<b>{G.OK}  {G.g('Target Added')}</b>\n{G.LINE}\n\n"
                f"{G.TGT}  <b>{result.chat_title}</b>  <code>{normalised}</code>\n\n"
                f"{G.CHECK} {G.g('Bot is admin with post permission.')}",
                panel.targets_menu(pipe)
            )
            await logger.emit(uid, "Target Added", f"Pipe #{pid} -> {result.chat_title} ({normalised})", level="pipe")

        elif state == "await_delay":
            pid = data["pipe_id"]
            try: delay = float(text)
            except ValueError:
                await reply(f"<b>{G.WARN}  {G.g('Invalid.')}</b> Send a number. Example: <code>1.5</code>"); return
            pipe = await store.update_pipeline(uid, pid, delay=delay)
            await reply(
                f"<b>{G.OK}  {G.g('Delay Updated')}</b>\n{G.LINE}\n\n"
                f"{G.RATE}  <code>{delay}s</code>",
                panel.pipe_settings(pipe)
            )

        elif state == "await_ratelimit":
            pid = data["pipe_id"]
            try:
                rpm = int(text)
                assert 1 <= rpm <= 100
            except (ValueError, AssertionError):
                await reply(f"<b>{G.WARN}</b> Send a number between <code>1</code> and <code>100</code>."); return
            pipe = await store.update_pipeline(uid, pid, rate_limit=rpm)
            from relay.throttle import _buckets, _TokenBucket
            _buckets[pid] = _TokenBucket(rpm / 60.0)
            await reply(
                f"<b>{G.OK}  {G.g('Rate Limit Updated')}</b>\n{G.LINE}\n\n"
                f"{G.RATE}  <code>{rpm}/min</code>",
                panel.pipe_settings(pipe)
            )

        elif state == "await_limit":
            pid = data["pipe_id"]
            try: limit = int(text)
            except ValueError:
                await reply(f"<b>{G.WARN}</b> Send a whole number. Example: <code>100</code> or <code>0</code>"); return
            pipe = await store.update_pipeline(uid, pid, fwd_limit=limit)
            await reply(
                f"<b>{G.OK}  {G.g('Limit Updated')}</b>\n{G.LINE}\n\n"
                f"{G.LIMIT}  <code>{limit if limit else G.g('off')}</code>",
                panel.pipe_settings(pipe)
            )

        elif state == "await_keyword":
            pid  = data["pipe_id"]
            pipe = await store.add_keyword(uid, pid, text)
            await reply(
                f"<b>{G.OK}  {G.g('Keyword Added')}</b>\n{G.LINE}\n\n"
                f"{G.KEY}  <code>{text}</code>",
                panel.keywords_menu(pipe)
            )

        elif state == "await_blacklist":
            pid  = data["pipe_id"]
            pipe = await store.add_blacklist(uid, pid, text)
            await reply(
                f"<b>{G.OK}  {G.g('Blacklisted')}</b>\n{G.LINE}\n\n"
                f"{G.BAN}  <code>{text}</code>",
                panel.blacklist_menu(pipe)
            )

        elif state == "await_caption":
            pid  = data["pipe_id"]
            pipe = await store.update_pipeline(uid, pid, caption_text=text)
            await reply(
                f"<b>{G.OK}  {G.g('Caption Saved')}</b>\n{G.LINE}\n\n"
                f"{G.CAP}  {text}",
                panel.caption_menu(pipe)
            )

        elif state == "await_sched_start":
            pid = data["pipe_id"]
            try: h = int(text); assert 0 <= h <= 23
            except (ValueError, AssertionError):
                await reply(f"<b>{G.WARN}</b> Send 0–23."); return
            pipe  = await store.get_pipeline(uid, pid)
            sched = pipe.get("schedule", {})
            sched["start_hour"] = h
            pipe  = await store.update_pipeline(uid, pid, schedule=sched)
            await reply(
                f"<b>{G.OK}  {G.g('Start Hour Set')}</b>\n{G.LINE}\n\n"
                f"{G.SCHED}  <code>{h:02d}:00</code>",
                panel.schedule_menu(pipe)
            )

        elif state == "await_sched_end":
            pid = data["pipe_id"]
            try: h = int(text); assert 0 <= h <= 23
            except (ValueError, AssertionError):
                await reply(f"<b>{G.WARN}</b> Send 0–23."); return
            pipe  = await store.get_pipeline(uid, pid)
            sched = pipe.get("schedule", {})
            sched["end_hour"] = h
            pipe  = await store.update_pipeline(uid, pid, schedule=sched)
            await reply(
                f"<b>{G.OK}  {G.g('End Hour Set')}</b>\n{G.LINE}\n\n"
                f"{G.SCHED}  <code>{h:02d}:00</code>",
                panel.schedule_menu(pipe)
            )

        elif state == "await_sched_tz":
            pid = data["pipe_id"]
            try:
                import pytz; pytz.timezone(text)
            except Exception:
                await reply(f"<b>{G.WARN}</b> Invalid timezone. Try <code>Asia/Kolkata</code> or <code>UTC</code>"); return
            pipe  = await store.get_pipeline(uid, pid)
            sched = pipe.get("schedule", {})
            sched["tz"] = text
            pipe  = await store.update_pipeline(uid, pid, schedule=sched)
            await reply(
                f"<b>{G.OK}  {G.g('Timezone Set')}</b>\n{G.LINE}\n\n"
                f"[ TZ ]  <code>{text}</code>",
                panel.schedule_menu(pipe)
            )

        elif state == "await_pipe_rename":
            pid = data["pipe_id"]
            pipe = await store.update_pipeline(uid, pid, name=text)
            await reply(
                f"<b>{G.OK}  {G.g('Pipeline Renamed')}</b>\n{G.LINE}\n\n"
                f"{G.g('New name:')} <b>{G.g(text)}</b>",
                panel.pipe_detail(pipe)
            )
            await logger.emit(uid, "Pipeline Renamed", f"#{pid} -> {text}", level="pipe")

        elif state == "await_clone_name":
            src_pid = data["pipe_id"]
            src     = await store.get_pipeline(uid, src_pid)
            if not src:
                await reply(f"<b>{G.WARN}</b>  {G.g('Original pipeline not found.')}"); return
            new_pipe = await store.clone_pipeline(uid, src, text)
            await reply(
                f"<b>{G.OK}  {G.g('Pipeline Cloned!')}</b>\n{G.LINE}\n\n"
                f"{G.g('Source')}: <b>{G.g(src['name'])}</b>\n"
                f"{G.g('Clone')}: <b>{G.g(new_pipe['name'])}</b>  <code>#{new_pipe['pipe_id']}</code>\n\n"
                f"<i>{G.g('All settings copied. Clone is inactive — review and activate.')}</i>",
                panel.pipe_detail(new_pipe)
            )
            await logger.emit(uid, "Pipeline Cloned", f"#{src_pid} → #{new_pipe['pipe_id']} {text}", level="pipe")

        elif state == "await_regex":
            import re
            pid = data["pipe_id"]
            try:
                re.compile(text)
            except re.error as e:
                await reply(f"<b>{G.WARN}  {G.g('Invalid Regex')}</b>\n<code>{e}</code>"); return
            pipe = await store.get_pipeline(uid, pid)
            t    = pipe.get("transform", {})
            t["regex_pattern"] = text
            pipe = await store.update_pipeline(uid, pid, transform=t)
            await reply(
                f"<b>{G.OK}  {G.g('Regex Pattern Set')}</b>\n{G.LINE}\n\n"
                f"<code>{text}</code>",
                panel.transform_menu(pipe)
            )

        elif state == "await_fj_channel":
            ch = text.strip()
            channels = await store.add_force_join_channel(ch)
            await logger.emit(uid, "Force-Join Added", ch, level="admin")
            await reply(
                f"<b>{G.OK}  {G.g('Channel Added')}</b>\n{G.LINE}\n\n"
                f"{G.CHANNELS}  <code>{ch}</code>\n\n"
                f"{G.g('Total channels')}: <code>{len(channels)}</code>",
                panel.owner_channels_kb(channels)
            )

        elif state == "await_btn_text":
            pid = data["pipe_id"]
            store.set_session(uid, "await_btn_url", pipe_id=pid, btn_text=text)
            await reply(
                f"<b>{G.ADD}  {G.g('Add Button — Step 2/2')}</b>\n{G.LINE}\n\n"
                f"{G.g('Label set:')} <b>{text}</b>\n\n"
                f"{G.g('Now send the URL for this button.')}\n\n"
                f"<i>{G.g('Example:')} <code>https://yoursite.com</code></i>",
                panel.back_pipe(pid)
            )

        elif state == "await_minlen":
            pid = data["pipe_id"]
            try: n = int(text); assert n >= 0
            except (ValueError, AssertionError):
                await reply(f"<b>{G.WARN}</b> Send a whole number >= 0."); return
            pipe = await store.update_pipeline(uid, pid, min_length=n)
            await reply(
                f"<b>{G.OK}  {G.g('Min Length Updated')}</b>\n{G.LINE}\n\n"
                f"<code>{n if n else G.g('off')}</code>",
                panel.pipe_settings(pipe)
            )

        elif state == "await_autodel":
            pid = data["pipe_id"]
            try: n = int(text); assert n >= 0
            except (ValueError, AssertionError):
                await reply(f"<b>{G.WARN}</b> Send a whole number >= 0."); return
            pipe = await store.update_pipeline(uid, pid, auto_delete=n)
            await reply(
                f"<b>{G.OK}  {G.g('Auto-Delete Updated')}</b>\n{G.LINE}\n\n"
                f"<code>{str(n) + ' min' if n else G.g('off')}</code>",
                panel.pipe_settings(pipe)
            )

        elif state == "await_watermark":
            pid = data["pipe_id"]
            wm  = "" if text.strip() == "-" else text.strip()
            pipe = await store.update_pipeline(uid, pid, watermark=wm)
            await reply(
                f"<b>{G.OK}  {G.g('Watermark Updated')}</b>\n{G.LINE}\n\n"
                f"<code>{wm or G.g('cleared')}</code>",
                panel.pipe_settings(pipe)
            )

        elif state == "await_btn_url":
            pid      = data["pipe_id"]
            btn_text = data.get("btn_text", "Button")
            url      = text.strip()
            if not url.startswith(("http://", "https://", "tg://")):
                store.set_session(uid, "await_btn_url", pipe_id=pid, btn_text=btn_text)
                await reply(
                    f"<b>{G.WARN}</b> {G.g('URL must start with')} <code>https://</code> {G.g('or')} <code>tg://</code>\n"
                    f"{G.g('Please try again.')}",
                    panel.back_pipe(pid)
                )
                return
            pipe = await store.add_inline_button(uid, pid, btn_text, url)
            await reply(
                f"<b>{G.OK}  {G.g('Button Added!')}</b>\n{G.LINE}\n\n"
                f"{G.LINK}  <b>{btn_text}</b>\n"
                f"<code>{url}</code>\n\n"
                f"{G.g('Total buttons')}: <code>{len(pipe.get('inline_buttons', []))}</code>",
                panel.inline_buttons_menu(pipe)
            )
            await logger.emit(uid, "Button Added", f"Pipe #{pid} — {btn_text}", level="pipe")

        elif state == "await_fr_find":
            pid = data["pipe_id"]
            store.set_session(uid, "await_fr_replace", pipe_id=pid, fr_find=text)
            await reply(
                f"<b>{G.EDIT}  {G.g('Add Find & Replace — Step 2/2')}</b>\n{G.LINE}\n\n"
                f"{G.g('Find')}: <code>{text}</code>\n\n"
                f"{G.g('Now send the REPLACEMENT text.')}  "
                f"<i>{G.g('Send a dash')} <code>-</code> {G.g('to delete (replace with nothing).')}</i>",
                panel.back_pipe(pid)
            )

        elif state == "await_fr_replace":
            pid      = data["pipe_id"]
            find_str = data.get("fr_find", "")
            replace  = "" if text.strip() == "-" else text
            pipe     = await store.add_find_replace(uid, pid, find_str, replace)
            await reply(
                f"<b>{G.OK}  {G.g('Rule Added!')}</b>\n{G.LINE}\n\n"
                f"{G.g('Find')}: <code>{find_str}</code>\n"
                f"{G.g('Replace')}: <code>{replace or '(delete)'}</code>",
                panel.findreplace_menu(pipe)
            )

        elif state == "await_admin_id":
            try: target_uid = int(text)
            except ValueError:
                await reply(f"<b>{G.WARN}</b> Send a numeric user ID."); return
            store.set_session(uid, "await_admin_perms", target_uid=target_uid)
            await reply(
                f"<b>{G.ADMIN}  {G.g('Add Admin')}</b>\n{G.LINE}\n\n"
                f"ID: <code>{target_uid}</code>\n\n"
                f"<b>{G.g('Send permissions')}:</b>\n"
                f"<code>pipelines, broadcast, export, commands</code>\n\n"
                f"<i>Or send <code>all</code> for all permissions.</i>"
            )

        elif state == "await_admin_perms":
            target_uid = data["target_uid"]
            if text.strip().lower() == "all":
                perms = ALL_PERMS[:]
            else:
                perms = [p.strip() for p in text.split(",") if p.strip() in ALL_PERMS]
            try:
                chat  = await client.get_users(target_uid)
                uname = chat.username or ""
            except Exception:
                uname = ""
            await store.add_admin(target_uid, uname, perms)
            await logger.emit(uid, "Admin Added", f"uid={target_uid} perms={perms}", level="admin")
            await reply(
                f"<b>{G.OK}  {G.g('Admin Added')}</b>\n{G.LINE}\n\n"
                f"{G.ADMIN}  <code>{target_uid}</code>\n"
                f"{G.g('Perms')}: <code>{', '.join(perms) or G.g('none')}</code>",
                panel.back_owner()
            )

        elif state == "await_broadcast":
            admins = await store.get_all_admins()
            sent = failed = 0
            for a in admins:
                try:
                    await client.send_message(
                        a["user_id"],
                        f"<b>{G.BROAD}  {G.g('Broadcast')}</b>\n{G.LINE}\n\n{text}",
                        parse_mode=ParseMode.HTML
                    )
                    sent += 1
                except Exception:
                    failed += 1
            await logger.emit(uid, "Broadcast Sent", f"sent={sent} failed={failed}", level="owner")
            await reply(
                f"<b>{G.OK}  {G.g('Broadcast Sent')}</b>\n{G.LINE}\n\n"
                f"{G.CHECK}  {G.g('Delivered')}: <code>{sent}</code>\n"
                f"{G.CROSS}  {G.g('Failed')}: <code>{failed}</code>",
                panel.back_owner()
            )
