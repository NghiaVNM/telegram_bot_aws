from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *AWS Automation Bot Commands:*\n\n"
        "/cost - 📊 View current AWS monthly cost\n"
        "/running - 🖥️ List running EC2 instances\n"
        "/start <instance-id> - ▶️ Start an EC2 instance\n"
        "/stop <instance-id> - ⏹️ Stop an EC2 instance\n"
        "/listall - 🌍 List all EC2 instances across all regions\n"
        "/help - ❓ Show help information"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")
