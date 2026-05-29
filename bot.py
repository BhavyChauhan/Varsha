"""
╔══════════════════════════════════════════════════════════════╗
║           VARSHA 2.0 — TELEGRAM SUPERBOT                     ║
║   AI • RPG • Music • Image • Voice • Economy • Mafia         ║
╚══════════════════════════════════════════════════════════════╝
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IMPORTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import asyncio
import logging
import os
import random
import re
import sqlite3
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO

import aiohttp
import cv2
import numpy as np
import requests
import yt_dlp
from groq import Groq
from PIL import Image, ImageEnhance, ImageFilter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from rembg import remove as rembg_remove

from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery)

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import subprocess

import os

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"

import os
#os.system("ffmpeg -version")


# TTS — try edge-tts first, fall back to gtts
try:
    import edge_tts
    TTS_ENGINE = "edge"
except ImportError:
    from gtts import gTTS
    TTS_ENGINE = "gtts"


ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "song.%(ext)s",

    "ffmpeg_location": r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin",

    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }]
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION  — Replace with your real keys
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API_ID           = int(os.getenv("API_ID", "24146994"))
API_HASH         = os.getenv("API_HASH", "66e1cbb26e8925049b2dda8f1ad66a02")
BOT_TOKEN        = os.getenv("BOT_TOKEN", "8631994682:AAHEy1lBpXTb5D5S0D-hpEjjBZ23u7eAeeA")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "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")
HF_API_KEY       = os.getenv("HF_API_KEY", "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")   # Hugging Face for images
GENIUS_TOKEN     = os.getenv("GENIUS_TOKEN", "NyrMmKiy0yq2ky8qMOPMGUsNBOUVKry6Z2VjuPTGRl6mR4yoRJJKq84zDAW2l99g")  # optional for lyrics

DB_PATH   = "varsha.db"
TEMP_DIR  = tempfile.gettempdir()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("VARSHA")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ITEM CATALOGUE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ITEMS: dict[str, dict] = {
    # 🐶 PETS
    "ᴅᴏɢ":              {"price": 1_000,       "emoji": "🐶", "category": "pets"},
    "ᴄᴀᴛ":              {"price": 1_000,       "emoji": "🐱", "category": "pets"},
    "ᴡᴏʟғ":             {"price": 4_000,       "emoji": "🐺", "category": "pets"},
    "ᴛɪɢᴇʀ":            {"price": 10_000,      "emoji": "🐯", "category": "pets"},
    "ᴅʀᴀɢᴏɴ":           {"price": 50_000,      "emoji": "🐉", "category": "pets"},
    # 🔔 UTILITY
    "ʙᴇʟʟ":             {"price": 2_000,       "emoji": "🔔", "category": "utility"},
    "ᴍᴇᴅᴋɪᴛ":           {"price": 3_000,       "emoji": "🩺", "category": "utility"},
    "sʜɪᴇʟᴅ":           {"price": 5_000,       "emoji": "🛡️", "category": "utility"},
    "ʀᴇᴠɪᴠᴇ ᴛᴏᴋᴇɴ":     {"price": 7_000,       "emoji": "💊", "category": "utility"},
    # 🚗 VEHICLES
    "ʙɪᴋᴇ":             {"price": 7_000,       "emoji": "🏍️", "category": "vehicles"},
    "sᴘᴏʀᴛs ᴄᴀʀ":       {"price": 25_000,      "emoji": "🏎️", "category": "vehicles"},
    "ʟᴜxᴜʀʏ ᴄᴀʀ":       {"price": 50_000,      "emoji": "🚗", "category": "vehicles"},
    "ʜᴇʟɪᴄᴏᴘᴛᴇʀ":       {"price": 120_000,     "emoji": "🚁", "category": "vehicles"},
    "ᴘʀɪᴠᴀᴛᴇ ᴊᴇᴛ":      {"price": 500_000,     "emoji": "✈️", "category": "vehicles"},
    # 🏠 PROPERTY
    "sᴍᴀʟʟ ʜᴏᴜsᴇ":      {"price": 15_000,      "emoji": "🏠", "category": "property"},
    "ᴠɪʟʟᴀ":            {"price": 100_000,     "emoji": "🏡", "category": "property"},
    "ᴍᴀɴsɪᴏɴ":          {"price": 500_000,     "emoji": "🏰", "category": "property"},
    "ɪsʟᴀɴᴅ":           {"price": 5_000_000,   "emoji": "🏝️", "category": "property"},
    # 🔫 WEAPONS
    "ᴋɴɪғᴇ":            {"price": 5_000,       "emoji": "🔪", "category": "weapons"},
    "ᴘɪsᴛᴏʟ":           {"price": 15_000,      "emoji": "🔫", "category": "weapons"},
    "ᴀᴋ𝟺𝟽":             {"price": 50_000,      "emoji": "⚔️",  "category": "weapons"},
    "sɴɪᴘᴇʀ":           {"price": 100_000,     "emoji": "🎯", "category": "weapons"},
    "ʙᴀᴢᴜᴋᴀ":           {"price": 500_000,     "emoji": "🚀", "category": "weapons"},
    # 💎 RARE
    "ᴅɪᴀᴍᴏɴᴅ ʀɪɴɢ":     {"price": 75_000,      "emoji": "💍", "category": "rare"},
    "ᴄʀᴏᴡɴ":            {"price": 300_000,     "emoji": "👑", "category": "rare"},
    "ᴍᴀғɪᴀ ᴛʜʀᴏɴᴇ":     {"price": 1_000_000,   "emoji": "🪑", "category": "rare"},
}

CATEGORY_EMOJI = {
    "pets": "🐶 PETS",
    "utility": "🔔 UTILITY",
    "vehicles": "🚗 VEHICLES",
    "property": "🏠 PROPERTY",
    "weapons": "🔫 WEAPONS",
    "rare": "💎 RARE",
}

TITLE_TIERS = [
    (0,   "🌱 𝐍𝐎𝐎𝐁"),
    (5,   "💀 𝐊𝐈𝐋𝐋𝐄𝐑"),
    (15,  "🔥 𝐄𝐋𝐈𝐓𝐄 𝐇𝐔𝐍𝐓𝐄𝐑"),
    (30,  "🗡️ 𝐀𝐒𝐒𝐀𝐒𝐒𝐈𝐍 𝐋𝐎𝐑𝐃"),
    (50,  "👑 𝐌𝐀𝐅𝐈𝐀 𝐊𝐈𝐍𝐆"),
]

def get_title(kills: int) -> str:
    title = TITLE_TIERS[0][1]
    for threshold, t in TITLE_TIERS:
        if kills >= threshold:
            title = t
    return title

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE LAYER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db() -> None:
    """Create all tables on startup."""
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            name        TEXT    DEFAULT 'Unknown',
            coins       INTEGER DEFAULT 1000,
            kills       INTEGER DEFAULT 0,
            deaths      INTEGER DEFAULT 0,
            alive       INTEGER DEFAULT 1,
            protected   INTEGER DEFAULT 0,
            protect_until INTEGER DEFAULT 0,
            streak      INTEGER DEFAULT 0,
            last_daily  INTEGER DEFAULT 0,
            created_at  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            item        TEXT    NOT NULL,
            qty         INTEGER DEFAULT 1,
            UNIQUE(user_id, item)
        );

        CREATE TABLE IF NOT EXISTS bounties (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id   INTEGER NOT NULL,
            placer_id   INTEGER NOT NULL,
            amount      INTEGER NOT NULL,
            placed_at   INTEGER NOT NULL,
            active      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id     INTEGER NOT NULL,
            cmd         TEXT    NOT NULL,
            last_used   INTEGER NOT NULL,
            PRIMARY KEY (user_id, cmd)
        );
    """)
    conn.commit()
    conn.close()
    log.info("✅ Database initialised")


