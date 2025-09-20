import discord
from discord.ext import commands
import logging
from bot.config import Config
from keep_alive import keep_alive

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ArcadiaBot")

# ---------------- Keep Alive ----------------
keep_alive()
logger.info("✅ Keep-alive server started")

# ---------------- Bot Class ----------------
class ArcadiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True  # required for commands/messages
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        cogs = [
            "cogs.main_menu",  # add more cogs here
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog}: {e}")

        # Sync slash commands globally
        try:
            await self.tree.sync()
            logger.info("✅ Slash commands synced globally")
        except Exception as e:
            logger.error(f"❌ Failed to sync slash commands: {e}")

    async def on_ready(self):
        logger.info(f"Bot is online as {self.user} ✅")

        # Optional: send a message to yourself when bot starts
        guild_id = 1096028646323527740  # replace with your server ID
        channel_id = 1407094852709253302  # replace with your channel ID
        user_id = 1360749637299998870  # your Discord user ID

        guild = self.get_guild(guild_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    member = guild.get_member(user_id) or await guild.fetch_member(user_id)
                    await channel.send(f"Hello {member.mention}, Arcadia is now online! 🎮")
                    logger.info("✅ Online message sent successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to send online message: {e}")

# ---------------- Bot Instance ----------------
bot = ArcadiaBot()

# Validate Config
Config.validate()

# ---------------- Run Bot ----------------
bot.run(Config.DISCORD_TOKEN)
