#!/usr/bin/env python3
"""
MAIN BOT HOSTING MANAGER
Version 2.0 - Complete Solution
"""

import os
import sys
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==================== CONFIGURATION ====================
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 7971284841
ADMIN_USERNAME = "@CyperXploit"

# CRITICAL CHECK
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in Railway Variables!")
    print("Go to: Project → Variables → Add BOT_TOKEN")
    sys.exit(1)

# ==================== DATABASE SETUP ====================
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            self.init_tables()
            print("✅ Database Connected")
        except Exception as e:
            print(f"⚠️ Database Warning: {e}")
    
    def init_tables(self):
        try:
            with self.conn.cursor() as cur:
                # Users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username VARCHAR(100),
                        first_name VARCHAR(100),
                        status VARCHAR(20) DEFAULT 'active',
                        trial_end TIMESTAMP,
                        plan VARCHAR(20) DEFAULT 'trial',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Deployments table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS deployments (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        bot_name VARCHAR(100),
                        status VARCHAR(20) DEFAULT 'pending',
                        files_uploaded BOOLEAN DEFAULT FALSE,
                        bot_token VARCHAR(200),
                        railway_url VARCHAR(500),
                        cancel_requested BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Referrals table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS referrals (
                        id SERIAL PRIMARY KEY,
                        referrer_id BIGINT,
                        referred_id BIGINT,
                        bonus_given BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.conn.commit()
        except Exception as e:
            print(f"⚠️ Table Error: {e}")

db = DatabaseManager()

# ==================== BOT HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Modern Start Command with Beautiful Design"""
    user = update.effective_user
    
    # Register user in database
    try:
        with db.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, username, first_name, trial_end)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET username = EXCLUDED.username
            """, (user.id, user.username, user.first_name, datetime.now() + timedelta(days=3)))
            db.conn.commit()
    except:
        pass
    
    # BEAUTIFUL KEYBOARD DESIGN
    keyboard = [
        [InlineKeyboardButton("🚀 START FREE TRIAL", callback_data="start_trial")],
        [InlineKeyboardButton("💎 UPGRADE TO PREMIUM", callback_data="buy_premium")],
        [InlineKeyboardButton("🤖 DEPLOY YOUR BOT", callback_data="deploy_bot")],
        [InlineKeyboardButton("📊 MY DASHBOARD", callback_data="my_dashboard")],
        [InlineKeyboardButton("👥 REFER & EARN (+2H)", callback_data="refer_friend")],
        [InlineKeyboardButton("❓ HELP & SUPPORT", callback_data="help_support")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # MODERN WELCOME MESSAGE
    welcome_msg = f"""
✨ **WELCOME {user.first_name}!** ✨

🤖 **PREMIUM BOT HOSTING SERVICE**
✅ 3 Days FREE Trial • Auto Deployment
✅ Premium Features • 24/7 Support
✅ Easy Setup • Secure Hosting

⚡ **QUICK START:**
1. Click *START FREE TRIAL*
2. Upload your `bot.py` & `requirements.txt`
3. We deploy on Railway instantly!

🎁 **BONUS:** Get 2 FREE hours for each referral!

📞 **Admin:** {ADMIN_USERNAME}
🆔 **Your ID:** `{user.id}`

👇 **SELECT AN OPTION BELOW:**
    """
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """MAIN CALLBACK HANDLER - ALL BUTTON CLICKS"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # ========== START TRIAL ==========
    if data == "start_trial":
        try:
            with db.conn.cursor() as cur:
                trial_end = datetime.now() + timedelta(days=3)
                cur.execute("""
                    UPDATE users SET trial_end = %s, plan = 'trial'
                    WHERE user_id = %s
                """, (trial_end, user_id))
                db.conn.commit()
            
            await query.edit_message_text(
                text=f"""
✅ **FREE TRIAL ACTIVATED!**

🎉 Congratulations! Your 3-day free trial is now active.
📅 Trial Ends: {trial_end.strftime('%d %B %Y, %I:%M %p')}

🚀 **NEXT STEPS:**
1. Click *DEPLOY YOUR BOT* to upload your files
2. We'll host your bot instantly
3. Enjoy premium features for FREE

💡 **Tip:** Refer friends to get extra hours!
                """,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 DEPLOY BOT NOW", callback_data="deploy_bot")],
                    [InlineKeyboardButton("📊 GO TO DASHBOARD", callback_data="my_dashboard")]
                ])
            )
        except Exception as e:
            await query.edit_message_text("❌ Error starting trial. Contact admin.")
    
    # ========== DEPLOY BOT ==========
    elif data == "deploy_bot":
        deploy_guide = """
📦 **HOW TO DEPLOY YOUR BOT**

✅ **YOU NEED ONLY 2 FILES:**

1️⃣ **`bot.py`** - Your main bot script
2️⃣ **`requirements.txt`** - Python libraries list

📝 **FILE REQUIREMENTS:**

**bot.py (Example):**
```python
import os
from telegram import Update
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")  # ✅ CORRECT

async def start(update: Update, context):
    await update.message.reply_text("Hello!")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()                trial_end
            ))
            
            user = cur.fetchone()
            self.conn.commit()
            return user
    
    def add_referral(self, referrer_id, referred_id):
        """Add referral and give bonus"""
        try:
            with self.conn.cursor() as cur:
                # Check if already referred
                cur.execute("""
                    SELECT id FROM referrals 
                    WHERE referrer_id = %s AND referred_id = %s
                """, (referrer_id, referred_id))
                
                if cur.fetchone():
                    return False
                
                # Add referral record
                cur.execute("""
                    INSERT INTO referrals (referrer_id, referred_id)
                    VALUES (%s, %s)
                """, (referrer_id, referred_id))
                
                # Add 2 hours bonus
                cur.execute("""
                    UPDATE users 
                    SET bot_expiry = bot_expiry + INTERVAL '2 hours'
                    WHERE user_id = %s
                    RETURNING bot_expiry
                """, (referrer_id,))
                
                self.conn.commit()
                return True
        except Exception as e:
            logger.error(f"Referral error: {e}")
            self.conn.rollback()
            return False

# Initialize database
db = Database()

# ==================== BOT COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with referral system"""
    user = update.effective_user
    user_id = user.id
    
    # Check for referral parameter
    referrer_id = None
    if context.args and len(context.args) > 0:
        try:
            referrer_id = int(context.args[0])
        except:
            pass
    
    # Get or create user
    user_data = db.get_user(user_id)
    
    if not user_data:
        # New user registration
        user_data = {
            'id': user_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        db.create_user(user_data)
        
        # Process referral if any
        if referrer_id and referrer_id != user_id:
            if db.add_referral(referrer_id, user_id):
                await update.message.reply_text(
                    "🎉 You joined via referral link!\n"
                    "The referrer received 2 hours bonus."
                )
    
    # Send welcome message
    keyboard = [
        [InlineKeyboardButton("🚀 Start Trial", callback_data="start_trial")],
        [InlineKeyboardButton("💰 Buy Premium", callback_data="buy_premium")],
        [InlineKeyboardButton("📊 My Dashboard", callback_data="my_dashboard")],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="referral")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = f"""
🤖 **Welcome to Bot Hosting Service!**

👋 Hello {user.first_name}!

🚀 **Get Started:**
• 3 Days FREE Trial
• Premium Bot Features
• Easy Hosting on Railway
• 24/7 Support

🎁 **Referral Bonus:** Get 2 hours FREE for each friend you refer!

📊 **Your Status:** {'Active' if user_data else 'New User'}

👉 Select an option below:
    """
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /referral command"""
    user = update.effective_user
    user_id = user.id
    bot_username = context.bot.username
    
    # Generate referral link
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # Get referral stats
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) as total_refs FROM referrals 
            WHERE referrer_id = %s
        """, (user_id,))
        stats = cur.fetchone()
    
    total_refs = stats['total_refs'] if stats else 0
    total_bonus = total_refs * 2
    
    message = f"""
📢 **REFERRAL SYSTEM**

🔗 **Your Referral Link:**
`{referral_link}`

📊 **Your Statistics:**
• Total Referrals: {total_refs}
• Bonus Hours Earned: {total_bonus} hours
• Pending Bonus: {total_bonus} hours

🎁 **How it works:**
1. Share your unique link above
2. Friend joins using your link
3. You get **2 hours FREE instantly**
4. No limit on referrals!

💰 **Bonus Applied Automatically**
The 2 hours bonus is added to your bot runtime immediately.

📈 **Track your referrals in dashboard**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📋 Copy Link", callback_data="copy_ref_link"),
            InlineKeyboardButton("📊 My Stats", callback_data="ref_stats")
        ],
        [
            InlineKeyboardButton("🎁 Bonus History", callback_data="bonus_history"),
            InlineKeyboardButton("📢 Share Now", switch_inline_query=f"Join via my referral! {referral_link}")
        ],
        [
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def my_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user dashboard"""
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    if not user_data:
        await update.message.reply_text("Please use /start first")
        return
    
    # Calculate remaining time
    now = datetime.now()
    expiry = user_data['bot_expiry']
    
    if expiry:
        remaining = expiry - now
        if remaining.total_seconds() > 0:
            days = remaining.days
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            time_left = f"{days}d {hours}h {minutes}m"
        else:
            time_left = "EXPIRED"
    else:
        time_left = "Not set"
    
    # Get bot status
    bot_status = "🟢 Active" if user_data['bot_active'] else "🔴 Inactive"
    
    # Get referrals count
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) as ref_count FROM referrals 
            WHERE referrer_id = %s
        """, (user.id,))
        ref_stats = cur.fetchone()
    
    ref_count = ref_stats['ref_count'] if ref_stats else 0
    
    dashboard_msg = f"""
