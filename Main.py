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
        intents.messages = True  # needed to send messages
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
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

        await self.tree.sync()
        print("✅ Slash commands synced globally")

    async def on_ready(self):
        print(f"Bot is online as {self.user} ✅")
        
        # --- Send a message mentioning you ---
        guild_id = 1096028646323527740  # Replace with your server ID
        channel_id = 1407094852709253302  # Replace with the channel you want to send in
        user_id = 1360749637299998870  # Your Discord user ID

        guild = self.get_guild(guild_id)
        if guild:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.send(f"Hello {guild.get_member(user_id).mention}, Arcadia is now online! 🎮")


# ---------------- Bot Instance ----------------
bot = ArcadiaBot()

# ---------------- Run Bot ----------------
Config.validate()  # ensure DISCORD_TOKEN is set
bot.run(Config.DISCORD_TOKEN)
