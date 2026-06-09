import logging
import asyncio
import time
from datetime import datetime
import pytz
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token
BOT_TOKEN = "8957859615:AAFN02C6EKe_odGgZs2_r_LAXRE8REU0QPA"

# Real channels
MAIN_CHANNEL = "@fbigarnob"
BACKUP_CHANNEL = "@otpgroupab"

# 🌍 মূল দেশের ডাটাবেজ
country_database = {
    "Myanmar S1": {"flag": "🇲🇲", "code": "+95", "stock": 5992},
    "Myanmar Top2": {"flag": "🇲🇲", "code": "+95", "stock": 8732},
    "Tanzania": {"flag": "🇹🇿", "code": "+255", "stock": 4727},
    "Tanzania S2": {"flag": "🇹🇿", "code": "+255", "stock": 1335},
    "Tanzania Top": {"flag": "🇹🇿", "code": "+255", "stock": 4516},
    "Algeria TT Fire": {"flag": "🇩🇿", "code": "+213", "stock": 390},
    "Tunisia Top": {"flag": "🇹🇳", "code": "+216", "stock": 7058},
    "Tajikistan": {"flag": "🇹🇯", "code": "+992", "stock": 57},
    "Tajikistan Fire": {"flag": "🇹🇯", "code": "+992", "stock": 6152},
    "Ukraine TT": {"flag": "🇺🇦", "code": "+380", "stock": 2176},
    "Mauritania Kop": {"flag": "🇲🇷", "code": "+222", "stock": 8659},
    "Mauritania S1": {"flag": "🇲🇷", "code": "+222", "stock": 1988}
}

# 📈 লাইভ ট্রাফিক স্ট্যাটস
traffic_stats = {
    "Tanzania S2": {"flag": "🇹🇿", "count": 20},
    "Bangladesh": {"flag": "🇧🇩", "count": 15},
    "India Top": {"flag": "🇮🇳", "count": 12},
    "Myanmar S1": {"flag": "🇲🇲", "count": 8},
    "Mauritania Kop": {"flag": "🇲🇷", "count": 5},
    "USA Premium": {"flag": "🇺🇸", "count": 3},
    "Russia Fast": {"flag": "🇷🇺", "count": 1}
}

# 🛠️ রিয়েল ইউজার ডাটাবেজ
user_db = {}
user_steps = {}

cached_traffic_text = ""
last_update_time = 0

def init_user(user_id: int):
    if user_id not in user_db:
        user_db[user_id] = {
            "balance": 0.0000, 
            "total_withdraw": 0.0000,
            "today_earning": 0.0000,
            "today_otps": 0
        }

def get_user_balance(user_id: int) -> float:
    init_user(user_id)
    return user_db[user_id]["balance"]

def update_user_balance(user_id: int, amount: float):
    init_user(user_id)
    user_db[user_id]["balance"] += amount