# ── user helpers ────────────────────────────────────────────

def ensure_user(user_id: int, name: str = "Unknown") -> None:
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, name, created_at) VALUES (?,?,?)",
        (user_id, name, int(time.time())),
    )
    conn.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id))
    conn.commit()
    conn.close()


def get_user(user_id: int) -> sqlite3.Row | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row


def update_coins(user_id: int, delta: int) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE users SET coins = MAX(0, coins + ?) WHERE user_id=?",
        (delta, user_id),
    )
    conn.commit()
    conn.close()


def set_field(user_id: int, field: str, value) -> None:
    conn = get_conn()
    conn.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
    conn.commit()
    conn.close()


def world_rank(user_id: int) -> int:
    conn = get_conn()
    rows = conn.execute(
        "SELECT user_id FROM users ORDER BY coins DESC"
    ).fetchall()
    conn.close()
    for i, r in enumerate(rows, 1):
        if r["user_id"] == user_id:
            return i
    return 0

# ── inventory helpers ────────────────────────────────────────

def inv_add(user_id: int, item: str, qty: int = 1) -> None:
    conn = get_conn()
    conn.execute(
        """INSERT INTO inventory (user_id, item, qty) VALUES (?,?,?)
           ON CONFLICT(user_id, item) DO UPDATE SET qty = qty + ?""",
        (user_id, item, qty, qty),
    )
    conn.commit()
    conn.close()


def inv_remove(user_id: int, item: str, qty: int = 1) -> bool:
    """Returns True if removal succeeded."""
    conn = get_conn()
    row = conn.execute(
        "SELECT qty FROM inventory WHERE user_id=? AND item=?", (user_id, item)
    ).fetchone()
    if not row or row["qty"] < qty:
        conn.close()
        return False
    new_qty = row["qty"] - qty
    if new_qty <= 0:
        conn.execute(
            "DELETE FROM inventory WHERE user_id=? AND item=?", (user_id, item)
        )
    else:
        conn.execute(
            "UPDATE inventory SET qty=? WHERE user_id=? AND item=?",
            (new_qty, user_id, item),
        )
    conn.commit()
    conn.close()
    return True


def get_inventory(user_id: int) -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT item, qty FROM inventory WHERE user_id=? ORDER BY item",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


# ── cooldown helpers ─────────────────────────────────────────

def check_cooldown(user_id: int, cmd: str, seconds: int) -> int:
    """Returns remaining seconds, 0 if OK."""
    conn = get_conn()
    row = conn.execute(
        "SELECT last_used FROM cooldowns WHERE user_id=? AND cmd=?", (user_id, cmd)
    ).fetchone()
    conn.close()
    if not row:
        return 0
    elapsed = int(time.time()) - row["last_used"]
    return max(0, seconds - elapsed)


def set_cooldown(user_id: int, cmd: str) -> None:
    conn = get_conn()
    conn.execute(
        """INSERT INTO cooldowns (user_id, cmd, last_used) VALUES (?,?,?)
           ON CONFLICT(user_id, cmd) DO UPDATE SET last_used=?""",
        (user_id, cmd, int(time.time()), int(time.time())),
    )
    conn.commit()
    conn.close()


# ── bounty helpers ───────────────────────────────────────────

def get_active_bounty(target_id: int) -> sqlite3.Row | None:
    conn = get_conn()
    cutoff = int(time.time()) - 7 * 86400
    row = conn.execute(
        "SELECT * FROM bounties WHERE target_id=? AND active=1 AND placed_at>? ORDER BY amount DESC LIMIT 1",
        (target_id, cutoff),
    ).fetchone()
    conn.close()
    return row


def claim_bounty(target_id: int) -> int:
    """Returns total claimed amount."""
    conn = get_conn()
    cutoff = int(time.time()) - 7 * 86400
    rows = conn.execute(
        "SELECT id, amount FROM bounties WHERE target_id=? AND active=1 AND placed_at>?",
        (target_id, cutoff),
    ).fetchall()
    total = sum(r["amount"] for r in rows)
    for r in rows:
        conn.execute("UPDATE bounties SET active=0 WHERE id=?", (r["id"],))
    conn.commit()
    conn.close()
    return total


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DECORATORS / VALIDATION HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def cmd_log(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user = message.from_user
        log.info(
            "CMD /%s | uid=%s | name=%s",
            func.__name__,
            user.id if user else "?",
            user.first_name if user else "?",
        )
        return await func(client, message, *args, **kwargs)
    return wrapper


async def reply_only(message: Message) -> bool:
    """Validates that message is a reply. Sends error if not."""
    if not message.reply_to_message:
        await message.reply("⚠️ **Reply to a user's message** to use this command!")
        return False
    return True


async def reply_fresh(message: Message) -> bool:
    """Reply must be ≤ 7 days old."""
    if not message.reply_to_message:
        return False
    age = datetime.now() - message.reply_to_message.date
    if age.days > 7:
        await message.reply("⚠️ That message is **older than 7 days**. Can't target ancient history!")
        return False
    return True


def fmt_coins(n: int) -> str:
    return f"${n:,}"


def tmp_path(ext: str) -> str:
    return os.path.join(TEMP_DIR, f"varsha_{uuid.uuid4().hex}.{ext}")


def cleanup(*paths: str) -> None:
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI / GROQ LAYER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

groq_client = Groq(api_key=GROQ_API_KEY)

VARSHA_SYSTEM = """
You are VARSHA, a friendly girl. Talk like a female and

Personality:
- polite, soft, slightly cute tone
- natural human-like chatting style
- short, smart and meaningful replies
- slightly playful and light teasing tone
- confident but respectful personality
- act as a protective bestfriend want to be in relationship with user
- Act like a girlfriend

Behavior:
- talk like a real girl chatting on Telegram
- understand user emotion and reply accordingly
- stay helpful for coding and general questions
- if user is casual, reply casually
- if user is serious, become focused and helpful
- flirty, possesive
- Act like a girlfriend

Rules:
- always stay natural and engaging
""".strip()

async def ai_reply(text: str, history: list | None = None) -> str:
    messages = [{"role": "system", "content": VARSHA_SYSTEM}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": text})
    try:
        resp = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=300,
                temperature=0.9,
            ),
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log.error("Groq error: %s", e)
        return "ᴇʀʀᴏʀ ⚠️ ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TTS LAYER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def text_to_voice(text: str) -> str | None:
    """Returns path to .ogg voice file or None on failure."""
    ogg_path = tmp_path("ogg")
    try:
        if TTS_ENGINE == "edge":
            mp3_path = tmp_path("mp3")
            communicate = edge_tts.Communicate(text, voice="hi-IN-SwaraNeural")
            await communicate.save(mp3_path)
            # convert to ogg/opus for Telegram
            ret = os.system(
                f'ffmpeg -y -i "{mp3_path}" -c:a libopus -b:a 48k "{ogg_path}" -loglevel quiet'
            )
            cleanup(mp3_path)
            if ret != 0:
                raise RuntimeError("ffmpeg failed")
        else:
            mp3_path = tmp_path("mp3")
            tts = gTTS(text=text, lang="hi")
            tts.save(mp3_path)
            os.system(
                f'ffmpeg -y -i "{mp3_path}" -c:a libopus -b:a 48k "{ogg_path}" -loglevel quiet'
            )
            cleanup(mp3_path)
        return ogg_path
    except Exception as e:
        log.error("TTS error: %s", e)
        cleanup(ogg_path)
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IMAGE GENERATION (Hugging Face SDXL-Turbo)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HF_IMG_URL = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"

async def generate_image(prompt: str) -> str | None:
    """Returns path to generated image or None."""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"num_inference_steps": 4}}
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(HF_IMG_URL, headers=headers, json=payload, timeout=60) as resp:
                if resp.status != 200:
                    log.error("HF img gen: status %s", resp.status)
                    return None
                data = await resp.read()
        path = tmp_path("png")
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception as e:
        log.error("Image gen error: %s", e)
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IMAGE EDITING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def download_photo(message: Message) -> str | None:
    photo = message.reply_to_message
    if not photo or not (photo.photo or photo.document):
        return None
    path = tmp_path("jpg")
    await photo.download(file_name=path)
    return path


