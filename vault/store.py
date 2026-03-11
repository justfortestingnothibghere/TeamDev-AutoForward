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

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument, DESCENDING
from datetime import datetime, timezone
import environ

_client = None
_db     = None


async def connect():
    global _client, _db
    _client = AsyncIOMotorClient(environ.MONGO_URI)
    _db     = _client["TeamDev"]
    await _db.pipelines.create_index("pipe_id")
    await _db.pipelines.create_index("owner")
    await _db.admins.create_index("user_id", unique=True)
    await _db.activity_log.create_index("ts", expireAfterSeconds=2592000)
    await _db.seen_messages.create_index("key", unique=True)
    await _db.seen_messages.create_index("ts", expireAfterSeconds=604800)
    await _db.custom_commands.create_index("command", unique=True)
    await _db.custom_commands.create_index("owner")

async def get_force_join_channels() -> list[str]:
    doc = await _db.settings.find_one({"_id": "force_join"})
    return doc.get("channels", []) if doc else []


async def add_force_join_channel(channel: str) -> list[str]:
    await _db.settings.update_one(
        {"_id": "force_join"},
        {"$addToSet": {"channels": channel}},
        upsert=True
    )
    return await get_force_join_channels()


async def remove_force_join_channel(channel: str) -> list[str]:
    await _db.settings.update_one(
        {"_id": "force_join"},
        {"$pull": {"channels": channel}}
    )
    return await get_force_join_channels()


def _now() -> datetime:
    return datetime.now(timezone.utc)

class Perm:
    PIPELINES = "pipelines"
    BROADCAST = "broadcast"
    EXPORT    = "export"
    COMMANDS  = "commands"

ALL_PERMS = [Perm.PIPELINES, Perm.BROADCAST, Perm.EXPORT, Perm.COMMANDS]

async def add_admin(user_id: int, username: str, perms: list) -> dict:
    doc = {
        "user_id":  user_id,
        "username": username,
        "perms":    perms,
        "added_at": _now(),
        "added_by": environ.OWNER_ID,
        "is_banned": False,
    }
    await _db.admins.update_one({"user_id": user_id}, {"$set": doc}, upsert=True)
    return doc


async def remove_admin(user_id: int) -> bool:
    r = await _db.admins.delete_one({"user_id": user_id})
    return r.deleted_count > 0


async def get_admin(user_id: int) -> dict | None:
    return await _db.admins.find_one({"user_id": user_id})


async def get_all_admins() -> list[dict]:
    return await _db.admins.find().to_list(None)


async def update_admin_perms(user_id: int, perms: list) -> dict | None:
    return await _db.admins.find_one_and_update(
        {"user_id": user_id},
        {"$set": {"perms": perms}},
        return_document=ReturnDocument.AFTER
    )


async def ban_admin(user_id: int) -> bool:
    r = await _db.admins.update_one({"user_id": user_id}, {"$set": {"is_banned": True}})
    return r.modified_count > 0


async def unban_admin(user_id: int) -> bool:
    r = await _db.admins.update_one({"user_id": user_id}, {"$set": {"is_banned": False}})
    return r.modified_count > 0


async def is_authorized(user_id: int) -> bool:
    if user_id == environ.OWNER_ID:
        return True
    a = await get_admin(user_id)
    return bool(a and not a.get("is_banned"))


async def has_perm(user_id: int, perm: str) -> bool:
    if user_id == environ.OWNER_ID:
        return True
    a = await get_admin(user_id)
    if not a or a.get("is_banned"):
        return False
    return perm in a.get("perms", [])

async def _next_pipe_id(owner_id: int) -> int:
    count = await _db.pipelines.count_documents({"owner": owner_id})
    return count + 1


async def create_pipeline(owner_id: int, name: str) -> dict:
    pipe_id = await _next_pipe_id(owner_id)
    doc = {
        "pipe_id":       pipe_id,
        "owner":         owner_id,
        "name":          name,
        "active":        False,
        "source":        None,
        "targets":       [],
        "hide_tag":      True,
        "media_filter":  "all",
        "delay":         1.5,
        "keywords":      [],
        "blacklist":     [],
        "caption_mode":  "original",
        "caption_text":  "",
        "schedule":      {"enabled": False, "start_hour": 0, "end_hour": 23, "tz": "UTC"},
        "dedup":         True,
        "fwd_limit":     0,
        "rate_limit":    environ.RATE_LIMIT,
        "stats":         {"forwarded": 0, "skipped": 0, "deduped": 0, "errors": 0},
        "created_at":    _now(),
        "updated_at":    _now(),
    }
    await _db.pipelines.insert_one(doc)
    doc.pop("_id", None)
    return doc


async def get_pipeline(owner_id: int, pipe_id: int) -> dict | None:
    d = await _db.pipelines.find_one({"owner": owner_id, "pipe_id": pipe_id})
    if d: d.pop("_id", None)
    return d


