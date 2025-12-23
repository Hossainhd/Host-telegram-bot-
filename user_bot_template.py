#!/usr/bin/env python3
"""
USER BOT TEMPLATE - Deployed on Railway for each user
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from datetime import datetime

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command for user bot"""
    user = update.effective_user
    
    welcome_msg = f"""
🤖 **Welcome to Your Bot!**

👤 Owner: {user.first_name}
🆔 User ID: {user.id}
📅 Created: {datetime.now().strftime('%d/%m/%Y')}

✨ **Premium Features Active:**
✅ Inline Buttons
✅ Custom Commands
✅ Keyword Auto-reply
✅ Media Support

🔧 **Commands:**
/start - Start bot
/help - Show help
/settings - Bot settings
/myid - Show your ID

📞 **Support:** @CyperXploit
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Features", callback_data="features"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
            InlineKeyboardButton("🆘 Help", url="https://t.me/CyperXploit")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def inline_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "features":
        await query.edit_message_text(
            text="✨ **Premium Features:**\n\n"
                 "✅ Inline Keyboard Buttons\n"
                 "✅ Custom Command System\n"
                 "✅ Auto Reply to Keywords\n"
                 "✅ Media File Support\n"
                 "✅ User Management\n"
                 "✅ Database Support\n"
                 "✅ Scheduled Messages\n"
                 "✅ Multi-language Support",
            parse_mode='Markdown'
        )

async def keyword_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto reply to keywords"""
    message_text = update.message.text.lower()
    
    keywords = {
        "hello": "👋 Hello! How can I help you?",
        "hi": "👋 Hi there!",
        "price": "💰 Check /premium for pricing",
        "help": "🆘 Need help? Contact @CyperXploit",
        "bot": "🤖 I'm a premium bot hosted on Railway!",
        "time": f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}"
    }
    
    for keyword, reply in keywords.items():
        if keyword in message_text:
            await update.message.reply_text(reply)
            break

def main():
    """Start user bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("myid", 
        lambda u, c: u.message.reply_text(f"Your ID: `{u.effective_user.id}`", parse_mode='Markdown')))
    
    application.add_handler(CallbackQueryHandler(inline_button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    
    # Start bot
    print(f"🤖 User Bot Started for Owner: {OWNER_ID}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()