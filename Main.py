import asyncio
import logging
import discord
from discord.ext import commands

from bot.config import Config
from keep_alive import keep_alive

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Arcadia")

# ---------------- Bot Class ----------------
class ArcadiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True  # needed for slash + normal messages

        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        logger.info("Bot is starting up...")

        # List your cogs here
        cogs_to_load = [
            "cogs.main_menu",
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to load cog {cog}: {e}")

        # Sync global slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Synced {len(synced)} global commands")
        except Exception as e:
            logger.error(f"❌ Failed to sync global commands: {e}")

    async def on_ready(self):
        logger.info(f"Bot is online as {self.user} ✅")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")

        # Announce in your guild
        guild_id = 1096028646323527740
        channel_id = 1407094852709253302
        user_id = 1360749637299998870

        guild = self.get_guild(guild_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    member = guild.get_member(user_id) or await guild.fetch_member(user_id)
                    await channel.send(f"Hello {member.mention}, Arcadia is now online! 🎮")
                except Exception as e:
                    logger.error(f"❌ Failed to send online message: {e}")

# ---------------- Main Entry ----------------
async def main():
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    keep_alive()

    bot = ArcadiaBot()
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