async def get_all_pipelines(owner_id: int) -> list[dict]:
    cur  = _db.pipelines.find({"owner": owner_id}).sort("pipe_id", 1)
    docs = await cur.to_list(None)
    for d in docs: d.pop("_id", None)
    return docs


async def get_all_pipelines_global() -> list[dict]:
    docs = await _db.pipelines.find().sort("owner", 1).to_list(None)
    for d in docs: d.pop("_id", None)
    return docs


async def get_active_pipelines() -> list[dict]:
    cur  = _db.pipelines.find({"active": True, "source": {"$ne": None}})
    docs = await cur.to_list(None)
    for d in docs: d.pop("_id", None)
    return docs


async def update_pipeline(owner_id: int, pipe_id: int, **fields) -> dict | None:
    fields["updated_at"] = _now()
    d = await _db.pipelines.find_one_and_update(
        {"owner": owner_id, "pipe_id": pipe_id},
        {"$set": fields},
        return_document=ReturnDocument.AFTER
    )
    if d: d.pop("_id", None)
    return d


async def delete_pipeline(owner_id: int, pipe_id: int) -> bool:
    r = await _db.pipelines.delete_one({"owner": owner_id, "pipe_id": pipe_id})
    return r.deleted_count > 0


async def toggle_pipeline(owner_id: int, pipe_id: int) -> dict | None:
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    return await update_pipeline(owner_id, pipe_id, active=not p["active"])


async def clone_pipeline(owner_id: int, source: dict, new_name: str) -> dict:
    new_id  = await _next_pipe_id(owner_id)
    import copy
    clone   = copy.deepcopy(source)
    clone.pop("_id", None)
    clone["pipe_id"]    = new_id
    clone["name"]       = new_name
    clone["active"]     = False
    clone["stats"]      = {"forwarded": 0, "skipped": 0, "deduped": 0, "errors": 0}
    clone["created_at"] = _now()
    clone["updated_at"] = _now()
    await _db.pipelines.insert_one(clone)
    clone.pop("_id", None)
    return clone


async def add_target(owner_id: int, pipe_id: int, target: str) -> dict | None:
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    t = p.get("targets", [])
    if target not in t:
        t.append(target)
    return await update_pipeline(owner_id, pipe_id, targets=t)


async def remove_target(owner_id: int, pipe_id: int, target: str) -> dict | None:
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    return await update_pipeline(owner_id, pipe_id, targets=[x for x in p["targets"] if x != target])



async def add_inline_button(owner_id: int, pipe_id: int, text: str, url: str):
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    btns = p.get("inline_buttons", [])
    if not any(b["url"] == url for b in btns):
        btns.append({"text": text, "url": url})
    return await update_pipeline(owner_id, pipe_id, inline_buttons=btns)


async def remove_inline_button(owner_id: int, pipe_id: int, idx: int):
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    btns = p.get("inline_buttons", [])
    if 0 <= idx < len(btns):
        btns.pop(idx)
    return await update_pipeline(owner_id, pipe_id, inline_buttons=btns)


async def clear_inline_buttons(owner_id: int, pipe_id: int):
    return await update_pipeline(owner_id, pipe_id, inline_buttons=[])


async def add_keyword(owner_id: int, pipe_id: int, kw: str) -> dict | None:
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    kws = p.get("keywords", [])
    if kw.lower() not in [k.lower() for k in kws]:
        kws.append(kw)
    return await update_pipeline(owner_id, pipe_id, keywords=kws)


async def clear_keywords(owner_id: int, pipe_id: int) -> dict | None:
    return await update_pipeline(owner_id, pipe_id, keywords=[])


async def add_blacklist(owner_id: int, pipe_id: int, word: str) -> dict | None:
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    bl = p.get("blacklist", [])
    if word.lower() not in [b.lower() for b in bl]:
        bl.append(word)
    return await update_pipeline(owner_id, pipe_id, blacklist=bl)


async def clear_blacklist(owner_id: int, pipe_id: int) -> dict | None:
    return await update_pipeline(owner_id, pipe_id, blacklist=[])


async def add_find_replace(owner_id: int, pipe_id: int, find: str, replace: str) -> dict | None:
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    rules = p.get("find_replace", [])
    rules = [r for r in rules if r.get("find") != find]
    rules.append({"find": find, "replace": replace})
    return await update_pipeline(owner_id, pipe_id, find_replace=rules)


async def remove_find_replace(owner_id: int, pipe_id: int, find: str) -> dict | None:
    p = await get_pipeline(owner_id, pipe_id)
    if not p: return None
    rules = [r for r in p.get("find_replace", []) if r.get("find") != find]
    return await update_pipeline(owner_id, pipe_id, find_replace=rules)


async def clear_find_replace(owner_id: int, pipe_id: int) -> dict | None:
    return await update_pipeline(owner_id, pipe_id, find_replace=[])


async def bump_stat(pipe_id: int, owner: int, field: str):
    await _db.pipelines.update_one(
        {"pipe_id": pipe_id, "owner": owner},
        {"$inc": {f"stats.{field}": 1}}
    )


