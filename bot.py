import os, sys, asyncio, logging 
from pyrogram import Client
from config import Config

logging.getLogger(__name__)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="FwdBot",
            bot_token=Config.BOT_TOKEN,
            api_hash=Config.API_HASH,
            api_id=Config.API_ID,
            plugins=dict(root='plugins')
        )
        
    async def start(self):
        try:
            await super().start()
            self.me = await self.get_me()
            # Userbot
            self.userbot = None
            try:
                if Config.USER_SESSION:
                    self.userbot = Client(name='UserBot', session_string=Config.USER_SESSION, app_version='ForwidBot')           
                    await self.userbot.start()
                    UserMe = await self.userbot.get_me()
                    logging.info(f'UserBot @{UserMe.username} started ✨')
                else:
                    logging.warning('add user session to enable userbot ➡️')
            except Exception as e:
                logging.error(e)
            logging.info(f"@{self.me.username} started!")
            for id in Config.ADMINS:
                try: await self.send_message(id, "Bot Restarted ✓")
                except: pass
            
        except Exception as e:
            logging.error(e)
            if self.is_connected: await self.send_message(7157319028, e)
            await asyncio.sleep(10)
            os.system("git pull")
            os.execl(sys.executable, sys.executable, "bot.py")

    
Bot().run()    
