import os
import secrets
import sqlite3

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_USERNAME = os.environ["BOT_USERNAME"]            # @ belgisiz, masalan: maktab_xabar_bot
API_KEY = os.environ["API_KEY"]                      # sayt va server orasidagi maxfiy kalit
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")  # Telegram so'rovlarini tekshirish uchun
DB_PATH = os.environ.get("DB_PATH", "bot.db")

TG = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI(title="Ota-onalarga xabar yuboruvchi bot")

db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.execute(
    "CREATE TABLE IF NOT EXISTS students("
    "id INTEGER PRIMARY KEY, full_name TEXT NOT NULL, link_token TEXT UNIQUE NOT NULL)"
)
db.execute(
    "CREATE TABLE IF NOT EXISTS parents("
    "id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, chat_id INTEGER NOT NULL, "
    "UNIQUE(student_id, chat_id))"
)
db.commit()


async def send(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=15) as client:
        return await client.post(f"{TG}/sendMessage", json={"chat_id": chat_id, "text": text})


def check_key(x_api_key: str | None):
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(401, "Ruxsat yo'q")


# ---------- Telegram webhook: faqat /start <token> ----------
@app.post("/telegram/webhook")
async def webhook(req: Request, x_telegram_bot_api_secret_token: str | None = Header(None)):
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(403, "Taqiqlangan")

    update = await req.json()
    msg = update.get("message")
    if not msg:
        return {"ok": True}

    text = msg.get("text", "")
    chat_id = msg["chat"]["id"]

    if text.startswith("/start"):
        parts = text.split()
        if len(parts) == 2:
            row = db.execute(
                "SELECT id, full_name FROM students WHERE link_token=?", (parts[1],)
            ).fetchone()
            if row:
                db.execute(
                    "INSERT OR IGNORE INTO parents(student_id, chat_id) VALUES(?,?)",
                    (row[0], chat_id),
                )
                db.commit()
                await send(chat_id, f"✅ {row[1]} uchun xabarnomalar yoqildi.")
                return {"ok": True}
        await send(chat_id, "Havola noto'g'ri yoki eskirgan. Maktabdan yangi havola so'rang.")
    # Boshqa xabarlarga bot javob bermaydi
    return {"ok": True}


# ---------- Veb-sayt uchun API ----------
class StudentIn(BaseModel):
    full_name: str


@app.post("/api/students")
async def add_student(data: StudentIn, x_api_key: str | None = Header(None)):
    """Talaba qo'shadi va ota-ona uchun ulanish havolasini qaytaradi."""
    check_key(x_api_key)
    token = secrets.token_urlsafe(16)
    cur = db.execute(
        "INSERT INTO students(full_name, link_token) VALUES(?,?)", (data.full_name, token)
    )
    db.commit()
    return {
        "student_id": cur.lastrowid,
        "link": f"https://t.me/{BOT_USERNAME}?start={token}",
    }


class Notify(BaseModel):
    student_id: int
    text: str


@app.post("/api/notify")
async def notify(data: Notify, x_api_key: str | None = Header(None)):
    """Talabaning barcha ulangan ota-onalariga xabar yuboradi."""
    check_key(x_api_key)
    rows = db.execute(
        "SELECT chat_id FROM parents WHERE student_id=?", (data.student_id,)
    ).fetchall()
    if not rows:
        raise HTTPException(404, "Bu talabaning ota-onasi botga ulanmagan")
    for (chat_id,) in rows:
        await send(chat_id, data.text)
    return {"sent": len(rows)}


@app.get("/")
async def health():
    return {"status": "ishlayapti"}
