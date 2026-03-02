"""passphrase_generate 工具：基于 xkcdpass 生成助记短语型口令

依赖 xkcdpass 库（pip install xkcdpass），基于 EFF 的 diceware 词表，
生成易于记忆、高安全性的短语口令。
"""
from __future__ import annotations

import math
import secrets

from agent.graph import register_tool
from agent.state import PassAgentState

# 尝试使用 xkcdpass，如果未安装则使用内置词表
try:
    from xkcdpass import xkcd_password as xp
    _WORDLIST = xp.generate_wordlist(wordfile="eff-long", min_length=3, max_length=9)
    _HAS_XKCDPASS = True
except ImportError:
    _HAS_XKCDPASS = False
    # 内置精简词表（EFF long list 摘录 + 常用英语词），保证无外部依赖也能工作
    _BUILTIN_WORDS = [
        "abandon", "ability", "above", "absent", "absorb", "abstract", "absurd",
        "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
        "action", "actor", "actress", "actual", "adapt", "addict", "address",
        "adjust", "admit", "adult", "advance", "advice", "aerobic", "affair",
        "afford", "afraid", "again", "agent", "agree", "ahead", "airport",
        "aisle", "alarm", "album", "alert", "alien", "allow", "almost",
        "alone", "alpha", "already", "alter", "always", "amateur", "amazing",
        "among", "amount", "amused", "anchor", "ancient", "anger", "angle",
        "animal", "annual", "another", "answer", "antenna", "antique", "anxiety",
        "apart", "apology", "appear", "apple", "approve", "april", "arctic",
        "arena", "army", "arrange", "arrest", "arrive", "arrow", "artist",
        "artwork", "aspect", "assault", "asset", "assist", "assume", "asthma",
        "athlete", "atlas", "atom", "attack", "attend", "attract", "auction",
        "audit", "august", "aunt", "author", "autumn", "average", "avocado",
        "banner", "barely", "basket", "battle", "beach", "beauty", "become",
        "before", "begin", "behind", "believe", "below", "bench", "benefit",
        "beyond", "bicycle", "blanket", "blossom", "board", "bonus", "border",
        "bottom", "bounce", "brain", "brave", "breeze", "bridge", "bright",
        "broken", "brother", "brush", "bubble", "budget", "buffalo", "bullet",
        "bundle", "burden", "burger", "butter", "cabin", "cable", "cactus",
        "camera", "cancel", "candle", "canvas", "canyon", "carbon", "carpet",
        "castle", "catalog", "catch", "cattle", "ceiling", "celery", "cement",
        "census", "cereal", "certain", "chair", "chalk", "chamber", "change",
        "chapter", "charge", "chase", "cherry", "chicken", "chief", "chimney",
        "choice", "chunk", "circle", "citizen", "clarify", "claw", "click",
        "climate", "clinic", "clock", "closet", "cloud", "cluster", "coach",
        "coconut", "coffee", "collect", "color", "column", "comfort", "comic",
        "common", "company", "concert", "conduct", "confirm", "connect", "consider",
        "control", "convert", "cookie", "copper", "coral", "corner", "cotton",
        "couch", "country", "couple", "course", "cousin", "cover", "craft",
        "crazy", "cream", "credit", "cricket", "crisp", "critic", "cross",
        "crouch", "crowd", "crucial", "cruel", "cruise", "crumble", "crystal",
        "culture", "current", "curtain", "cushion", "custom", "cycle", "damage",
        "danger", "daring", "daughter", "dawn", "debate", "decade", "decline",
        "decorate", "defense", "define", "degree", "delay", "deliver", "demand",
        "denial", "dentist", "depart", "deposit", "depth", "deputy", "derive",
        "describe", "desert", "design", "detect", "develop", "device", "devote",
        "diamond", "diary", "diesel", "differ", "digital", "dignity", "dilemma",
        "dinner", "dinosaur", "direct", "disease", "display", "distance", "divide",
        "doctor", "dolphin", "domain", "donkey", "donate", "double", "dragon",
        "drastic", "dream", "dress", "drift", "drill", "drink", "drizzle",
        "drum", "during", "dynamic", "eagle", "early", "earth", "easily",
        "economy", "editor", "educate", "effort", "eight", "either", "elbow",
        "elder", "electric", "elegant", "element", "elephant", "elite", "embark",
        "embrace", "emerge", "emotion", "employ", "empower", "empty", "enable",
        "endless", "energy", "enforce", "engage", "engine", "enjoy", "enough",
        "enrich", "ensure", "entire", "entry", "envelope", "episode", "equal",
        "equip", "erode", "erosion", "error", "erupt", "escape", "essay",
        "essence", "estate", "eternal", "evoke", "evolve", "exact", "example",
        "excess", "exclude", "excite", "excuse", "execute", "exhaust", "exhibit",
        "exist", "expand", "expect", "expire", "explain", "expose", "express",
        "extend", "extra", "eyebrow", "fabric", "faculty", "faint", "faith",
        "family", "famous", "fancy", "fantasy", "fashion", "father", "fatigue",
        "favorite", "feature", "federal", "female", "fence", "festival", "fetch",
        "fiction", "filter", "final", "finger", "finish", "flame", "flavor",
        "flight", "floor", "flower", "fluid", "flush", "focus", "follow",
        "forest", "forget", "fortune", "foster", "found", "fragile", "frame",
        "frozen", "fruit", "gadget", "galaxy", "gallery", "garden", "garlic",
        "garment", "gather", "general", "genius", "gentle", "genuine", "gesture",
        "giant", "ginger", "giraffe", "glance", "glimpse", "globe", "glory",
        "goat", "goddess", "gospel", "gossip", "govern", "grace", "grain",
        "grant", "grape", "gravity", "green", "grocery", "group", "guitar",
        "habit", "hammer", "hamster", "harbor", "harvest", "hazard", "health",
        "heart", "heavy", "hedgehog", "height", "helmet", "hidden", "highway",
        "history", "hobby", "hockey", "hollow", "honest", "holiday", "horror",
        "horse", "hospital", "hotel", "hover", "humble", "humor", "hundred",
        "hungry", "hurdle", "hybrid", "icon", "idea", "identify", "ignore",
        "illness", "image", "immune", "impact", "impose", "impulse", "include",
        "income", "index", "indicate", "indoor", "infant", "inflict", "inform",
        "inherit", "initial", "inject", "inmate", "inner", "innocent", "insane",
        "insect", "inside", "inspire", "install", "intact", "interest", "invest",
        "invite", "island", "isolate", "ivory", "jacket", "jaguar", "jelly",
        "jewel", "journey", "judge", "jungle", "junior", "junk", "justice",
        "kangaroo", "kidney", "kingdom", "kitchen", "kiwi", "knife", "label",
        "ladder", "laundry", "layer", "leader", "lecture", "legend", "leisure",
        "lemon", "length", "leopard", "lesson", "letter", "liberty", "library",
        "license", "light", "limit", "linger", "liquid", "little", "lizard",
        "lobby", "local", "lonely", "lounge", "lumber", "lunar", "luxury",
        "machine", "magic", "magnet", "mammal", "manage", "mandate", "mansion",
        "margin", "marine", "market", "master", "matrix", "matter", "meadow",
        "measure", "media", "melody", "member", "memory", "mention", "mentor",
        "mercy", "merit", "method", "middle", "million", "mineral", "minimum",
        "miracle", "mirror", "misery", "mistake", "mixture", "mobile", "model",
        "modify", "moment", "monitor", "monkey", "monster", "morning", "mosquito",
        "mother", "motion", "mountain", "mouse", "movie", "multiply", "muscle",
        "museum", "mushroom", "mutual", "mystery", "narrow", "nasty", "nation",
        "nature", "navigate", "neglect", "neither", "nephew", "nervous", "network",
        "neutral", "noble", "nominee", "normal", "notable", "nothing", "notice",
        "nuclear", "number", "nurse", "observe", "obtain", "obvious", "occur",
        "officer", "olive", "olympic", "opinion", "oppose", "option", "orange",
        "orbit", "orchard", "ordinary", "organ", "orient", "orphan", "ostrich",
        "outdoor", "output", "outside", "owner", "oxygen", "oyster", "palace",
        "palm", "pancake", "panda", "panel", "panic", "panther", "parade",
        "parent", "parrot", "partner", "patrol", "pattern", "pause", "peanut",
        "peasant", "pelican", "penalty", "pencil", "pepper", "perfect", "permit",
        "person", "phrase", "piano", "picnic", "picture", "pilot", "pioneer",
        "pistol", "planet", "plastic", "platter", "player", "pledge", "pluck",
        "plunge", "pocket", "poetry", "polar", "polite", "popular", "portion",
        "poverty", "powder", "power", "praise", "predict", "prepare", "present",
        "pretty", "prevent", "primary", "print", "priority", "prison", "private",
        "problem", "process", "produce", "program", "project", "promote", "prosper",
        "protect", "provide", "public", "pudding", "pumpkin", "punch", "pupil",
        "purchase", "purple", "purpose", "puzzle", "pyramid", "quality", "quantum",
        "quarter", "question", "quiz", "quote", "rabbit", "raccoon", "radar",
        "random", "range", "rapid", "rather", "raven", "reason", "rebel",
        "recipe", "record", "recycle", "reform", "region", "regret", "regular",
        "reject", "relief", "remain", "remember", "remind", "remove", "render",
        "renew", "repair", "repeat", "replace", "report", "require", "rescue",
        "resemble", "resist", "resource", "respond", "result", "retire", "retreat",
        "return", "reunion", "reveal", "review", "reward", "rhythm", "ribbon",
        "rifle", "ritual", "river", "rocket", "romance", "rooster", "royal",
        "rubber", "runway", "rural", "saddle", "sadness", "safety", "salmon",
        "salon", "sample", "satisfy", "sauce", "sausage", "scatter", "scene",
        "scheme", "scissors", "scorpion", "script", "search", "season", "secret",
        "section", "segment", "select", "senior", "sense", "sentence", "series",
        "session", "settle", "shadow", "shallow", "shelter", "sheriff", "shield",
        "shock", "shoulder", "shuffle", "sibling", "siege", "silent", "silver",
        "similar", "simple", "since", "siren", "sister", "situate", "sketch",
        "skill", "slender", "slice", "slogan", "smooth", "snack", "snake",
        "snow", "soccer", "social", "soldier", "solution", "someone", "spirit",
        "sponsor", "spoon", "spray", "spread", "squeeze", "stadium", "staff",
        "stand", "start", "steak", "stereo", "sticky", "stomach", "stone",
        "story", "strategy", "street", "strike", "strong", "struggle", "student",
        "study", "stumble", "style", "subject", "submit", "subway", "success",
        "sudden", "suffer", "suggest", "summer", "sunburn", "sunset", "super",
        "supply", "supreme", "surface", "surge", "surprise", "surround", "survey",
        "suspect", "sustain", "swallow", "swamp", "symbol", "symptom", "system",
        "tackle", "talent", "target", "tattoo", "taxi", "teacher", "temple",
        "tenant", "tender", "tennis", "terminal", "test", "there", "therapy",
        "thought", "three", "thrive", "thunder", "ticket", "timber", "tissue",
        "toast", "tobacco", "today", "toilet", "tomato", "tongue", "tonight",
        "topple", "tornado", "tortoise", "total", "tourist", "toward", "tower",
        "traffic", "tragedy", "train", "transfer", "trash", "travel", "treat",
        "trend", "trial", "trigger", "triple", "trophy", "trouble", "truck",
        "truly", "trumpet", "trust", "tumble", "tunnel", "turkey", "turtle",
        "twenty", "twice", "typical", "ugly", "unable", "uncle", "under",
        "unfair", "unfold", "unhappy", "uniform", "unique", "unit", "universe",
        "unknown", "unlock", "unusual", "unveil", "update", "upgrade", "uphold",
        "upper", "upset", "urban", "useful", "useless", "usual", "utility",
        "vacant", "vacuum", "valley", "valve", "vanish", "various", "venture",
        "verify", "version", "veteran", "viable", "victory", "village", "vintage",
        "violin", "virtual", "visible", "vision", "visit", "visual", "vital",
        "vivid", "vocal", "voice", "volcano", "volume", "voyage", "waffle",
        "wagon", "walnut", "wander", "warfare", "warrior", "wealth", "weapon",
        "weather", "wedding", "weekend", "welcome", "western", "whale", "wheat",
        "whisper", "widen", "width", "window", "winter", "wisdom", "witness",
        "wonder", "world", "worry", "worthy", "wrestle", "write", "yellow",
        "young", "youth", "zebra", "zero", "zombie",
    ]


