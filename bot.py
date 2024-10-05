import logging
import logging.config
import warnings
from pyrogram import Client, idle
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from pytz import timezone
from datetime import datetime
import asyncio
from plugins.web_support import web_server
from plugins.file_rename import app
import pyromod

# Define version for the bot
__version__ = "1.0.0"

# Set up logging with UTF-8 encoding to handle Unicode characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    encoding='utf-8'
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


class Bot(Client):

    def __init__(self):
        session_name = "string.session" if Config.STRING_SESSION else "ANIFLIX.session"
        super().__init__(
            name=session_name,
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
                logging.warning("Make sure the bot is an admin in the force sub channel")
                self.force_channel = None
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app_runner, bind_address, Config.PORT).start()
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
                await self.send_message(
                    Config.LOG_CHANNEL,
                    f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n📅 Dᴀᴛᴇ : `{date}`\n⏰ Tɪᴍᴇ : `{time}`\n🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`"
                )
            except:
                logging.error("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪꜱ Iꜱ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ", exc_info=True)

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
