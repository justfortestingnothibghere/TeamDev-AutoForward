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

_MAP = {
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ',
    'i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ',
    'q':'Q','r':'ʀ','s':'ꜱ','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x',
    'y':'ʏ','z':'ᴢ',
}

def g(text: str) -> str:
    return ''.join(_MAP.get(c.lower(), c) for c in text)


LINE      = "━━━━━━━━━━━━━━"
THIN      = "┄┄┄┄┄┄┄┄┄┄┄"
DOUBLE    = "═════════════"
WAVE      = "〰〰〰〰〰〰〰〰〰〰〰"

DOT       = "◈"
ARR       = "›"
ARR2      = "»"
BULLET    = "▸"
SQUARE    = "▪"
CIRCLE    = "◉"
LOZENGE   = "◆"
STAR      = "✦"
CROSS     = "✖"
PLUS      = "✚"
CHECK     = "✔"
MINUS     = "▬"

TL        = "╔"
TR        = "╗"
BL        = "╚"
BR        = "╝"
LR        = "║"
TB        = "═"

SPARK     = "◈ TᴇᴀᴍDᴇᴠ"
OK        = "✔"
NO        = "✖"
WARN      = "⚑"
INFO      = "◎"
LOCK      = "⊘"
PIPE      = "⇒"
SRC       = "«"
TGT       = "»"
GEAR      = "⚙"
CHART     = "▦"
TRASH     = "⌫"
ADD       = "⊕"
EDIT      = "⌘"
PLAY      = "▶"
STOP      = "■"
PAUSE     = "⏸"
BACK      = "‹"
CROWN     = "◇"
ADMIN     = "◆"
LOG       = "▤"
BROAD     = "◈"
KEY       = "⊞"
BAN       = "⊗"
DUPE      = "⟳"
CAP       = "❝"
LIMIT     = "⊡"
RELOAD    = "↺"
EXPRT     = "▣"
IMPRT     = "▢"
SCHED     = "◷"
CMD       = "/"
QUEUE     = "⊟"
RATE      = "⧖"
ERR       = "⚠"
CLONE     = "⎘"
REGEX     = "⌥"
TRANSFORM = "⇄"
PIN       = "⊳"
JOIN      = "⊕"
CHANNELS  = "◈"
LINK      = "⌁"