async def reset_stats(owner_id: int, pipe_id: int) -> dict | None:
    return await update_pipeline(owner_id, pipe_id,
        stats={"forwarded": 0, "skipped": 0, "deduped": 0, "errors": 0})


async def is_seen(pipe_id: int, msg_id: int) -> bool:
    return bool(await _db.seen_messages.find_one({"key": f"{pipe_id}:{msg_id}"}))


async def mark_seen(pipe_id: int, msg_id: int):
    key = f"{pipe_id}:{msg_id}"
    await _db.seen_messages.update_one(
        {"key": key},
        {"$set": {"key": key, "ts": _now()}},
        upsert=True
    )

async def set_command(owner_id: int, command: str, payload: dict) -> dict:
    cmd  = command.lstrip("/").lower()
    doc  = {
        "command":    cmd,
        "owner":      owner_id,
        "payload":    payload,
        "enabled":    payload.get("enabled", True),
        "use_count":  0,
        "created_at": _now(),
        "updated_at": _now(),
    }
    await _db.custom_commands.update_one(
        {"command": cmd},
        {"$set": doc},
        upsert=True
    )
    return doc


async def get_command(command: str) -> dict | None:
    cmd = command.lstrip("/").lower()
    return await _db.custom_commands.find_one({"command": cmd})


async def get_all_commands(owner_id: int | None = None) -> list[dict]:
    q = {"owner": owner_id} if owner_id else {}
    docs = await _db.custom_commands.find(q).sort("command", 1).to_list(None)
    for d in docs: d.pop("_id", None)
    return docs


async def delete_command(command: str) -> bool:
    r = await _db.custom_commands.delete_one({"command": command.lstrip("/").lower()})
    return r.deleted_count > 0


async def toggle_command(command: str) -> dict | None:
    cmd = command.lstrip("/").lower()
    c   = await get_command(cmd)
    if not c: return None
    new_state = not c.get("enabled", True)
    return await _db.custom_commands.find_one_and_update(
        {"command": cmd},
        {"$set": {"enabled": new_state, "updated_at": _now()}},
        return_document=ReturnDocument.AFTER
    )


async def bump_cmd_use(command: str):
    await _db.custom_commands.update_one(
        {"command": command.lstrip("/").lower()},
        {"$inc": {"use_count": 1}}
    )


async def bulk_import_commands(owner_id: int, commands: list[dict]) -> tuple[int, int]:
    ok, skip = 0, 0
    for item in commands:
        try:
            cmd = item.get("command", "").lstrip("/").lower()
            if not cmd:
                skip += 1; continue
            payload = {
                "text":       item.get("text", ""),
                "parse_mode": item.get("parse_mode", "html"),
                "photo":      item.get("photo"),
                "video":      item.get("video"),
                "buttons":    item.get("buttons", []),
                "enabled":    item.get("enabled", True),
            }
            await set_command(owner_id, cmd, payload)
            ok += 1
        except Exception:
            skip += 1
    return ok, skip

async def log_activity(user_id: int, action: str, detail: str = ""):
    await _db.activity_log.insert_one({
        "user_id": user_id,
        "action":  action,
        "detail":  detail,
        "ts":      _now(),
    })


async def get_activity_log(limit: int = 30, user_id: int = None) -> list[dict]:
    q   = {"user_id": user_id} if user_id else {}
    cur = _db.activity_log.find(q).sort("ts", DESCENDING).limit(limit)
    docs = await cur.to_list(None)
    for d in docs: d.pop("_id", None)
    return docs


async def global_stats() -> dict:
    pipes  = await _db.pipelines.find().to_list(None)
    admins = await _db.admins.count_documents({})
    cmds   = await _db.custom_commands.count_documents({})
    return {
        "total_pipes":  len(pipes),
        "active_pipes": sum(1 for p in pipes if p.get("active")),
        "total_users":  len(set(p["owner"] for p in pipes)),
        "total_admins": admins,
        "total_cmds":   cmds,
        "forwarded":    sum(p.get("stats", {}).get("forwarded", 0) for p in pipes),
        "skipped":      sum(p.get("stats", {}).get("skipped",   0) for p in pipes),
        "deduped":      sum(p.get("stats", {}).get("deduped",   0) for p in pipes),
        "errors":       sum(p.get("stats", {}).get("errors",    0) for p in pipes),
    }


_sessions: dict = {}


def set_session(uid: int, state: str, **data):
    _sessions[uid] = {"state": state, "data": data}


def get_session(uid: int) -> dict | None:
    return _sessions.get(uid)


def clear_session(uid: int):
    _sessions.pop(uid, None)

async def get_user_lang(uid: int) -> str:
    doc = await _db.user_prefs.find_one({"user_id": uid}, {"lang": 1})
    return doc.get("lang", "en") if doc else "en"


async def set_user_lang(uid: int, lang: str) -> None:
    await _db.user_prefs.update_one(
        {"user_id": uid},
        {"$set": {"user_id": uid, "lang": lang, "updated_at": _now()}},
        upsert=True,
    )
