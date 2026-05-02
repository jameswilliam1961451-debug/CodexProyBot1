bot.py


import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import random
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(name)

subscribed_users = set()

MOTIVATIONAL_QUOTES = [
    "🚀 Your journey to greatness begins now! Keep pushing forward!",
    "💪 The only limit is your mind. Break through it!",
    "✨ Every expert was once a beginner. Keep learning, keep growing!",
    "🔥 Your potential is endless. Don't stop until you're proud!",
    "🎯 Small daily improvements are the key to staggering results.",
    "🌟 You are capable of amazing things. Believe in yourself!"
]

async def send_motivation(context: ContextTypes.DEFAULT_TYPE):
    message = random.choice(MOTIVATIONAL_QUOTES)
    message += "\n\nStay focused. Stay great. 💪"
    
    for user_id in subscribed_users.copy():
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            logger.info(f"Sent motivation to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            subscribed_users.discard(user_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        await update.message.reply_text(
            "🌟 Your journey to greatness begins now!\n\n"
            "I will send you powerful motivation every 2 hours to keep your fire burning.\n\n"
            "Stay focused. Stay great.\n\n"
            "Use /stop to unsubscribe."
        )
        logger.info(f"New user subscribed: {user_id}")
    else:
        await update.message.reply_text("You're already subscribed! 🚀")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribed_users.discard(user_id)
    await update.message.reply_text(
        "You've been unsubscribed. Use /start to resubscribe anytime! 💪"
    )
    logger.info(f"User unsubscribed: {user_id}")

async def post_init(application: Application):
    scheduler = BackgroundScheduler()
    
    async def send_messages():
        await send_motivation(application.bot)
    
    def job_wrapper():
        asyncio.create_task(send_messages())
    
    scheduler.add_job(job_wrapper, trigger=IntervalTrigger(hours=2), id='motivation_job')
    scheduler.start()
    logger.info("Bot started - sending motivation every 2 hours")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("No bot token found! Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    application = Application.builder().token(token).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.run_polling()

if name == 'main':
    main()
