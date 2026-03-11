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


from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton as Btn
from wire.glyph import (
    g, OK, NO, BACK, GEAR, CHART, PIPE, SRC, TGT, ADD, TRASH, EDIT,
    PLAY, STOP, CROWN, ADMIN, LOG, BROAD, KEY, BAN,
    DUPE, CAP, LIMIT, RELOAD, EXPRT, SCHED, WARN, INFO, LOZENGE,
    STAR, BULLET, SQUARE, CMD, RATE, QUEUE, CIRCLE, DOT, CHECK, CROSS,
    CLONE, REGEX, TRANSFORM, PIN, JOIN, CHANNELS, LINK,
)
import environ


def home(pipes: list, is_owner: bool = False) -> InlineKeyboardMarkup:
    rows = []
    for p in pipes:
        icon  = PLAY if p["active"] else STOP
        label = f"{icon}  {g(p['name'])}  [{p['pipe_id']}]"
        rows.append([Btn(label, callback_data=f"pipe_view:{p['pipe_id']}")])

    rows.append([Btn(f"{ADD}  {g('New Pipeline')}", callback_data="pipe_new")])

    bottom = [
        Btn(f"{CHART}  {g('Stats')}",  callback_data="global_stats"),
        Btn(f"{CMD}  {g('Commands')}", callback_data="cmd_list"),
        Btn(f"?  {g('Help')}",        callback_data="help"),
    ]
    if is_owner:
        rows.append([Btn(f"{CROWN}  {g('Owner Panel')}", callback_data="owner_panel")])
    rows.append(bottom)
    return InlineKeyboardMarkup(rows)


def pipe_detail(pipe: dict) -> InlineKeyboardMarkup:
    pid    = pipe["pipe_id"]
    active = pipe["active"]
    toggle = f"{STOP}  {g('Deactivate')}" if active else f"{PLAY}  {g('Activate')}"
    return InlineKeyboardMarkup([
        [Btn(toggle, callback_data=f"pipe_toggle:{pid}")],
        [
            Btn(f"{SRC}  {g('Source')}",   callback_data=f"pipe_source:{pid}"),
            Btn(f"{TGT}  {g('Targets')}",  callback_data=f"pipe_targets:{pid}"),
        ],
        [
            Btn(f"{GEAR}  {g('Settings')}",  callback_data=f"pipe_settings:{pid}"),
            Btn(f"{CHART}  {g('Stats')}",    callback_data=f"pipe_stats:{pid}"),
        ],
        [
            Btn(f"{KEY}  {g('Filters')}",    callback_data=f"pipe_filters:{pid}"),
            Btn(f"{CAP}  {g('Caption')}",    callback_data=f"pipe_caption:{pid}"),
        ],
        [
            Btn(f"{SCHED}  {g('Schedule')}", callback_data=f"pipe_schedule:{pid}"),
            Btn(f"{TRANSFORM}  {g('Transform')}", callback_data=f"pipe_transform:{pid}"),
        ],
        [
            Btn(f"{LINK}  {g('Buttons')}",   callback_data=f"pipe_buttons:{pid}"),
            Btn(f"{EXPRT}  {g('Export')}",   callback_data=f"pipe_export:{pid}"),
        ],
        [
            Btn(f"{CLONE}  {g('Clone')}",    callback_data=f"pipe_clone_ask:{pid}"),
        ],
        [
            Btn(f"{EDIT}  {g('Rename')}",    callback_data=f"pipe_rename:{pid}"),
            Btn(f"{TRASH}  {g('Delete')}",   callback_data=f"pipe_delete_ask:{pid}"),
        ],
        [Btn(f"{BACK}  {g('Home')}",         callback_data="home")],
    ])