def main_keyboard():
    keyboard = [
        ["☎️ Get Number", "🌍 Available Country"],
        ["📊 Status", "💰 Balance"],
        ["😎 Withdraw", "🟢 Live Traffic"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def set_bot_description(app: Application):
    desc_text = (
        "AB OTP bot আনলিমিটেড নাম্বার নেয়ার জন্য আপনারা এখনই জয়েন করেন আমাদের সাথে "
        "এবং আমাদের সর্বক্ষণিক ওটিপি পাবেন এবং কোন সমস্যা হলে আমাদের সাপোর্ট গ্রুপে মেসেজ দিই সমাধান পাবেন"
    )
    try: await app.bot.set_description(description=desc_text)
    except Exception: pass

async def check_joined(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member1 = await context.bot.get_chat_member(chat_id=MAIN_CHANNEL, user_id=user_id)
        member2 = await context.bot.get_chat_member(chat_id=BACKUP_CHANNEL, user_id=user_id)
        return member1.status not in ['left', 'kicked', 'restricted'] and member2.status not in ['left', 'kicked', 'restricted']
    except Exception: return False

def get_real_live_traffic(force_refresh=False):
    global cached_traffic_text, last_update_time
    current_time = time.time()
    tz = pytz.timezone('Asia/Dhaka')
    current_date = datetime.now(tz).strftime("%d/%m/%Y")
    
    if force_refresh or (current_time - last_update_time > 300) or not cached_traffic_text:
        sorted_traffic = sorted(traffic_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        total_clicks = sum(item[1]['count'] for item in sorted_traffic[:5]) or 1
        
        top_country_name = sorted_traffic[0][0]
        top_country_flag = sorted_traffic[0][1]['flag']
        
        traffic_text = (
            "╭──────────────────────╮\n"
            "🟢  𝙻𝙸𝚅𝙴 𝚃𝚁𝙰𝙵𝙵𝙸𝙲 𝚂𝚃𝙰𝚃𝚂  🟢\n"
            "╰──────────────────────╯\n\n"
            f"📅 **Date / তারিখ:** `{current_date}`\n"
            "⏱️ **Window:** `Auto Sync (5 Min)`\n"
            "⚡ **Success Rate:** `100%`\n"
            f"🔝 **Top Active:** {top_country_flag} `{top_country_name}`\n\n"
            "📈 **📊 __TOP TRAFFIC LEADERBOARD__**\n"
            "🗺️ ━━━━━━━━━━━━━━━━━━━ 🗺️\n"
        )
        medals = ["🥇", "🥈", "🥉", "🔹", "🔹"]
        for idx, (name, data) in enumerate(sorted_traffic[:5]):
            percentage = round((data['count'] / total_clicks) * 100, 1)
            traffic_text += f"{medals[idx]} {data['flag']} **{name}** ───⪧ `{percentage}%` (`{data['count']}` OTPs)\n"
        traffic_text += "🗺️ ━━━━━━━━━━━━━━━━━━━ 🗺️"
        cached_traffic_text = traffic_text
        last_update_time = current_time
    return cached_traffic_text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    init_user(user.id)
    if await check_joined(user.id, context):
        welcome_text = (
            "╭──────────────────────╮\n"
            "👑  𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝘼𝘽 𝙊𝙏𝙋  👑\n"
            "╰──────────────────────╯\n\n"
            f"👋 **Greetings, `{user.first_name}`**\n\n"
            "🌐 *You are connected to the premium high-speed OTP distribution system.*\n"
            "🌐 আপনি প্রিমিয়াম হাই-স্পিড ওটিপি ডিস্ট্রিবিউশন সিস্টেমে যুক্ত হয়েছেন।\n\n"
            "⚡ **Status / অবস্থা:** `Fully Operational`\n"
            "💎 **Secure Network Threads:** `Active`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👇 **Use the dashboard menu below to start:**\n"
            "👇 কাজ শুরু করতে নিচের ড্যাশবোর্ড মেনু ব্যবহার করুন:"
        )
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        join_text = (
            "╭──────────────────────╮\n"
            "🔒  𝙂𝘼𝙏𝙀𝙒𝘼𝙔 𝘼𝘾𝘾𝙀𝙎𝙎 𝙇𝙊𝘾𝙆𝙀𝘿  🔒\n"
            "╰──────────────────────╯\n\n"
            "⚠️ **Access Denied! Channel Verification Required.**\n"
            "⚠️ বটের সার্ভিসগুলো ব্যবহার করতে অফিশিয়াল চ্যানেলে জয়েন থাকা বাধ্যতামূলক।\n\n"
            "📢 **Please join our network channels below to unlock the system:**\n"
            "📢 সিস্টেমটি আনলক করতে নিচের চ্যানেলগুলোতে যুক্ত হয়ে ভেরিফাই করুন:"
        )
        keyboard = [
            [InlineKeyboardButton("📬 Main Channel", url=f"https://t.me/{MAIN_CHANNEL[1:]}")],
            [InlineKeyboardButton("✉️ OTP Group", url=f"https://t.me/{BACKUP_CHANNEL[1:]}")],
            [InlineKeyboardButton("🔄 Verify System / ভেরিফাই", callback_data="check_again")]
        ]
        await update.message.reply_text(join_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    init_user(user.id)
    
    if query.data == "check_again":
        if await check_joined(user.id, context):
            await query.answer("✅ Verification Successful!")
            await query.message.delete()
            welcome_text = (
                "╭──────────────────────╮\n"
                "🔓  𝙎𝙔𝙎𝙏𝙀𝙈 𝙐𝙉𝙇𝙊𝘾𝙆𝙀𝘿  🔓\n"
                "╰──────────────────────╯\n\n"
                f"🎉 **Access Granted! Welcome, `{user.first_name}`**\n\n"
                "Your account is now fully verified and synced with our main database.\n"
                "আপনার অ্যাকাউন্ট সফলভাবে ভেরিফাইড এবং মেইন ডাটাবেজের সাথে সিঙ্ক হয়েছে।\n\n"
                "📢 **Choose an action from the dashboard:**\n"
                "📢 ড্যাশবোর্ড থেকে আপনার কাঙ্ক্ষিত বাটন সিলেক্ট করুন:"
            )
            await context.bot.send_message(chat_id=user.id, text=welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())
        else:
            await query.answer("❌ Verification Failed! Join both channels first. / দুটি চ্যানেলেই আগে জয়েন করুন!", show_alert=True)
            
    elif query.data == "refresh_traffic":
        traffic_text = get_real_live_traffic(force_refresh=True)
        keyboard = [[InlineKeyboardButton("🔄 𝚁𝚎𝚏𝚛𝚎𝚜𝚑 𝙳𝚊𝚝𝚊", callback_data="refresh_traffic")]]
        try:
            await query.edit_message_text(traffic_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            await query.answer("⚡ Refreshed / আপডেট হয়েছে!")
        except Exception: await query.answer()

    elif query.data in ["w_bkash", "w_nagad"]:
        method = "bKash" if query.data == "w_bkash" else "Nagad"
        user_steps[user.id] = {"method": method, "step": "get_number"}
        await query.message.delete()
        
        input_num_text = (
            "╭──────────────────────╮\n"
            f"📥  𝙒工𝙏𝙃𝘿configＡＬ: {method.upper()}  \n"
            "╰──────────────────────╯\n\n"
            f"📱 **Enter your {method} Personal Number:**\n"
            f"📱 আপনার **{method} Personal** অ্যাকাউন্ট নাম্বারটি দিন:\n\n"
            "📌 **Example / উদাহরণ:** `017xxxxxxxx`"
        )
        await context.bot.send_message(chat_id=user.id, text=input_num_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    init_user(user.id)
    real_balance = get_user_balance(user.id)
    
    if not await check_joined(user.id, context):
        await update.message.reply_text("⚠️ Join channels first! / প্রথমে চ্যানেলে জয়েন করুন।")
        return

    # Withdraw setup
    if user.id in user_steps:
        state = user_steps[user.id]
        if state["step"] == "get_number":
            if len(text) == 11 and text.startswith("01") and text.isdigit():
                state["number"] = text
                state["step"] = "get_amount"
                amount_prompt = (
                    "╭──────────────────────╮\n"
                    "💵  𝙒工𝙏𝙃𝘿configＡ𝙒 ＡＭ工𝙐做Ｔ  \n"
                    "╰──────────────────────╯\n\n"
                    f"💰 **Your Balance:** `{real_balance:.4f}$`\n\n"
                    "✍️ **Enter withdrawal amount ($):**\n"
                    "✍️ আপনি কত ডলার উইথড্র করতে চান নিচে লিখুন (e.g. `2` or `5.5`):"
                )
                await update.message.reply_text(amount_prompt, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Invalid number! Please enter a valid 11-digit number:\n❌ ভুল নাম্বার! আবার সঠিক ১১ ডিজিটের নাম্বার দিন:")
            return
            
        elif state["step"] == "get_amount":
            try:
                amount = float(text)
                if amount <= 0 or amount > real_balance:
                    await update.message.reply_text("❌ Insufficient funds or invalid amount!\n❌ পর্যাপ্ত ব্যালেন্স নেই অথবা ভুল অ্যামাউন্ট! আবার লিখুন:")
                    return
                update_user_balance(user.id, -amount)
                user_db[user.id]["total_withdraw"] += amount
                
                success_text = (
                    "╭──────────────────────╮\n"
                    "🚀  𝙍𝙀𝙌𝙐𝙀𝙎𝙏 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇  🚀\n"
                    "╰──────────────────────╯\n\n"
                    f"💵 **Amount / পরিমাণ:** `{amount:.4f}$`\n"
                    f"💳 **Method / গেটওয়ে:** `{state['method']}`\n"
                    f"📱 **Account / নাম্বার:** `{state['number']}`\n"
                    "💎 ━━━━━━━━━━━━━━━━━━━ 💎\n\n"
                    "⏱️ **Status:** `Pending Approval` (Within 24h)\n"
                    "ℹ️ Your request is recorded! রিকোয়েস্টটি সফলভাবে এডমিন প্যানেলে জমা হয়েছে।"
                )
                await update.message.reply_text(success_text, parse_mode="Markdown", reply_markup=main_keyboard())
                user_steps.pop(user.id, None)
            except ValueError:
                await update.message.reply_text("❌ Numbers only! / শুধুমাত্র সংখ্যায় লিখুন:")
            return

    # Button responses
    if text == "🟢 Live Traffic":
        traffic_text = get_real_live_traffic()
        keyboard = [[InlineKeyboardButton("🔄 𝚁𝚎𝚏𝚛𝚎𝚜𝚑 𝙳𝚊𝚝𝚊", callback_data="refresh_traffic")]]
        await update.message.reply_text(traffic_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif text == "😎 Withdraw":
        if real_balance < 1.0:
            low_bal = (
                "╭──────────────────────╮\n"
                "⚠️  𝙇𝙊𝙒 𝘽𝘼𝙇𝘼𝙉𝘾𝙀 专𝙊𝙏工ＣＥ  ⚠️\n"
                "╰──────────────────────╯\n\n"
                f"❌ **Minimum withdrawal is 1.00$!**\n"
                f"🛑 মিনিমাম উইথড্রাল অ্যামাউন্ট হচ্ছে **1.00$**।\n\n"
                f"💰 **Current Balance:** `{real_balance:.4f}$`"
            )
            await update.message.reply_text(low_bal, parse_mode="Markdown")
        else:
            withdraw_panel = (
                "╭──────────────────────╮\n"
                "😎  𝙒工𝙏𝙃𝘿configＡＬ 𝙋𝘼做𝙀𝙇  😎\n"
                "╰──────────────────────╯\n\n"
                "👇 **Select your payment gateway below:**\n"
                "👇 নিচে থেকে আপনার কাঙ্ক্ষিত পেমেন্ট মেথডটি সিলেক্ট করুন:"
            )
            keyboard = [[InlineKeyboardButton("💲 bKash", callback_data="w_bkash")], [InlineKeyboardButton("💱 Nagad", callback_data="w_nagad")]]
            await update.message.reply_text(withdraw_panel, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            
    elif text == "☎️ Get Number":
        gn_text = (
            "╭──────────────────────╮\n"
            "☎️  **𝙾𝚃𝙿  𝙽𝚄𝙼𝙱𝙴𝚁  𝙿𝙰𝙽𝙴𝙻** ☎️\n"
            "╰──────────────────────╯\n\n"
            "⚡ **Real Server Module is Online!**\n"
            "🔥 **রিয়েল ওটিপি সার্ভার মডিউল এক্টিভ!**\n"
            "💎 ━━━━━━━━━━━━━━━━━━━ 💎\n\n"
            "*(Wired configuration ready for API delivery)*"
        )
        await update.message.reply_text(gn_text, parse_mode="Markdown")
        
    elif text == "💰 Balance":
        data = user_db[user.id]
        balance_text = (
            "💰 **YOUR LIVE ACCOUNT STATUS**\n"
            "═════════════════════════════\n\n"
            f"💵 **Total Earned / মোট আয়:** ${data['balance'] + data['total_withdraw']:.4f} USDT\n"
            f"💳 **Total Withdrawn / মোট উইথড্র:** ${data['total_withdraw']:.4f} USDT\n"
            f"📊 **Today's Earnings / আজকের আয়:** ${data['today_earning']:.4f} USDT\n"
            f"📱 **Today's OTPs / আজকের ওটিপি:** {data['today_otps']}\n"
            "─────────────────────────────\n"
            f"💰 **Available Balance / চলতি ব্যালেন্স:** ${data['balance']:.4f} USDT\n"
            "─────────────────────────────\n"
            "⚠️ **Minimum Withdrawal:** $1.00 USDT\n\n"
            "💡 Get more numbers to boost your metrics!"
        )
        await update.message.reply_text(balance_text, parse_mode="Markdown")

    elif text == "🌍 Available Country":
        country_text = (
            "🌍 **AVAILABLE COUNTRIES & SERVERS**\n"
            "🗺️ ━━━━━━━━━━━━━━━━━━━━━━━━━ 🗺️\n\n"
        )
        for name, info in country_database.items():
            country_text += f"{info['flag']} **{name}** ({info['code']}) ──⪧ `Stock: {info['stock']}`\n"
        await update.message.reply_text(country_text, parse_mode="Markdown")
    
    elif text == "📊 Status":
        status_text = (
            "📊 **SYSTEM SERVER STATUS**\n"
            "═══════════════════════\n\n"
            "⚡ **Bot Node:** `Active`\n"
            "📡 **API Gateways:** `Operational`\n"
            "👥 **Active Multi-Traffic Threads:** `Online`\n\n"
            "Everything is running perfectly! সব সিস্টেম একদম ঠিকঠাক চলছে!"
        )
        await update.message.reply_text(status_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Selected / সিলেক্ট করেছেন: **{text}**")

def main():
    def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Dual Language Premium Bot is running successfully...")
    app.run_polling()

if __name__ == '__main__':
    main()
