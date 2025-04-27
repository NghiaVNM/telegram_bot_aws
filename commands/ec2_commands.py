from telegram import Update
from telegram.ext import ContextTypes
from aws.ec2 import start_instance, stop_instance, list_running_instances, list_all_instances_across_regions

async def start_ec2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        instance_id = context.args[0]
        message = start_instance(instance_id)
        await update.message.reply_text(message)

async def stop_ec2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        instance_id = context.args[0]
        message = stop_instance(instance_id)
        await update.message.reply_text(message)

async def running(update: Update, context: ContextTypes.DEFAULT_TYPE):
    instances = list_running_instances()
    if instances:
        await update.message.reply_text("🖥️ Running instances:\n" + "\n".join(instances))
    else:
        await update.message.reply_text("No running instances.")

async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    instances = list_all_instances_across_regions()
    if instances:
        await update.message.reply_text("🗺️ All instances across regions:\n" + "\n".join(instances))
    else:
        await update.message.reply_text("No instances found.")