def pipe_settings(pipe: dict) -> InlineKeyboardMarkup:
    pid   = pipe["pipe_id"]
    hide  = pipe.get("hide_tag", True)
    mf    = pipe.get("media_filter", "all").upper()
    delay = pipe.get("delay", 1.5)
    dedup = pipe.get("dedup", True)
    lim   = pipe.get("fwd_limit", 0)
    rpm   = pipe.get("rate_limit", 20)

    hide_lbl  = f"{OK}  {g('Hide Tag')}"  if hide  else f"{NO}  {g('Hide Tag')}"
    dedup_lbl = f"{OK}  {g('Dedup')}"     if dedup else f"{NO}  {g('Dedup')}"
    wm        = pipe.get("watermark", "")
    dry_run   = pipe.get("dry_run", False)
    dry_lbl   = f"{OK}  {g('Dry Run')}"   if dry_run else f"{NO}  {g('Dry Run')}"

    return InlineKeyboardMarkup([
        [Btn(hide_lbl,                                      callback_data=f"ps_hidetag:{pid}")],
        [Btn(dedup_lbl,                                     callback_data=f"ps_dedup:{pid}")],
        [Btn(dry_lbl,                                       callback_data=f"ps_dryrun:{pid}")],
        [Btn(f"[ {mf} ]  {g('Media Filter')}",             callback_data=f"ps_media:{pid}")],
        [Btn(f"{RATE}  {g('Delay')}: {delay}s",            callback_data=f"ps_delay:{pid}")],
        [Btn(f"{RATE}  {g('Rate Limit')}: {rpm}/min",      callback_data=f"ps_ratelimit:{pid}")],
        [Btn(f"{LIMIT}  {g('Fwd Limit')}: {lim or g('off')}", callback_data=f"ps_limit:{pid}")],
        [Btn(f"[ ]  {g('Min Msg Length')}: {pipe.get('min_length', 0) or g('off')}", callback_data=f"ps_minlen:{pid}")],
        [Btn(f"[ ]  {g('Auto-Delete')}: {str(pipe.get('auto_delete', 0)) + 'min' if pipe.get('auto_delete') else g('off')}", callback_data=f"ps_autodel:{pid}")],
        [Btn(f"[ ]  {g('Watermark')}",                     callback_data=f"ps_watermark:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",                       callback_data=f"pipe_view:{pid}")],
    ])


def media_filter_kb(pipe: dict) -> InlineKeyboardMarkup:
    pid     = pipe["pipe_id"]
    current = pipe.get("media_filter", "all")
    options = ["all", "text", "photo", "video", "document", "audio"]
    rows, row = [], []
    for opt in options:
        label = f"{OK} {opt.upper()}" if current == opt else opt.upper()
        row.append(Btn(label, callback_data=f"ps_mf_set:{pid}:{opt}"))
        if len(row) == 3:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([Btn(f"{BACK}  {g('Back')}", callback_data=f"pipe_settings:{pid}")])
    return InlineKeyboardMarkup(rows)


def filters_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid = pipe["pipe_id"]
    kws = len(pipe.get("keywords", []))
    bls = len(pipe.get("blacklist", []))
    return InlineKeyboardMarkup([
        [Btn(f"{KEY}  {g('Keywords')} ({kws})",   callback_data=f"pipe_keywords:{pid}")],
        [Btn(f"{BAN}  {g('Blacklist')} ({bls})",  callback_data=f"pipe_blacklist:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",              callback_data=f"pipe_view:{pid}")],
    ])


def keywords_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid  = pipe["pipe_id"]
    rows = []
    for kw in pipe.get("keywords", []):
        rows.append([
            Btn(f"{BULLET} {kw}", callback_data="noop"),
            Btn(TRASH,            callback_data=f"kw_rm:{pid}:{kw}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add')}",        callback_data=f"kw_add:{pid}")],
        [Btn(f"{TRASH}  {g('Clear All')}", callback_data=f"kw_clear:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",       callback_data=f"pipe_filters:{pid}")],
    ]
    return InlineKeyboardMarkup(rows)


