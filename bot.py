from core.telegram_app import app
from commands.cost_commands import cost
from commands.ec2_commands import start_ec2, stop_ec2, running, list_all
from commands.help_command import help_command
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from scheduler.daily_report import send_daily_cost_report
from datetime import time
from config.setting import TELEGRAM_CHAT_ID
from scheduler.daily_report import send_daily_cost_report


# Gắn command handler
app.add_handler(CommandHandler("cost", cost))
app.add_handler(CommandHandler("start", start_ec2))
app.add_handler(CommandHandler("stop", stop_ec2))
app.add_handler(CommandHandler("running", running))
app.add_handler(CommandHandler("listall", list_all))
app.add_handler(CommandHandler("help", help_command))

# post_init phải nhận tham số "application"
async def on_startup(application):
    print("Setting up bot commands...")
    commands = [
        BotCommand("cost", "View current AWS monthly cost"),
        BotCommand("running", "List running EC2 instances"),
        BotCommand("start", "Start an EC2 instance"),
        BotCommand("stop", "Stop an EC2 instance"),
        BotCommand("listall", "List all EC2 instances across regions"),
        BotCommand("help", "Show help information"),
    ]
    await application.bot.set_my_commands(commands)

    await application.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID, 
        text='✅ AWS Bot restarted and is now running.'
    )

    await send_daily_cost_report(application)

    app.job_queue.run_daily(
        send_daily_cost_report,
        time=time(hour=8, minute=0) 
    )

if __name__ == "__main__":
    print("Starting AWS Bot...")
    app.post_init = on_startup
    app.run_polling()

