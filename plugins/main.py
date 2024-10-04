import re, os, time, sys, shutil, psutil, asyncio

from config import Config, Txt
from pyrogram import Client, filters, enums 
from utils import humanbytes, get_time


@Client.on_message(filters.private & filters.command('start') & filters.user(Config.ADMINS))
async def start_bot(client, message):
    await message.reply(text=Txt.START)
        
@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMINS) & filters.private)
async def status_handler(b, m):
    total, used, free = shutil.disk_usage(".")
    ram = psutil.virtual_memory()
    start_t = time.time()
    sts = await m.reply_text("ᴡᴀɪᴛ..")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    stats = Txt.STATS.format(
        uptime = get_time(time.time() - b.uptime),
        ping = f"{time_taken_s:.3f} ᴍꜱ",
        total = humanbytes(total),
        used = humanbytes(used),
        free = humanbytes(free),
        t_ram = humanbytes(ram.total),
        u_ram = humanbytes(ram.used),
        f_ram = humanbytes(ram.available),
        cpu_usage = psutil.cpu_percent(),
        ram_usage = psutil.virtual_memory().percent,
        disk_usage = psutil.disk_usage('/').percent,
        sent = humanbytes(psutil.net_io_counters().bytes_sent),
        recv = humanbytes(psutil.net_io_counters().bytes_recv),
    )
    await sts.edit(stats, parse_mode=enums.ParseMode.MARKDOWN) 

@Client.on_message(filters.command("restart") & filters.user(Config.ADMINS))
async def restarted_bot(b, m):
    await m.reply("Bot Restarting......")
    try: os.remove('log.txt')
    except: pass
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("update") & filters.user(Config.ADMINS))
async def update_bot(c, m):
    try:
        os.system("git pull")
        await m.reply_text("ᴜᴩᴅᴀᴛᴇᴅ & ʀᴇꜱᴛᴀʀᴛɪɴɢ...")
        os.execl(sys.executable, sys.executable, "bot.py")
    except Exception as e:
        await m.reply(e)
        
@Client.on_callback_query(filters.regex(r'^stop_btn$'))
async def stop_button(client, cb):
    await cb.answer('stopping......')
    await cb.message.edit('stropping......')
    os.execl(sys.executable, sys.executable, *sys.argv)
    
    
    