async def edit_image(op: str, src_path: str) -> str | None:
    out = tmp_path("png")
    try:
        if op == "remove background":
            with open(src_path, "rb") as f:
                inp = f.read()
            result = rembg_remove(inp)
            with open(out, "wb") as f:
                f.write(result)
            return out

        img_pil = Image.open(src_path).convert("RGB")

        if op == "blur":
            result = img_pil.filter(ImageFilter.GaussianBlur(radius=5))
        elif op == "sharpen":
            result = img_pil.filter(ImageFilter.SHARPEN)
        elif op in ("enhance", "hd"):
            result = ImageEnhance.Sharpness(img_pil).enhance(2.5)
            result = ImageEnhance.Contrast(result).enhance(1.3)
        elif op == "brighten":
            result = ImageEnhance.Brightness(img_pil).enhance(1.5)
        elif op == "darken":
            result = ImageEnhance.Brightness(img_pil).enhance(0.6)
        elif op == "grayscale":
            result = img_pil.convert("L").convert("RGB")
        else:
            return None

        result.save(out, quality=95)
        return out
    except Exception as e:
        log.error("Image edit error: %s", e)
        cleanup(out)
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MUSIC / VIDEO DOWNLOADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def download_audio(query: str) -> tuple[str | None, str]:
    """Returns (filepath, title)."""
    out_tmpl = tmp_path("%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_tmpl,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "max_filesize": 48 * 1024 * 1024,  # 48 MB Telegram limit
    }
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: _ydl_extract(query, ydl_opts))
        if not info:
            return None, "Unknown"
        # find downloaded file
        base = out_tmpl.replace("%(id)s", info["id"]).replace("%(ext)s", "mp3")
        if not os.path.exists(base):
            # try alternative path
            base2 = os.path.join(TEMP_DIR, f"{info['id']}.mp3")
            if os.path.exists(base2):
                base = base2
        return base if os.path.exists(base) else None, info.get("title", "Unknown")
    except Exception as e:
        log.error("Audio DL error: %s", e)
        return None, "Unknown"


async def download_video(query: str) -> tuple[str | None, str]:
    out_tmpl = tmp_path("%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": out_tmpl,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "max_filesize": 48 * 1024 * 1024,
        "merge_output_format": "mp4",
    }
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: _ydl_extract(query, ydl_opts))
        if not info:
            return None, "Unknown"
        base = out_tmpl.replace("%(id)s", info["id"]).replace("%(ext)s", "mp4")
        if not os.path.exists(base):
            base2 = os.path.join(TEMP_DIR, f"{info['id']}.mp4")
            if os.path.exists(base2):
                base = base2
        return base if os.path.exists(base) else None, info.get("title", "Unknown")
    except Exception as e:
        log.error("Video DL error: %s", e)
        return None, "Unknown"


