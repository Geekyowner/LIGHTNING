import logging
import logging.config
import warnings
from pyrogram import Client, idle
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from pytz import timezone
from datetime import datetime
import asyncio
from plugins.web_support import web_server
from plugins.file_rename import app
import pyromod

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client):

    def __init__(self):
        # Use the STRING_SESSION if available, otherwise use API ID and API HASH for bot login
        if Config.STRING_SESSION:
            super().__init__(
                session_name=Config.STRING_SESSION,  # Using STRING_SESSION for session login
                api_id=Config.STRING_API_ID,
                api_hash=Config.STRING_API_HASH,
                workers=200,
                plugins={"root": "plugins"},
                sleep_threshold=15,
            )
        else:
            super().__init__(
                name="ANIFLIX",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=Config.BOT_TOKEN,
                workers=200,
                plugins={"root": "plugins"},
                sleep_threshold=15,
            )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.force_channel = Config.FORCE_SUB
        
        if Config.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(Config.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                logging.warning(e)
                logging.warning("Make Sure Bot admin in force sub channel")
                self.force_channel = None

        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, Config.PORT).start()
        logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")

        for id in Config.ADMIN:
            try:
                await self.send_message(id, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")
            except:
                pass

        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
        
                # Check if STRING_SESSION is valid and premium
                if Config.STRING_SESSION:
                    session_valid = True
                    try:
                        user = await self.get_me()  # This call will raise an error if the session is invalid
                        is_premium = user.is_premium if hasattr(user, 'is_premium') else False
                        session_status = "✅ Valid Premium" if is_premium else "✅ Valid Non-Premium"
                    except Exception as e:
                        logging.error(f"Invalid session: {e}")
                        session_valid = False
                        session_status = "❌ Invalid STRING_SESSION"
                else:
                    session_valid = False
                    session_status = "No STRING_SESSION provided"
        
                # Send the log message with session status and premium information
                await self.send_message(
                    Config.LOG_CHANNEL, 
                    f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!__**\n\n"
                    f"📅 Dᴀᴛᴇ : `{date}`\n"
                    f"⏰ Tɪᴍᴇ : `{time}`\n"
                    f"🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n"
                    f"🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`\n"
                    f"💼 Sᴇssɪᴏɴ Sᴛᴀᴛᴜs : `{session_status}`"
                )
            except Exception as e:
                logging.error(f"Error sending message to log channel: {e}")
                print("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪs Iɴ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ")


    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")

bot_instance = Bot()

def main():
    async def start_services():
        await asyncio.gather(
            app.start(),        # Start the web server or any other service
            bot_instance.start()  # Start the bot instance
        )
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_services())
    loop.run_forever()

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="There is no current event loop")
    main()
