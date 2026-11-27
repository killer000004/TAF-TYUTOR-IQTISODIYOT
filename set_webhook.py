"""Ishlatish: python set_webhook.py https://sizning-domen.uz"""
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()
if len(sys.argv) != 2:
    sys.exit("Misol: python set_webhook.py https://sizning-domen.uz")

url = sys.argv[1].rstrip("/") + "/telegram/webhook"
r = httpx.post(
    f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/setWebhook",
    json={"url": url, "secret_token": os.environ.get("WEBHOOK_SECRET", "")},
)
print(r.json())
