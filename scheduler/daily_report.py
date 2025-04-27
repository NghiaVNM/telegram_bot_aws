from aws.cost import get_monthly_cost
from config.setting import TELEGRAM_CHAT_ID
from core.telegram_app import app

async def send_daily_cost_report(context):
    cost = get_monthly_cost()
    await app.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"📊 Daily AWS Cost Report:\nCurrent cost: {cost}")
