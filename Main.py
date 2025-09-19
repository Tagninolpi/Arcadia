import discord
from discord.ext import commands
from bot.config import Config
from keep_alive import keep_alive

# Start keep-alive server for UptimeRobot
keep_alive()

# ---------------- Bot Class ----------------
class ArcadiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True  # required for slash commands
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        # Sync slash commands globally
        await self.tree.sync()
        print("✅ Slash commands synced globally")

# ---------------- Bot Instance ----------------
bot = ArcadiaBot()

# ---------------- Run Bot ----------------
Config.validate()  # ensure DISCORD_TOKEN is set
bot.run(Config.DISCORD_TOKEN)
