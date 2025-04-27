from telegram.ext import ApplicationBuilder
from config.setting import TELEGRAM_TOKEN
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()