def generate_passphrase(
    word_count: int = 4,
    separator: str = "-",
    capitalize: bool = False,
    add_number: bool = False,
) -> dict:
    """生成助记短语型口令。"""
    if _HAS_XKCDPASS:
        words = xp.generate_xkcdpassword(_WORDLIST, numwords=word_count, delimiter=" ").split()
    else:
        words = [secrets.choice(_BUILTIN_WORDS) for _ in range(word_count)]

    if capitalize:
        words = [w.capitalize() for w in words]

    if add_number:
        words.append(str(secrets.randbelow(100)))

    passphrase = separator.join(words)

    # 计算熵值
    pool_size = len(_WORDLIST) if _HAS_XKCDPASS else len(_BUILTIN_WORDS)
    entropy = round(word_count * math.log2(pool_size), 1)

    return {
        "passphrase": passphrase,
        "word_count": word_count,
        "separator": separator,
        "length": len(passphrase),
        "entropy_bits": entropy,
        "wordlist_size": pool_size,
    }


@register_tool("passphrase_generate")
async def passphrase_generate_tool(state: PassAgentState) -> dict:
    """生成助记短语型口令。"""
    params = state.get("action_params", {})
    word_count = params.get("word_count", 4)
    separator = params.get("separator", "-")

    # 生成多个候选
    candidates = []
    for capitalize, add_num in [(False, False), (True, False), (True, True)]:
        result = generate_passphrase(
            word_count=word_count,
            separator=separator,
            capitalize=capitalize,
            add_number=add_num,
        )
        candidates.append(result)

    return {
        "_tool_result": {
            "candidates": candidates,
            "count": len(candidates),
            "using_xkcdpass": _HAS_XKCDPASS,
        }
    }