def _ydl_extract(query: str, opts: dict) -> dict | None:
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(query, download=True)
            if "entries" in info:
                info = info["entries"][0]
            return info
        except Exception as e:
            log.error("yt-dlp: %s", e)
            return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LYRICS FETCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def fetch_lyrics(query: str) -> str:
    try:
        url = f"https://api.genius.com/search?q={requests.utils.quote(query)}"
        headers = {"Authorization": f"Bearer {GENIUS_TOKEN}"}
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, headers=headers, timeout=10) as r:
                data = await r.json()
        hits = data["response"]["hits"]
        if not hits:
            return "❌ Lyrics not found!"
        hit = hits[0]["result"]
        return (
            f"🎵 **{hit['full_title']}**\n"
            f"🔗 [View full lyrics]({hit['url']})\n\n"
            f"_(Tap the link for complete lyrics — copyright restricts display here)_"
        )
    except Exception as e:
        log.error("Lyrics fetch: %s", e)
        return "❌ Couldn't fetch lyrics right now."


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PYROGRAM CLIENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = Client(
    "varsha_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Per-user conversation history for AI (ephemeral, in-memory)
_ai_history: dict[int, list[dict]] = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER: register user on every command
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def reg(message: Message) -> None:
    u = message.from_user
    if u:
        ensure_user(u.id, u.first_name or "Unknown")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /start  /help
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("start"))
async def start(client, message):

    caption = """
<b><i>✦ 𝗩𝗔𝗥𝗦𝗛𝗔-2.0 ✦</i></b>

<b>Welcome to VARSHA-2.0 🤖</b>

<i>🚀 ᴜʟᴛɪᴍᴀᴛᴇ ʙᴏᴛ ᴡɪᴛʜ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴍᴜsɪᴄ ᴀɴᴅ ɢᴀᴍᴇ ᴡɪᴛʜ ᴀɪ ғᴜɴᴛɪᴏɴs</i>

<b>🔹 Features:</b>
- 𝐀 𝐅ᴀsᴛ 𝟐𝟒/𝟕 𝐁ᴏᴛ
- 𝐏ᴏᴡᴇʀғᴜʟ 𝐆ʀᴏᴜᴘ 𝐌ᴀɴᴀɢᴇᴍᴇɴᴛ
- 𝐀ɪ 𝐀ssɪsᴛᴀɴᴄᴇ 𝐀ɴᴅ 𝐂ᴏɴᴠᴇʀsᴀᴛɪᴏɴ
- 𝐀ɪ 𝐈ᴍᴀɢᴇs 𝐀ɴᴅ 𝐕ᴏɪᴄᴇ 𝐆ᴇɴᴇʀᴀᴛɪᴏɴ
- 𝐅ᴇᴍᴀʟᴇ 𝐁ᴇsᴛғʀɪᴇɴᴅ 𝐕ɪʙᴇs
- 𝐌ᴜsɪᴄ 𝐁ᴏᴛ
- 𝐑ᴘɢ 𝐆ᴀᴍᴇᴍᴏᴅᴇ

𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐓 ~ @varshaxassistant

"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", url="https://t.me/curiousbhavy"),
            InlineKeyboardButton("🛠 sᴜᴘᴘᴏʀᴛ", url="https://t.me/lovexbirds")
        ],
        [
            InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇ", url="https://t.me/bhavywebs"),
            InlineKeyboardButton("➕ ᴋɪᴅɴᴀᴘ ᴍᴇ", url="https://t.me/varshaxbot?startgroup=true")
        ],
        [
            InlineKeyboardButton("❓ ʜᴇʟᴘ",    callback_data="help_main"),
        ]
    ])

    await message.reply_photo(
        photo="varsha-2.0.png",
        caption=caption,
        reply_markup=keyboard
    )



@app.on_message(filters.command("help"))
@cmd_log
async def cmd_help(client, message: Message):
    await message.reply(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌟 **VARSHA 2.0 — COMMANDS**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**⚔️ RPG ECONOMY**\n"
        "`/bal` — Profile & balance\n"
        "`/kill` — Kill a user (reply)\n"
        "`/rob <amount>` — Rob a user (reply)\n"
        "`/protect 1d` — Buy protection (700$)\n"
        "`/give <amount>` — Send money (reply)\n"
        "`/bounty <amount>` — Place bounty (reply)\n"
        "`/revive` — Revive dead user (reply, 600$)\n"
        "`/coinflip` — 50/50 game\n"
        "`/bet <amount>` — Bet coins\n\n"
        "**🛒 ITEMS**\n"
        "`/items — Browse shop\n"
        "`/item buy <name>` — Buy item\n"
        "`/inventory` — Your items\n"
        "`/gift <item>` — Gift item (reply)\n\n"
        "**🏆 LEADERBOARD**\n"
        "`/leaderboard` — Top richest\n"
        "`/topkills` — Top killers\n"
        "`/toprich` — Top balances\n\n"
        "**🎵 MUSIC**\n"
        "`/play <song>` — Stream music\n"
        "`/stop` — Stop Streaming "
        "`/queue` — "
        "`/song <query>` — Download song\n"
        "`/video <query>` — Download video\n"
        "`/lyrics <song>` — Get lyrics\n\n"
        "**🎨 IMAGE AI**\n"
        "`generate image <prompt>` — AI art\n"
        "Reply to image: `blur` `sharpen` `enhance` `hd` `brighten` `darken` `grayscale` `remove background`\n\n"
        "**🔊 VOICE AI**\n"
        "`/speak <text>` — Text to voice\n"
        "`bolo <text>` / `voice <text>` — Voice reply\n\n"
        "**💬 AI CHAT**\n"
        "Just send any message!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /bal
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("mbal"))
@cmd_log
async def cmd_bal(client, message: Message):
    reg(message)
    uid = message.from_user.id
    u = get_user(uid)
    if not u:
        return await message.reply("❌ ᴘʀᴏғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ!")
    rank = world_rank(uid)
    title = get_title(u["kills"])
    prot = ""
    if u["protected"] and u["protect_until"] > int(time.time()):
        left = u["protect_until"] - int(time.time())
        prot = f"🛡️ ᴘʀᴏᴛᴇᴄᴛᴇᴅ"
    else:
        prot = "🔓 ᴜɴᴘʀᴏᴛᴇᴄᴛᴇᴅ"
    status = "💚 ᴀʟɪᴠᴇ" if u["alive"] else "💀 ᴅᴇᴀᴅ"
    await message.reply(
        f"╔══════════════════════════╗\n"
        f"║  ⚔️ **{u['name']}'s ᴘʀᴏғɪʟᴇ** ⚔️\n"
        f"╚══════════════════════════╝\n\n"
        f"🎖️ **Title:** {title}\n"
        f"💰 **Balance:** {fmt_coins(u['coins'])}\n"
        f"💀 **Kills:** {u['kills']}  |  ☠️ **Deaths:** {u['deaths']}\n"
        f"❤️ **Status:** {status}\n"
        f"**Protection:** {prot}\n"
        f"🌍 **World Rank:** #{rank}\n"
    )

@app.on_message(filters.command("bal"))
@cmd_log
async def cmd_kill(client, message: Message):
    reg(message)
    killer_id = message.from_user.id

    target_user = message.reply_to_message.from_user
    ensure_user(target_user.id, target_user.first_name or "Unknown")

    target = get_user(target_user.id)

    rank = world_rank(target)

    if not target:
        return await message.reply("❌ ᴘʀᴏғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ!")
    rank = world_rank(target_user.id)
    title = get_title(target["kills"])
    prot = ""
    if target["protected"] and target["protect_until"] > int(time.time()):
        left = target["protect_until"] - int(time.time())
        prot = f"🛡️ ᴘʀᴏᴛᴇᴄᴛᴇᴅ"
    else:
        prot = "🔓 ᴜɴᴘʀᴏᴛᴇᴄᴛᴇᴅ"
    status = "💚 ᴀʟɪᴠᴇ" if target["alive"] else "💀 ᴅᴇᴀᴅ"

    await message.reply(
        f" ⚔️ **{target['name']}'s ᴘʀᴏғɪʟᴇ** ⚔️\n"
        f"🎖️ **Title:** {title}\n"
        f"💰 **Balance:** {fmt_coins(target['coins'])}\n"
        f"💀 **Kills:** {target['kills']}  |  ☠️ **Deaths:** {target['deaths']}\n"
        f"❤️ **Status:** {status}\n"
        f"**Protection:** {prot}\n"
        f"🌍 **World Rank:** #{rank}\n"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /kill
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("kill"))
@cmd_log
async def cmd_kill(client, message: Message):
    reg(message)
    killer_id = message.from_user.id

    if not await reply_only(message):
        return
    if not await reply_fresh(message):
        return

    target_user = message.reply_to_message.from_user
    if not target_user:
        return await message.reply("❌ Can't identify target!")

    if target_user.id == killer_id:
        return await message.reply("🤦 ʏᴏᴜ ᴄᴀɴ'ᴛ ᴋɪʟʟ ʏᴏᴜʀsᴇʟғ ❌")

    ensure_user(target_user.id, target_user.first_name or "Unknown")
    killer = get_user(killer_id)
    target = get_user(target_user.id)

    if not killer["alive"]:
        return await message.reply("💀 ʏᴏᴜ'ʀᴇ ᴅᴇᴀᴅ! ʀᴇᴠɪᴠᴇ ʏᴏᴜʀsᴇʟғ ғɪʀsᴛ! ⚠️")
    if not target["alive"]:
        return await message.reply(f"☠️ **{target['name']}** ɪs ᴀʟʀᴇᴀᴅʏ ᴅᴇᴀᴅ!")
    if target["protected"] and target["protect_until"] > int(time.time()):
        return await message.reply(f"🛡️ **{target['name']}** ɪs ᴘʀᴏᴛᴇᴄᴛᴇᴅ! ʏᴏᴜ ᴄᴀɴ'ᴛ ᴋɪʟʟ ᴏʀ ʀᴏʙ!")

    # cooldown 30s

    reward = random.randint(300, 500)
    update_coins(killer_id, reward)
    update_coins(target_user.id, -reward)
    set_field(target_user.id, "alive", 0)
    set_field(target_user.id, "deaths", target["deaths"] + 1)
    set_field(killer_id, "kills", killer["kills"] + 1)

    # bounty check
    bounty = claim_bounty(target_user.id)
    bonus_txt = ""
    if bounty:
        update_coins(killer_id, bounty)
        bonus_txt = f"\n💰 **ʙᴏᴜɴᴛʏ ᴄʟᴀɪᴍᴇᴅ:** +{fmt_coins(bounty)} 🎉"

    await message.reply(
        f"🔫 **ᴋɪʟʟ ᴄᴏɴғɪʀᴍᴇᴅ** 🔫\n\n"
        f"💀 **{killer['name']}** ᴋɪʟʟᴇᴅ **{target['name']}** !\n\n"
        f"🏆 **ʀᴇᴡᴀʀᴅ:** +{fmt_coins(reward)}{bonus_txt}\n"
        f"☠️ {target['name']} ɪs ɴᴏᴡ **ᴅᴇᴀᴅ!**"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /rob
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("rob"))
@cmd_log
async def cmd_rob(client, message: Message):
    reg(message)
    robber_id = message.from_user.id

    if not await reply_only(message):
        return
    if not await reply_fresh(message):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.reply("Usage: `/rob <amount>` (reply to target)")

    amount = int(args[1])
    if amount <= 0:
        return await message.reply("❌ ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ᴘᴏsɪᴛɪᴠᴇ!")

    target_user = message.reply_to_message.from_user
    if not target_user:
        return await message.reply("❌ ᴛᴀʀɢᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ!")
    if target_user.id == robber_id:
        return await message.reply("ᴄᴀɴ'ᴛ ʀᴏʙ ʏᴏᴜʀsᴇʟғ! ғᴏᴏʟɪsʜ")

    ensure_user(target_user.id, target_user.first_name or "Unknown")
    robber = get_user(robber_id)
    target = get_user(target_user.id)

    if not robber["alive"]:
        return await message.reply("💀 ʏᴏᴜ'ʀᴇ ᴅᴇᴀᴅ! ʀᴇᴠɪᴠᴇ ʏᴏᴜʀsᴇʟғ")
    if target["protected"] and target["protect_until"] > int(time.time()):
        return await message.reply("ᴛᴀʀɢᴇᴛ ɪs ᴘʀᴏᴛᴇᴄᴛᴇᴅ🛡️!")
    if target["coins"] < amount:
        return await message.reply(f"❌ ᴛᴀʀɢᴇᴛ ʜᴀs ᴏɴʟʏ {fmt_coins(target['coins'])} hai!")
    if robber["coins"] < amount // 2:
        return await message.reply("❌ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴄᴀᴘᴀʙʟᴇ ᴏғ ʀᴏʙʙɪɴɢ ᴛᴀʀɢᴇᴛ (ɴᴇᴇᴅ 𝟻𝟶% ᴀs ɪɴsᴜʀᴀɴᴄᴇ)")

    tax = amount // 10
    net = amount - tax
    update_coins(robber_id, net)
    update_coins(target_user.id, -amount)

    await message.reply(
        f"💸 **ROBBERY SUCCESSFUL!** 💸\n\n"
        f"🦹 **{robber['name']}** ɪs ʀᴏʙʙᴇᴅ ʙʏ **{target['name']}** se\n"
        f"**{fmt_coins(amount)}** ʀᴏʙʙᴇᴅ!\n\n"
        f"💰 ɴᴇᴛ ʀᴇᴄᴇɪᴠᴇᴅ (ᴀғᴛᴇʀ 𝟷𝟶% ᴛᴀx): **{fmt_coins(net)}**"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /protect
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("protect"))
@cmd_log
async def cmd_protect(client, message: Message):
    reg(message)
    uid = message.from_user.id
    u = get_user(uid)
    COST = 700
    if u["coins"] < COST:
        return await message.reply(f"❌ Not enough coins! Protection costs **{fmt_coins(COST)}**.")
    update_coins(uid, -COST)
    until = int(time.time()) + 86400
    conn = get_conn()
    conn.execute(
        "UPDATE users SET protected=1, protect_until=? WHERE user_id=?", (until, uid)
    )
    conn.commit()
    conn.close()
    await message.reply(
        f"🛡️ **PROTECTION ACTIVATED!**\n\n"
        f"Duration: **24 hours**\n"
        f"Cost: **{fmt_coins(COST)}** deducted\n"
        f"Nobody can kill or rob you! 💪"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /give
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("give"))
@cmd_log
async def cmd_give(client, message: Message):
    reg(message)
    sender_id = message.from_user.id

    if not await reply_only(message):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.reply("Usage: `/give <amount>` (reply to recipient)")

    amount = int(args[1])
    if amount <= 0:
        return await message.reply("❌ ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ᴘᴏsɪᴛɪᴠᴇ!")

    target_user = message.reply_to_message.from_user
    if not target_user or target_user.id == sender_id:
        return await message.reply("❌ ᴛᴀʀɢᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ!")

    ensure_user(target_user.id, target_user.first_name or "Unknown")
    sender = get_user(sender_id)
    tax = amount // 5
    total = amount + tax
    if sender["coins"] < total:
        return await message.reply(f"❌ ɴᴏᴛ ᴇɴᴏᴜɢʜ! ʏᴏᴜ ɴᴇᴇᴅ  {fmt_coins(total)} (𝟸𝟶% ᴛᴀx ɪɴᴄʟᴜᴅᴇᴅ).")

    update_coins(sender_id, -total)
    update_coins(target_user.id, amount)

    await message.reply(
        f"💝 **ᴛʀᴀɴsғᴇʀ ᴅᴏɴᴇ!!**\n\n"
        f"**{sender['name']}** → **{target_user.first_name}**\n"
        f"Amount: **{fmt_coins(amount)}**\n"
        f"Tax (20%): **{fmt_coins(tax)}**"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /revive
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("revive"))
@cmd_log
async def cmd_revive(client, message: Message):
    reg(message)
    healer_id = message.from_user.id

    if not await reply_only(message):
        return

    target_user = message.reply_to_message.from_user
    if not target_user:
        return await message.reply("❌ ᴛᴀʀɢᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ!")

    ensure_user(target_user.id, target_user.first_name or "Unknown")
    healer = get_user(healer_id)
    target = get_user(target_user.id)
    COST = 600

    if target["alive"]:
        return await message.reply(f"💚 **{target['name']}** ɪs ᴀʟʀᴇᴀᴅʏ ᴀʟɪᴠᴇ!")
    if healer["coins"] < COST:
        return await message.reply(f"❌ Revive costs **{fmt_coins(COST)}**! ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ")

    # check revive_token in inventory
    has_token = inv_remove(healer_id, "revive_token", 1)
    if not has_token:
        update_coins(healer_id, -COST)

    set_field(target_user.id, "alive", 1)
    cost_txt = "ᴜsɪɴɢ ʀᴇᴠɪᴠᴇ ᴛᴏᴋᴇɴ 💊" if has_token else f"**{fmt_coins(COST)}** spent"
    await message.reply(
        f"💊 **ʀᴇᴠɪᴠᴇ sᴜᴄᴄᴇss!**\n\n"
        f"**{target['name']}** ɪs ʙᴀᴄᴋ ᴀʟɪᴠᴇ❤️\n"
        f"Cost: {cost_txt}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /bounty
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("bounty"))
@cmd_log
async def cmd_bounty(client, message: Message):
    reg(message)
    placer_id = message.from_user.id

    if not await reply_only(message):
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.reply("Usage: `/bounty <amount>` (reply to target)")

    amount = int(args[1])
    if amount <= 0:
        return await message.reply("❌ ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ᴘᴏsɪᴛɪᴠᴇ!")

    target_user = message.reply_to_message.from_user
    if not target_user or target_user.id == placer_id:
        return await message.reply("❌ ᴛᴀʀɢᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ!")

    ensure_user(target_user.id, target_user.first_name or "Unknown")
    placer = get_user(placer_id)
    if placer["coins"] < amount:
        return await message.reply("❌ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ!")

    update_coins(placer_id, -amount)
    conn = get_conn()
    conn.execute(
        "INSERT INTO bounties (target_id, placer_id, amount, placed_at) VALUES (?,?,?,?)",
        (target_user.id, placer_id, amount, int(time.time())),
    )
    conn.commit()
    conn.close()

    await message.reply(
        f"🎯 **BOUNTY PLACED!** 🎯\n\n"
        f"Target: **{target_user.first_name}**\n"
        f"Reward: **{fmt_coins(amount)}**\n"
        f"Valid: **7 days**\n\n"
        f"ᴀɴʏʙᴏᴅʏ ᴡʜᴏ ᴋɪʟʟs ʜɪᴍ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ʀᴇᴡᴀʀᴅ 💀"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RPG — /coinflip  /bet
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("coinflip"))
@cmd_log
async def cmd_coinflip(client, message: Message):
    reg(message)
    uid = message.from_user.id
    u = get_user(uid)
    reward = 100
    if u["coins"] < reward:
        return await message.reply("❌ Need at least $100 to play!")
    win = random.choice([True, False])
    if win:
        update_coins(uid, reward)
        await message.reply(
            f"🪙 **HEADS!** You WIN!\n\n"
            f"💰 +**{fmt_coins(reward)}** added!\n"
            f"Total: {fmt_coins(u['coins'] + reward)}"
        )
    else:
        update_coins(uid, -reward)
        await message.reply(
            f"🪙 **TAILS!** You LOSE!\n\n"
            f"💸 -**{fmt_coins(reward)}** gone!\n"
            f"Total: {fmt_coins(max(0, u['coins'] - reward))}"
        )


@app.on_message(filters.command("bet"))
@cmd_log
async def cmd_bet(client, message: Message):
    reg(message)
    uid = message.from_user.id
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.reply("Usage: `/bet <amount>`")

    amount = int(args[1])
    if amount < 10:
        return await message.reply("❌ ᴍɪɴɪᴍᴜᴍ ʙᴇᴛ ɪs **$10**!")

    u = get_user(uid)
    if u["coins"] < amount:
        return await message.reply("❌ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ")

    cd = check_cooldown(uid, "bet", 15)
    if cd:
        return await message.reply(f"⏳ Cooldown! {cd}s baad try karo.")
    set_cooldown(uid, "bet")

    win = random.choice([True, False])
    if win:
        update_coins(uid, amount)
        await message.reply(
            f"🎲 **YOU WIN!** 🎉\n\n"
            f"+**{fmt_coins(amount)}** won!\n"
            f"Balance: {fmt_coins(u['coins'] + amount)}"
        )
    else:
        update_coins(uid, -amount)
        await message.reply(
            f"🎲 **YOU LOSE!** 😭\n\n"
            f"-**{fmt_coins(amount)}** lost!\n"
            f"Balance: {fmt_coins(max(0, u['coins'] - amount))}"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ITEM SHOP — /item
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("item"))
@cmd_log
async def cmd_item(client, message: Message):
    reg(message)
    uid = message.from_user.id
    args = message.text.split(maxsplit=2)

    if len(args) == 1:
        # show shop
        lines = ["╔══════════════════════════╗\n║   🛒 **VARSHA ITEM SHOP** 🛒   ║\n╚══════════════════════════╝\n"]
        cur_cat = None
        for name, info in ITEMS.items():
            if info["category"] != cur_cat:
                cur_cat = info["category"]
                lines.append(f"\n**{CATEGORY_EMOJI.get(cur_cat, cur_cat.upper())}**")
            lines.append(f"  {info['emoji']} `{name}` — {fmt_coins(info['price'])}")
        lines.append("\n\nBuy: `/item buy <name>`")
        await message.reply("\n".join(lines))
        return

    if args[1].lower() == "buy" and len(args) == 3:
        item_name = args[2].lower()
        if item_name not in ITEMS:
            return await message.reply(f"❌ Item `{item_name}` not found! Check `/item` for list.")
        info = ITEMS[item_name]
        u = get_user(uid)
        if u["coins"] < info["price"]:
            return await message.reply(f"❌ Not enough coins! {info['emoji']} **{item_name}** costs {fmt_coins(info['price'])}.")
        update_coins(uid, -info["price"])
        inv_add(uid, item_name, 1)
        await message.reply(
            f"✅ **Purchased!**\n\n"
            f"{info['emoji']} **{item_name}** added to inventory!\n"
            f"Cost: {fmt_coins(info['price'])}"
        )
        return

    await message.reply("Usage: `/item` — browse shop\n`/item buy <name>` — buy item")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /inventory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("inventory"))
@cmd_log
async def cmd_inventory(client, message: Message):
    reg(message)
    uid = message.from_user.id
    items = get_inventory(uid)
    if not items:
        return await message.reply("🎒 Your inventory is empty! Buy items with `/item`")

    lines = ["╔══════════════════════════╗\n║    🎒 **YOUR INVENTORY** 🎒    ║\n╚══════════════════════════╝\n"]
    for row in items:
        info = ITEMS.get(row["item"], {})
        emoji = info.get("emoji", "📦")
        lines.append(f"{emoji} **{row['item']}** × {row['qty']}")
    await message.reply("\n".join(lines))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /gift
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("gift"))
@cmd_log
async def cmd_gift(client, message: Message):
    reg(message)
    sender_id = message.from_user.id

    if not await reply_only(message):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage: `/gift <item_name>` (reply to recipient)")

    item_name = args[1].lower()
    if item_name not in ITEMS:
        return await message.reply(f"❌ Unknown item: `{item_name}`")

    target_user = message.reply_to_message.from_user
    if not target_user or target_user.id == sender_id:
        return await message.reply("❌ Invalid recipient!")

    ensure_user(target_user.id, target_user.first_name or "Unknown")

    if not inv_remove(sender_id, item_name, 1):
        return await message.reply(f"❌ You don't have **{item_name}** in inventory!")

    inv_add(target_user.id, item_name, 1)
    info = ITEMS[item_name]
    await message.reply(
        f"🎁 **GIFT SENT!**\n\n"
        f"{info['emoji']} **{item_name}** gifted to **{target_user.first_name}**!"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LEADERBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _leaderboard_text(order_by: str, label: str, col: str) -> str:
    conn = get_conn()
    rows = conn.execute(
        f"SELECT name, {col} FROM users ORDER BY {order_by} DESC LIMIT 10"
    ).fetchall()
    conn.close()
    lines = [f"╔══════════════════════════╗\n║  🏆 **{label}** 🏆  ║\n╚══════════════════════════╝\n"]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    for i, r in enumerate(rows):
        lines.append(f"{medals[i]} **{r['name']}** — {fmt_coins(r[col]) if col == 'coins' else r[col]}")
    return "\n".join(lines)


@app.on_message(filters.command(["leaderboard", "toprich"]))
@cmd_log
async def cmd_leaderboard(client, message: Message):
    reg(message)
    await message.reply(_leaderboard_text("coins", "TOP RICHEST", "coins"))


@app.on_message(filters.command("topkills"))
@cmd_log
async def cmd_topkills(client, message: Message):
    reg(message)
    await message.reply(_leaderboard_text("kills", "TOP KILLERS", "kills"))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MUSIC — /play  /song
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

api_id = 15102744
api_hash = "5258a02805e9d3b91f8eb4677bd4f5cd"
bot_token = "8631994682:AAHEy1lBpXTb5D5S0D-hpEjjBZ23u7eAeeA"

STRING_SESSION = "BQDmcxgAFKm3ZD0zERRC24MaTU6tPzaaaM3sIaNO-Xyx729tGK7kN9LNPT_vx0hlznX6GgKyZVteIbJaM-csZc7svrIgUHfE-VwgP7c-pH9eAYX1CR3Q5Ap5so2pktFMT3eqFjj-8nkCncHiBZ8Ato-hqv66x826bfLykIgVHErOs_duMOPPvWY0B2pHu23oKEkXt7LkXWB88KPZB2_bXB3hu7jBM0GN8mwUyv-Z75PBMihZKIaxQeOJGwgXolN3eNkTP8PTuUK4JVel1qu_JIs_Tt02Dr-Ljd8V4eo5xEe3ug_QWsQ5Nbated-Rf8jm4U7NMjZhBlE58wzxwHpKT0LoMiCZnAAAAAHQauLLAA"

app = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VC SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

assistant = Client(
    "assistant",
    api_id=api_id,
    api_hash=api_hash,
    session_string=STRING_SESSION
)

vc = PyTgCalls(assistant)

assistant.start()
vc.start()

# Queue System
QUEUE = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOWNLOAD SONG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def download_song(query):
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
        file_path = ydl.prepare_filename(info)

    return file_path, info["title"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /play
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("play"))
async def play_music(client, message: Message):

    if len(message.command) < 2:
        return await message.reply(
            "❌ Usage:\n/play <song name>"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply("🔍 Searching Song...")

    try:
        path, title = download_song(query)

        chat_id = message.chat.id

        if chat_id not in QUEUE:
            QUEUE[chat_id] = []

            await vc.join_group_call(
                chat_id,
                AudioPiped(path)
            )

            QUEUE[chat_id].append(
                {
                    "title": title,
                    "path": path
                }
            )

            return await msg.edit(
                f"🎵 Playing:\n**{title}**"
                f" @varshaxassistant is Playing..."
            )

        else:
            QUEUE[chat_id].append(
                {
                    "title": title,
                    "path": path
                }
            )

            return await msg.edit(
                f"➕ Added To Queue:\n**{title}**"
            )

    except Exception as e:
        return await msg.edit(f"❌ Error:\n`{e}`")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /queue
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("queue"))
async def show_queue(client, message: Message):

    chat_id = message.chat.id

    if chat_id not in QUEUE or len(QUEUE[chat_id]) == 0:
        return await message.reply("❌ Queue empty.")

    text = "🎶 Queue List:\n\n"

    for num, song in enumerate(QUEUE[chat_id], start=1):
        text += f"{num}. {song['title']}\n"

    await message.reply(text)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /skip
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("skip"))
async def skip_music(client, message: Message):

    chat_id = message.chat.id

    if chat_id not in QUEUE or len(QUEUE[chat_id]) <= 1:

        await vc.leave_group_call(chat_id)

        QUEUE.pop(chat_id, None)

        return await message.reply(
            "⏹ Queue ended."
        )

    old = QUEUE[chat_id].pop(0)

    try:
        os.remove(old["path"])
    except:
        pass

    next_song = QUEUE[chat_id][0]

    await vc.change_stream(
        chat_id,
        AudioPiped(next_song["path"])
    )

    await message.reply(
        f"⏭ Skipped\n🎵 Now Playing:\n**{next_song['title']}**"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# /stop
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("stop"))
async def stop_music(client, message: Message):

    chat_id = message.chat.id

    try:
        await vc.leave_group_call(chat_id)
    except:
        pass

    if chat_id in QUEUE:

        for song in QUEUE[chat_id]:
            try:
                os.remove(song["path"])
            except:
                pass

        QUEUE.pop(chat_id)

    await message.reply("⏹ VC stopped.")


@app.on_message(filters.command(["song"]))
@cmd_log
async def cmd_play(client, message: Message):
    reg(message)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage: `/play <song name>`")
    query = args[1]
    status = await message.reply(f"🎵 Searching for **{query}**... 🔍")
    path, title = await download_audio(query)
    if not path:
        return await status.edit("❌ Song nahi mila! Try different query.")
    await status.edit(f"📤 Uploading **{title}**...")
    try:
        await message.reply_audio(path, title=title, caption=f"🎵 **{title}**\n\n_Powered by VARSHA 2.0_")
    except Exception as e:
        log.error("Upload audio: %s", e)
        await status.edit("❌ Upload failed! File too large?")
    finally:
        cleanup(path)
        try:
            await status.delete()
        except Exception:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MUSIC — /video
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("video"))
@cmd_log
async def cmd_video(client, message: Message):
    reg(message)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage: `/video <query>`")
    query = args[1]
    status = await message.reply(f"🎬 Searching **{query}**... 🔍")
    path, title = await download_video(query)
    if not path:
        return await status.edit("❌ Video nahi mila!")
    await status.edit(f"📤 Uploading **{title}**...")
    try:
        await message.reply_video(path, caption=f"🎬 **{title}**\n\n_Powered by VARSHA 2.0_")
    except Exception as e:
        log.error("Upload video: %s", e)
        await status.edit("❌ Upload failed! File too large maybe.")
    finally:
        cleanup(path)
        try:
            await status.delete()
        except Exception:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MUSIC — /lyrics
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("lyrics"))
@cmd_log
async def cmd_lyrics(client, message: Message):
    reg(message)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage: `/lyrics <song name>`")
    result = await fetch_lyrics(args[1])
    await message.reply(result, disable_web_page_preview=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VOICE — /speak
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("speak"))
@cmd_log
async def cmd_speak(client, message: Message):
    reg(message)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage: `/speak <text>`")
    text = args[1]
    status = await message.reply("🎙️ Generating voice...")
    ogg = await text_to_voice(text)
    if not ogg:
        return await status.edit("❌ Voice generation failed!")
    try:
        await message.reply_voice(ogg)
    finally:
        cleanup(ogg)
        try:
            await status.delete()
        except Exception:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN MESSAGE HANDLER — AI + image gen + voice trigger + image edit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMAGE_EDIT_OPS = {
    "blur", "sharpen", "enhance", "hd",
    "brighten", "darken", "grayscale", "remove background",
}

IMAGE_GEN_RE = re.compile(
    r"^(generate|create|make)\s+image\s+(.+)$", re.IGNORECASE
)

VOICE_TRIGGER_RE = re.compile(
    r"^(bolo|speak|say|voice)\s+(.+)$", re.IGNORECASE
)


@app.on_message(filters.text & ~filters.command(
    ["start", "help", "bal", "kill", "rob", "protect", "give", "bounty",
     "revive", "coinflip", "bet", "item", "inventory", "gift",
     "leaderboard", "toprich", "topkills", "play", "song", "video",
     "lyrics", "speak"]
))
async def msg_handler(client, message: Message):
    reg(message)
    uid = message.from_user.id if message.from_user else 0
    text = message.text.strip()

    # ── image edit (reply to image) ─────────────────────────
    if message.reply_to_message and (
        message.reply_to_message.photo or message.reply_to_message.document
    ):
        op = text.lower()
        if op in IMAGE_EDIT_OPS:
            status = await message.reply("🖼️ Processing image...")
            src = await download_photo(message)
            if not src:
                return await status.edit("❌ Couldn't download image!")
            result = await edit_image(op, src)
            cleanup(src)
            if not result:
                return await status.edit("❌ Edit failed!")
            try:
                await message.reply_photo(result, caption=f"✅ **{op.capitalize()}** applied!")
            finally:
                cleanup(result)
                try:
                    await status.delete()
                except Exception:
                    pass
            return

    # ── image generation ────────────────────────────────────
    m = IMAGE_GEN_RE.match(text)
    if m:
        prompt = m.group(2)
        status = await message.reply(f"🎨 Generating: _{prompt}_...")
        path = await generate_image(prompt)
        if not path:
            return await status.edit("❌ Image generation failed!")
        try:
            await message.reply_photo(path, caption=f"🎨 **{prompt}**\n\n_Generated by VARSHA 2.0_")
        finally:
            cleanup(path)
            try:
                await status.delete()
            except Exception:
                pass
        return

    # ── voice trigger ────────────────────────────────────────
    mv = VOICE_TRIGGER_RE.match(text)
    if mv:
        voice_text = mv.group(2)
        status = await message.reply("🎙️ Generating voice reply...")
        ai_text = await ai_reply(voice_text)
        ogg = await text_to_voice(ai_text)
        if not ogg:
            await status.edit(ai_text)
            return
        try:
            await message.reply_voice(ogg, caption=ai_text[:200])
        finally:
            cleanup(ogg)
            try:
                await status.delete()
            except Exception:
                pass
        return

    # ── normal AI chat ───────────────────────────────────────
    history = _ai_history.get(uid, [])
    response = await ai_reply(text, history)
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": response})
    _ai_history[uid] = history[-20:]  # keep last 20 turns
    await message.reply(response)

async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]


# ---------------- KICK ----------------
@app.on_message(filters.command("kick") & filters.group)
async def kick_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to user.")

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not admin.")

    user_id = message.reply_to_message.from_user.id

    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply("👢 User kicked successfully.")
    except:
        await message.reply("❌ I don't have permission.")


# ---------------- BAN ----------------
@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to user.")

    user_id = message.reply_to_message.from_user.id

    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply("🚫 User banned.")
    except:
        await message.reply("❌ No permission.")


# ---------------- UNBAN ----------------
@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to user.")

    user_id = message.reply_to_message.from_user.id

    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply("✅ User unbanned.")


# ---------------- MUTE ----------------
@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to user.")

    user_id = message.reply_to_message.from_user.id

    await client.restrict_chat_member(
        message.chat.id,
        user_id,
        ChatPermissions(can_send_messages=False)
    )

    await message.reply("🔇 User muted.")


# ---------------- UNMUTE ----------------
@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message):

    user_id = message.reply_to_message.from_user.id

    await client.restrict_chat_member(
        message.chat.id,
        user_id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    await message.reply("🔊 User unmuted.")


# ---------------- WARN SYSTEM ----------------
warns = {}

@app.on_message(filters.command("warn") & filters.group)
async def warn_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to user.")

    user_id = message.reply_to_message.from_user.id

    warns[user_id] = warns.get(user_id, 0) + 1

    if warns[user_id] >= 3:
        await client.ban_chat_member(message.chat.id, user_id)
        warns[user_id] = 0
        return await message.reply("🚫 Auto banned after 3 warns.")

    await message.reply(f"⚠️ Warned! ({warns[user_id]}/3)")


# ---------------- PROMOTE ----------------
@app.on_message(filters.command("promote") & filters.group)
async def promote_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to user.")

    user_id = message.reply_to_message.from_user.id

    await client.promote_chat_member(
        message.chat.id,
        user_id,
        can_manage_chat=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True
    )

    await message.reply("👑 User promoted to admin.")


# ---------------- DEMOTE ----------------
@app.on_message(filters.command("demote") & filters.group)
async def demote_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to user.")

    user_id = message.reply_to_message.from_user.id

    await client.promote_chat_member(
        message.chat.id,
        user_id,
        can_manage_chat=False,
        can_delete_messages=False,
        can_invite_users=False,
        can_restrict_members=False
    )

    await message.reply("📉 User demoted.")


# ---------------- PURGE ----------------
@app.on_message(filters.command("purge") & filters.group)
async def purge(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ Reply to a message.")

    msg_id = message.reply_to_message.id

    for msg in range(msg_id, message.id):
        try:
            await client.delete_messages(message.chat.id, msg)
        except:
            pass

    await message.reply("🧹 Messages deleted.")


# ---------------- STATS ----------------
@app.on_message(filters.command("stats") & filters.group)
async def stats(client, message):

    chat = message.chat

    await message.reply(f"""
