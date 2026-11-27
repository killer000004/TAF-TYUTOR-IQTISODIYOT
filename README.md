# Ota-onalarga xabar yuboruvchi Telegram bot

Veb-saytdan kelgan buyruq orqali talabaning ota-onasiga Telegramda xabar yuboradi.

## O'rnatish
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # va .env ichini to'ldiring
uvicorn main:app --host 0.0.0.0 --port 8000
python set_webhook.py https://sizning-domen.uz
```

## API (barchasi `X-API-Key` sarlavhasini talab qiladi)

**Talaba qo'shish** — `POST /api/students`
```json
{ "full_name": "Ali Valiyev" }
```
Javob: `{ "student_id": 1, "link": "https://t.me/bot?start=..." }` — shu havolani ota-onaga bering.

**Xabar yuborish** — `POST /api/notify`
```json
{ "student_id": 1, "text": "Farzandingiz bugun darsga kelmadi." }
```

Eslatma: API kalitni faqat backend'dan ishlating, frontend kodiga yozmang.
