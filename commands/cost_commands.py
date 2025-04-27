from telegram import Update
from telegram.ext import ContextTypes
from aws.cost import get_monthly_cost

async def cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cost = get_monthly_cost()
    await update.message.reply_text(f"📊 Current AWS Cost: {cost}")