def blacklist_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid  = pipe["pipe_id"]
    rows = []
    for w in pipe.get("blacklist", []):
        rows.append([
            Btn(f"{CROSS} {w}", callback_data="noop"),
            Btn(TRASH,          callback_data=f"bl_rm:{pid}:{w}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add Word')}",   callback_data=f"bl_add:{pid}")],
        [Btn(f"{TRASH}  {g('Clear All')}", callback_data=f"bl_clear:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",       callback_data=f"pipe_filters:{pid}")],
    ]
    return InlineKeyboardMarkup(rows)


def caption_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid   = pipe["pipe_id"]
    mode  = pipe.get("caption_mode", "original")
    modes = ["original", "prepend", "append", "replace"]
    rows  = []
    for m in modes:
        label = f"{OK}  {m.upper()}" if mode == m else m.upper()
        rows.append([Btn(label, callback_data=f"cap_mode:{pid}:{m}")])
    rows += [
        [Btn(f"[+]  {g('Edit Caption Text')}", callback_data=f"cap_edit:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",           callback_data=f"pipe_view:{pid}")],
    ]
    return InlineKeyboardMarkup(rows)


def schedule_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid     = pipe["pipe_id"]
    sched   = pipe.get("schedule", {})
    enabled = sched.get("enabled", False)
    sh      = sched.get("start_hour", 0)
    eh      = sched.get("end_hour", 23)
    tz      = sched.get("tz", "UTC")
    en_lbl  = f"{OK}  {g('Enabled')}" if enabled else f"{NO}  {g('Disabled')}"
    return InlineKeyboardMarkup([
        [Btn(en_lbl,                                      callback_data=f"sched_toggle:{pid}")],
        [Btn(f"[ {sh:02d}:00 ]  {g('Start Hour')}",      callback_data=f"sched_start:{pid}")],
        [Btn(f"[ {eh:02d}:00 ]  {g('End Hour')}",        callback_data=f"sched_end:{pid}")],
        [Btn(f"[ {tz} ]  {g('Timezone')}",               callback_data=f"sched_tz:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",                     callback_data=f"pipe_view:{pid}")],
    ])


def targets_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid  = pipe["pipe_id"]
    rows = []
    for t in pipe.get("targets", []):
        rows.append([
            Btn(f"{TGT} {t}", callback_data="noop"),
            Btn(TRASH,        callback_data=f"tgt_remove:{pid}:{t}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add Target')}", callback_data=f"tgt_add:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",      callback_data=f"pipe_view:{pid}")],
    ]
    return InlineKeyboardMarkup(rows)


def cmd_list_kb(cmds: list) -> InlineKeyboardMarkup:
    rows = []
    for c in cmds:
        state = OK if c.get("enabled") else NO
        rows.append([
            Btn(f"{state}  /{c['command']}  ({c.get('use_count',0)}x)",
                callback_data=f"cmd_manage:{c['command']}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add Command')}",     callback_data="cmd_add_prompt")],
        [Btn(f"[ ] {g('Schema / Help')}",      callback_data="cmd_schema")],
        [Btn(f"{BACK}  {g('Back')}",           callback_data="home")],
    ]
    return InlineKeyboardMarkup(rows)


def cmd_manage_kb(cmd: dict) -> InlineKeyboardMarkup:
    name    = cmd["command"]
    enabled = cmd.get("enabled", True)
    en_lbl  = f"{OK}  {g('Enabled')}" if enabled else f"{NO}  {g('Disabled')}"
    return InlineKeyboardMarkup([
        [Btn(en_lbl,                               callback_data=f"cmd_toggle:{name}")],
        [Btn(f"[ ]  {g('Test Preview')}",          callback_data=f"cmd_test:{name}")],
        [Btn(f"{TRASH}  {g('Delete')}",            callback_data=f"cmd_delete_ask:{name}")],
        [Btn(f"{BACK}  {g('Commands')}",           callback_data="cmd_list")],
    ])



