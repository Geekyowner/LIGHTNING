import logging
import logging.config
import warnings
import os
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from pytz import timezone
from datetime import datetime
import asyncio
from plugins.web_support import web_server
from plugins.file_rename import app

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="ANIFLIX",
            api_id=Config.STRING_API_ID,
            api_hash=Config.STRING_API_HASH,
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

        # Checking premium status of the session string
        session_string = Config.STRING_SESSION  # Use the session string from config
        if session_string:
            is_premium = await self.check_if_premium(session_string)
            logging.info(f"Session premium status: {is_premium}")
        else:
            logging.info("No session string provided.")

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
                await self.send_message(Config.LOG_CHANNEL, f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n📅 Dᴀᴛᴇ : `{date}`\n⏰ Tɪᴍᴇ : `{time}`\n🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`</b>")
            except:
                print("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪꜱ Iɴ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ")

    async def check_if_premium(self, session_string):
        """
        Check if the session string belongs to a premium account.
        """
        try:
            # Initialize a temporary client with the session string
            temp_client = Client("premium_check", session_string=session_string)
            await temp_client.start()
            
            # Get the user's own information
            user = await temp_client.get_me()

            # Check if the user is premium
            is_premium = user.is_premium  # This attribute tells if the user has premium status

            # Stop the temporary client
            await temp_client.stop()

            return is_premium
        except Exception as e:
            logging.error(f"Error checking premium status for session: {e}")
            return False

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")

bot_instance = Bot()

def main():
    async def start_services():
        if Config.STRING_SESSION:
            await asyncio.gather(
                app.start(),        # Start the Pyrogram Client
                bot_instance.start()  # Start the bot instance
            )
        else:
            await asyncio.gather(
                bot_instance.start()
            )
        
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_services())
    loop.run_forever()

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="There is no current event loop")
    main()
