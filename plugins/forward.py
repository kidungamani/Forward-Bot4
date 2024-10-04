import re, math, os, sys, asyncio

from config import Config, Txt
from utils import iter_messages
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified, MessageNotModified

lock = asyncio.Lock()
 
@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def forward(bot, message):
    if lock.locked():
        return await message.reply("Already one task is running...")
    
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match: return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric(): chat_id  = int(("-100" + chat_id))
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else: return

    method = await bot.ask(message.chat.id, text="send the method `user` or `bot`", filters=filters.text)
    client = bot
    if method.text == 'user':
        client = bot.userbot 
        if not bot.userbot: 
            return await message.reply('Userbot not founded. process cancelled')
            
    try:  await client.get_chat(chat_id)
    except ChannelInvalid:  return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified): return await message.reply('Invalid Link specified.')
    except Exception as e: return await message.reply(f'Errors - {e}')
    try: k = await client.get_messages(chat_id, last_msg_id)
    except: return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
    if k.empty: return await message.reply('This may be group and iam not a admin of the group.')
    
    skip = await bot.ask(message.chat.id, text="send skip number or send `0`", filters=filters.text)
    current = int(skip.text)
    total_files = 0
    deleted = 0
    errors = 0
    
    buttons = [[InlineKeyboardButton('🚫 STOP', callback_data='stop_btn')]]
    sts = await message.reply(
        text=f"Forward Starting...\n\nSuccess: `{total_files}`\nDeletedFils: `{deleted}`\nErros `{errors}`",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    async with lock:
        try:
            async for msg in iter_messages(client, chat_id, last_msg_id, current):
                try:
                    if msg.empty:
                        deleted += 1
                        continue
                    await client.copy_message(chat_id=Config.TO_CHANNEL, from_chat_id=chat_id, message_id=msg.id)
                    total_files += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.copy_message(chat_id=Config.TO_CHANNEL, from_chat_id=chat_id, message_id=msg.id)
                    total_files += 1    
                except Exception as e:
                    error += 1
                    continue
                if total_files % 10 == 0:
                    try: await sts.edit_text(f"Forwarding...\n\nSuccess: `{total_files}`\nDeletedFils: `{deleted}`\nErros `{errors}`", reply_markup=InlineKeyboardMarkup(buttons))
                    except: pass
        except Exception as e:
            try: await sts.edit_text(f"Error While Forward!\n\nError: {e}\n\nSuccess: `{total_files}`\nDeletedFils: `{deleted}`\nErros `{errors}`", reply_markup=InlineKeyboardMarkup(buttons))
            except: pass
        
    await sts.edit(f"Successful ✅ \n\nSuccess: `{total_files}`\nDeletedFils: `{deleted}`\nErros `{errors}`")
        
