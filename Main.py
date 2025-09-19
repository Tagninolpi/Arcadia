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
        intents.guilds = True
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        # Load all cogs dynamically
        cogs = [
            "cogs.main_menu",
            # Add more cogs here later
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded cog: {cog}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog}: {e}")

        # Sync slash commands globally
        await self.tree.sync()
        print("✅ Slash commands synced globally")

# ---------------- Bot Instance ----------------
bot = ArcadiaBot()

# ---------------- Run Bot ----------------
Config.validate()  # ensure DISCORD_TOKEN is set
bot.run(Config.DISCORD_TOKEN)