def owner_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [Btn(f"{ADMIN}  {g('Admin Management')}", callback_data="admin_list")],
        [Btn(f"{LOG}  {g('Activity Log')}",       callback_data="activity_log")],
        [Btn(f"{BROAD}  {g('Broadcast')}",        callback_data="broadcast_prompt")],
        [Btn(f"{CHART}  {g('Global Stats')}",     callback_data="global_stats")],
        [Btn(f"{CIRCLE}  {g('All Pipelines')}",  callback_data="all_pipelines")],
        [Btn(f"{QUEUE}  {g('Queue Status')}",     callback_data="queue_status")],
        [Btn(f"{CHANNELS}  {g('Force-Join Channels')}", callback_data="fj_manage")],
        [Btn(f"{STOP}  {g('Pause All Pipelines')}", callback_data="pause_all_ask")],
        [Btn(f"{RELOAD}  {g('Restart Bot')}",     callback_data="bot_restart_ask")],
        [Btn(f"{BACK}  {g('Home')}",              callback_data="home")],
    ])


def admin_list_kb(admins: list) -> InlineKeyboardMarkup:
    rows = []
    for a in admins:
        icon  = BAN if a.get("is_banned") else ADMIN
        uname = a.get("username") or str(a["user_id"])
        rows.append([
            Btn(f"{icon}  @{uname}", callback_data="noop"),
            Btn(f"{GEAR}",          callback_data=f"admin_manage:{a['user_id']}"),
            Btn(TRASH,              callback_data=f"admin_remove_ask:{a['user_id']}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add Admin')}", callback_data="admin_add_prompt")],
        [Btn(f"{BACK}  {g('Back')}",     callback_data="owner_panel")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_manage_kb(admin: dict) -> InlineKeyboardMarkup:
    uid   = admin["user_id"]
    perms = admin.get("perms", [])
    from vault.store import ALL_PERMS
    rows  = []
    for p in ALL_PERMS:
        has  = p in perms
        lbl  = f"{OK}  {g(p)}" if has else f"{NO}  {g(p)}"
        rows.append([Btn(lbl, callback_data=f"admin_perm_toggle:{uid}:{p}")])
    banned  = admin.get("is_banned", False)
    ban_lbl = f"[+]  {g('Unban')}" if banned else f"{BAN}  {g('Ban')}"
    rows += [
        [Btn(ban_lbl,                 callback_data=f"admin_ban_toggle:{uid}")],
        [Btn(f"{BACK}  {g('Back')}", callback_data="admin_list")],
    ]
    return InlineKeyboardMarkup(rows)


def confirm_kb(yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        Btn(f"{OK}  {g('Yes')}", callback_data=yes_cb),
        Btn(f"{NO}  {g('No')}",  callback_data=no_cb),
    ]])


def pipe_stats_kb(pid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [Btn(f"{TRASH}  {g('Reset Stats')}", callback_data=f"pipe_stats_reset:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",         callback_data=f"pipe_view:{pid}")],
    ])


def back_home() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[Btn(f"{BACK}  {g('Home')}", callback_data="home")]])


def back_pipe(pid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[Btn(f"{BACK}  {g('Back')}", callback_data=f"pipe_view:{pid}")]])


def back_owner() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[Btn(f"{BACK}  {g('Back')}", callback_data="owner_panel")]])


def back_cmds() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[Btn(f"{BACK}  {g('Commands')}", callback_data="cmd_list")]])


def inline_buttons_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid  = pipe["pipe_id"]
    btns = pipe.get("inline_buttons", [])
    rows = []
    for i, b in enumerate(btns):
        label = f"{LINK} {b['text']}  [{b['url'][:30]}...]" if len(b.get('url','')) > 30 else f"{LINK} {b['text']}  [{b.get('url','')}]"
        rows.append([
            Btn(label, callback_data="noop"),
            Btn(TRASH,  callback_data=f"pbtn_remove:{pid}:{i}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add Button')}",    callback_data=f"pbtn_add:{pid}")],
        [Btn(f"{TRASH}  {g('Clear All')}",   callback_data=f"pbtn_clear:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",         callback_data=f"pipe_view:{pid}")],
    ]
    return InlineKeyboardMarkup(rows)