📊 **YOUR DASHBOARD**

👤 **Account Info:**
• User ID: `{user.id}`
• Username: @{user.username or 'N/A'}
• Plan: {user_data['plan_type'].upper()}

⏰ **Bot Status:**
• Status: {bot_status}
• Time Remaining: {time_left}
• Expiry: {expiry.strftime('%d/%m/%Y %H:%M') if expiry else 'N/A'}

📈 **Statistics:**
• Total Referrals: {ref_count}
• Bonus Hours: {ref_count * 2} hours
• Bot Active: {'Yes' if user_data['bot_active'] else 'No'}

🎯 **Quick Actions:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🤖 Start My Bot", callback_data="start_my_bot"),
            InlineKeyboardButton("⏰ Add Time", callback_data="add_time")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_dash"),
            InlineKeyboardButton("📞 Support", url=f"https://t.me/{ADMIN_USERNAME[1:]}")
        ],
        [
            InlineKeyboardButton("💰 Upgrade Plan", callback_data="upgrade_plan"),
            InlineKeyboardButton("🎁 Refer Friends", callback_data="referral")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        dashboard_msg,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium plans"""
    plans_msg = """
💰 **PREMIUM PLANS**

🚀 **BASIC PLAN** - $5/month
• 30 Days Bot Hosting
• Basic Features
• Email Support
• 1 Bot Deployment

🔥 **PRO PLAN** - $10/month
• 60 Days Bot Hosting
• All Premium Features
• Priority Support
• 3 Bot Deployments
• Custom Domain

💎 **ULTIMATE PLAN** - $20/month
• 90 Days Bot Hosting
• All Features Unlimited
• 24/7 Priority Support
• 10 Bot Deployments
• API Access
• Custom Bot Development

🎁 **SPECIAL OFFER:**
• Pay for 3 months, get 1 month FREE!
• Refer 5 friends, get 1 month FREE!

👉 **How to Purchase:**
1. Select a plan below
2. Contact admin for payment
3. Activate instantly after payment

📞 **Contact Admin:** @CyperXploit
    """
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Basic - $5", callback_data="plan_basic"),
            InlineKeyboardButton("🔥 Pro - $10", callback_data="plan_pro")
        ],
        [
            InlineKeyboardButton("💎 Ultimate - $20", callback_data="plan_ultimate")
        ],
        [
            InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME[1:]}"),
            InlineKeyboardButton("💬 Payment Info", callback_data="payment_info")
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        plans_msg,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "start_trial":
        await start_trial(query, user_id)
    
    elif data == "referral":
        await referral_command(update, context)
    
    elif data == "my_dashboard":
        await my_dashboard(update, context)
    
    elif data == "buy_premium":
        await buy_premium(update, context)
    
    elif data == "copy_ref_link":
        await query.edit_message_text(
            text="✅ **Link copied to clipboard!**\n\nShare this with your friends:\n`https://t.me/your_bot?start={user_id}`\n\nEach referral gives you 2 hours FREE!",
            parse_mode='Markdown'
        )
    
    elif data == "contact_admin":
        await query.edit_message_text(
            text=f"📞 **Contact Admin:**\n\n"
                 f"Username: {ADMIN_USERNAME}\n"
                 f"ID: {ADMIN_ID}\n\n"
                 f"Send your User ID and plan choice.\n"
                 f"✅ Fast activation after payment.",
            parse_mode='Markdown'
        )

async def start_trial(query, user_id):
    """Start user trial bot"""
    user_data = db.get_user(user_id)
    
    if not user_data:
        await query.edit_message_text("Please use /start first")
        return
    
    # Check if trial already started
    if user_data['trial_start']:
        await query.edit_message_text(
            "🎉 **Your trial is already active!**\n\n"
            f"Started: {user_data['trial_start'].strftime('%d/%m/%Y')}\n"
            f"Expires: {user_data['trial_end'].strftime('%d/%m/%Y')}\n\n"
            "Check /dashboard for details."
        )
        return
    
    # Start trial
    with db.conn.cursor() as cur:
        trial_start = datetime.now()
        trial_end = trial_start + timedelta(days=3)
        
        cur.execute("""
            UPDATE users 
            SET trial_start = %s, trial_end = %s, bot_expiry = %s
            WHERE user_id = %s
        """, (trial_start, trial_end, trial_end, user_id))
        
        db.conn.commit()
    
    await query.edit_message_text(
        "🎉 **Trial Started Successfully!**\n\n"
        "✅ 3 Days FREE Trial Activated\n"
        "⏰ Expires: " + trial_end.strftime('%d/%m/%Y %H:%M') + "\n\n"
        "🚀 **Next Steps:**\n"
        "1. Go to /dashboard\n"
        "2. Deploy your bot\n"
        "3. Start using premium features\n\n"
        "💡 **Tip:** Refer friends to get FREE hours!"
    )

# ==================== ADMIN COMMANDS ====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel - only for admin"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Access Denied!")
        return
    
    with db.conn.cursor() as cur:
        # Get stats
        cur.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cur.fetchone()['total_users']
        
        cur.execute("SELECT COUNT(*) as active_trials FROM users WHERE trial_end > NOW()")
        active_trials = cur.fetchone()['active_trials']
        
        cur.execute("SELECT COUNT(*) as premium_users FROM users WHERE premium_status = TRUE")
        premium_users = cur.fetchone()['premium_users']
        
        cur.execute("SELECT COUNT(*) as total_refs FROM referrals")
        total_refs = cur.fetchone()['total_refs']
    
    admin_msg = f"""
👑 **ADMIN PANEL**

📊 **Statistics:**
• Total Users: {total_users}
• Active Trials: {active_trials}
• Premium Users: {premium_users}
• Total Referrals: {total_refs}
• Revenue Today: $0.00

🔧 **Quick Actions:**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📋 User List", callback_data="admin_users"),
            InlineKeyboardButton("💰 Payments", callback_data="admin_payments")
        ],
        [
            InlineKeyboardButton("🤖 Bots Status", callback_data="admin_bots"),
            InlineKeyboardButton("🎁 Add Bonus", callback_data="admin_add_bonus")
        ],
        [
            InlineKeyboardButton("📊 Full Stats", callback_data="admin_stats"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="admin_refresh")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        admin_msg,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(CommandHandler("dashboard", my_dashboard))
    application.add_handler(CommandHandler("premium", buy_premium))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start bot
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
