import os
import traceback
import logging

from pyrogram import Client
from pyrogram import StopPropagation, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from handlers.broadcast import broadcast
from handlers.check_user import handle_user_status
from handlers.database import Database

LOG_CHANNEL = config.LOG_CHANNEL
AUTH_USERS = config.AUTH_USERS
DB_URL = config.DB_URL
DB_NAME = config.DB_NAME

db = Database(DB_URL, DB_NAME)


Bot = Client(
    "BroadcastBot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
)

@Bot.on_message(filters.private)
async def _(bot, cmd):
    await handle_user_status(bot, cmd)
@Bot.on_message(filters.command("start") & filters.private)
async def startprivate(client, message):
    # return
    chat_id = message.from_user.id
    if not await db.is_user_exist(chat_id):
        data = await client.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        if LOG_CHANNEL:
            await client.send_message(
                LOG_CHANNEL,
                f"#مستخدم جديد: \n\nمستخدم جديد [{message.from_user.first_name}](tg://user?id={message.from_user.id}) داس ستارت @{BOT_USERNAME} !!",
            )

    raise StopPropagation

@Bot.on_message(filters.private & filters.command("stats"))
async def sts(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    await m.reply_text(
        text=f"**إجمالي المستخدمين في قاعدة البيانات 📂:** `{await db.total_users_count()}`\n\n**إجمالي المستخدمين مع تمكين الإخطار 🔔:** `{await db.total_notif_users_count()}`",
        parse_mode="Markdown",
        quote=True
    )

Bot.run()
