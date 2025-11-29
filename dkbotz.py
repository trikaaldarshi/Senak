from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
import asyncio
import re
import os

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "your_api_hash")

ALL_LINKS = os.getenv("ALL_LINKS", True)
TELEGRAM_USERNAME = os.getenv("TELEGRAM_USERNAME", True)
JOIN_HIDER = os.getenv("JOIN_HIDER", True)
FILTER_DOMAIN = os.getenv("FILTER_DOMAIN", True)

LOG_CHANNEL = os.getenv("LOG_CHANNEL")
if LOG_CHANNEL and LOG_CHANNEL.startswith("-100"):
    LOG_CHANNEL = int(LOG_CHANNEL)

UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/shuklaxd")
# ==========================================

# ================= Message =================
START_MESSAGE = """
👋 Hello {user}!

🤖 I Am **Group Guard Bot**, Your Personal Security System For Telegram Groups.

🚨 **Features:**
━━━━━━━━━━━━━━━━━━━
🔒 Remove Unwanted **Buttons** (Inline/Reply)  
🌐 Block **Links** (Http/Https/Www)  
🏷 Delete **Domain Mentions** (.Com, .In, .Org, Etc.)  
📛 Block **@Usernames** From Messages  
🚪 Hide **Join/Leave System Messages**  
🤖 Remove Spammy **Bot Messages** (If Non-Admin)  
📝 Log Deleted Content If `LOG_CHANNEL` Enabled  
━━━━━━━━━━━━━━━━━━━

✅ **Group Admins & Owner Are Always Safe.**

⚡ Keep Your Group **Clean, Safe, And Spam-Free** With Me!
"""
# ==========================================


URL_REGEX = re.compile(
    r"(https?:\/\/(?:www\.)?|www\.)"
    r"([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}"
    r"(\/[^\s]*)?"
)

DOMAIN_REGEX = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+(com|in|org|net|xyz|info|co|gov|edu|ai|app|shop)\b")

USERNAME_REGEX = re.compile(r"@[\w\d_]{3,}")

DKBOTZ = Client(
    "dkbotz_group_security_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)


@DKBOTZ.on_message(filters.command("start"))
async def dkbotz_start_cmd(client, message: Message):
    user = message.from_user.first_name if message.from_user else "User"
    await message.reply_text(START_MESSAGE.format(user=user),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📢 Join Update Channel", url=UPDATE_CHANNEL)]]
        )
    )

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return True
    except Exception:
        return False
    return False

@DKBOTZ.on_message(filters.group)
async def dkbotz_guard_group(client, message: Message):
    user = message.from_user.mention if message.from_user else "System"
    original_text = message.text or message.caption or ""

    if JOIN_HIDER and not message.from_user:
        try:
            await message.delete()
            reason = "🚪 Join/Leave message"
            if LOG_CHANNEL:
                await client.send_message(LOG_CHANNEL, f"🗑 Deleted Message\nUser: {user}\nReason: {reason}\nChat: {message.chat.title}")
        except:
            pass
        return

    if not message.from_user:
        return

    reason = None

    if await is_admin(client, message.chat.id, message.from_user.id):
        return

    if message.from_user.is_bot:
        reason += " (🤖 Bot detected)"
        
    elif message.reply_markup:
        reason = "❌ Buttons are not allowed here!"

    elif ALL_LINKS and URL_REGEX.search(original_text):
        reason = "❌ Links are not allowed here!"

    elif FILTER_DOMAIN and DOMAIN_REGEX.search(original_text):
        reason = "❌ Domain mentions are not allowed here!"

    elif TELEGRAM_USERNAME and USERNAME_REGEX.search(original_text):
        reason = "❌ Telegram usernames are not allowed here!"

    if not reason:
        return

    try:
        await message.delete()
        warn = await message.reply_text(f"⚠️ **Warning {user}**\n\n{reason}\n\n🚫 Your message has been removed by **Group Security Bot**.")
        await asyncio.sleep(10)
        await warn.delete()
    except Exception:
        pass

    if LOG_CHANNEL:
        try:
            await client.send_message(LOG_CHANNEL, f"🗑 **Deleted Message Log**\n👤 User: {user}\n💬 Chat: {message.chat.title}\n⚠️ Reason: {reason}\n📝 Original: {original_text[:300]}")
        except:
            pass

DKBOTZ.run()