def transform_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid   = pipe["pipe_id"]
    t     = pipe.get("transform", {})
    s     = pipe.get("strip_opts", {})
    regex = OK if t.get("regex_enabled") else NO
    pin   = OK if t.get("pin_forwarded") else NO
    silent= OK if t.get("silent_pin")    else NO
    rm_bt = OK if t.get("remove_buttons") else NO
    invert= OK if t.get("invert_filter") else NO
    strip_m = OK if s.get("mentions")    else NO
    strip_h = OK if s.get("hashtags")    else NO
    fr_count = len(pipe.get("find_replace", []))
    return InlineKeyboardMarkup([
        [Btn(f"{REGEX}  {g('Regex Filter')}: {regex}",   callback_data=f"tr_regex_toggle:{pid}")],
        [Btn(f"[ ]  {g('Set Regex Pattern')}",            callback_data=f"tr_regex_set:{pid}")],
        [Btn(f"{TRANSFORM}  {g('Invert Filter')}: {invert}", callback_data=f"tr_invert:{pid}")],
        [Btn(f"{PIN}  {g('Pin Forwarded')}: {pin}",      callback_data=f"tr_pin_toggle:{pid}")],
        [Btn(f"[ ]  {g('Silent Pin')}: {silent}",        callback_data=f"tr_silent_toggle:{pid}")],
        [Btn(f"{TRASH}  {g('Remove Buttons')}: {rm_bt}", callback_data=f"tr_rmbtn_toggle:{pid}")],
        [
            Btn(f"@  {g('Strip Mentions')}: {strip_m}", callback_data=f"tr_strip_mentions:{pid}"),
            Btn(f"#  {g('Strip Hashtags')}: {strip_h}", callback_data=f"tr_strip_hashtags:{pid}"),
        ],
        [Btn(f"{EDIT}  {g('Find & Replace')} ({fr_count})", callback_data=f"pipe_findreplace:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",                     callback_data=f"pipe_view:{pid}")],
    ])


def findreplace_menu(pipe: dict) -> InlineKeyboardMarkup:
    pid   = pipe["pipe_id"]
    rules = pipe.get("find_replace", [])
    rows  = []
    for r in rules:
        find_str = r.get("find", "")[:20]
        rows.append([
            Btn(f"{BULLET} {find_str}", callback_data="noop"),
            Btn(TRASH, callback_data=f"fr_rm:{pid}:{r.get('find','')}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add Rule')}",    callback_data=f"fr_add:{pid}")],
        [Btn(f"{TRASH}  {g('Clear All')}", callback_data=f"fr_clear:{pid}")],
        [Btn(f"{BACK}  {g('Back')}",       callback_data=f"pipe_transform:{pid}")],
    ]
    return InlineKeyboardMarkup(rows)


def force_join_channels_kb(channels: list, lang: str = "en") -> InlineKeyboardMarkup:
    from wire.i18n import t as _t
    rows = []
    for ch in channels:
        url = f"https://t.me/{ch.lstrip('@')}" if ch.startswith("@") else f"https://t.me/c/{str(ch).lstrip('-100')}/1"
        rows.append([Btn(f"{JOIN}  {_t('Join', lang)} {ch}", url=url)])
    rows.append([Btn(f"{CHECK}  {_t('I have joined — Check', lang)}", callback_data="fj_check")])
    return InlineKeyboardMarkup(rows)


def owner_channels_kb(channels: list) -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        rows.append([
            Btn(f"{CHANNELS}  {ch}", callback_data="noop"),
            Btn(TRASH, callback_data=f"fj_remove:{ch}"),
        ])
    rows += [
        [Btn(f"{ADD}  {g('Add Channel')}", callback_data="fj_add_prompt")],
        [Btn(f"{BACK}  {g('Back')}",       callback_data="owner_panel")],
    ]
    return InlineKeyboardMarkup(rows)