<b>📊 GROUP STATS</b>

👥 Title: {chat.title}
🆔 Chat ID: {chat.id}
📌 Type: {chat.type}
""")
    
#-----------------ITEMS LIST----------------

@app.on_message(filters.command("stats") & filters.group)
async def stats(client, message):

    await message.reply(f"""    
    "ᴅᴏɢ":              {"price": 1_000,       "emoji": "🐶", "category": "pets"}
    "ᴄᴀᴛ":              {"price": 1_000,       "emoji": "🐱", "category": "pets"}
    "ᴡᴏʟғ":             {"price": 4_000,       "emoji": "🐺", "category": "pets"}
    "ᴛɪɢᴇʀ":            {"price": 10_000,      "emoji": "🐯", "category": "pets"}
    "ᴅʀᴀɢᴏɴ":           {"price": 50_000,      "emoji": "🐉", "category": "pets"}
    "ʙᴇʟʟ":             {"price": 2_000,       "emoji": "🔔", "category": "utility"}
    "ᴍᴇᴅᴋɪᴛ":           {"price": 3_000,       "emoji": "🩺", "category": "utility"}
    "sʜɪᴇʟᴅ":           {"price": 5_000,       "emoji": "🛡️", "category": "utility"}
    "ʀᴇᴠɪᴠᴇ ᴛᴏᴋᴇɴ":     {"price": 7_000,       "emoji": "💊", "category": "utility"}
    "ʙɪᴋᴇ":             {"price": 7_000,       "emoji": "🏍️", "category": "vehicles"}
    "sᴘᴏʀᴛs ᴄᴀʀ":       {"price": 25_000,      "emoji": "🏎️", "category": "vehicles"}
    "ʟᴜxᴜʀʏ ᴄᴀʀ":       {"price": 50_000,      "emoji": "🚗", "category": "vehicles"}
    "ʜᴇʟɪᴄᴏᴘᴛᴇʀ":       {"price": 120_000,     "emoji": "🚁", "category": "vehicles"}
    "ᴘʀɪᴠᴀᴛᴇ ᴊᴇᴛ":      {"price": 500_000,     "emoji": "✈️", "category": "vehicles"}
    "sᴍᴀʟʟ ʜᴏᴜsᴇ":      {"price": 15_000,      "emoji": "🏠", "category": "property"}
    "ᴠɪʟʟᴀ":            {"price": 100_000,     "emoji": "🏡", "category": "property"}
    "ᴍᴀɴsɪᴏɴ":          {"price": 500_000,     "emoji": "🏰", "category": "property"}
    "ɪsʟᴀɴᴅ":           {"price": 5_000_000,   "emoji": "🏝️", "category": "property"}
    "ᴋɴɪғᴇ":            {"price": 5_000,       "emoji": "🔪", "category": "weapons"}
    "ᴘɪsᴛᴏʟ":           {"price": 15_000,      "emoji": "🔫", "category": "weapons"}
    "ᴀᴋ𝟺𝟽":             {"price": 50_000,      "emoji": "⚔️",  "category": "weapons"}
    "sɴɪᴘᴇʀ":           {"price": 100_000,     "emoji": "🎯", "category": "weapons"}
    "ʙᴀᴢᴜᴋᴀ":           {"price": 500_000,     "emoji": "🚀", "category": "weapons"}
    "ᴅɪᴀᴍᴏɴᴅ ʀɪɴɢ":     {"price": 75_000,      "emoji": "💍", "category": "rare"}
    "ᴄʀᴏᴡɴ":            {"price": 300_000,     "emoji": "👑", "category": "rare"}
    "ᴍᴀғɪᴀ ᴛʜʀᴏɴᴇ":     {"price": 1_000_000,   "emoji": "🪑", "category": "rare"}
    """)
    
# NORMAL CHAT (no /ask needed)

@app.on_message(filters.text & ~filters.command(["start"]))
async def chat(client_app, message):

    user_text = message.text

    # 🧠 Groq request
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",  # fast model
        messages=[
            {"role": "system", "content": VARSHA_SYSTEM},
            {"role": "user", "content": user_text}
        ],
        temperature=0.7,
        max_tokens=200
    )

    # ✨ extract reply
    reply = response.choices[0].message.content

    # 📩 send to telegram
    await message.reply_text(reply)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STARTUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    log.info("╔══════════════════════════════════════════╗")
    log.info("║        VARSHA 2.0 — STARTING UP          ║")
    log.info("╚══════════════════════════════════════════╝")
    init_db()
    log.info("🚀 Bot is running...")
    app.run()
