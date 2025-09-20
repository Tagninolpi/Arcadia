import discord
from discord.ext import commands
from bot.config import Config
from keep_alive import keep_alive

# Start keep-alive server
keep_alive()
 
class ArcadiaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True  # ✅ required for commands/messages
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        cogs = [
            "cogs.main_menu",
            # Add more cogs here
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
                    print(f"❌ Failed to send online message: {e}")

bot = ArcadiaBot()
Config.validate()
bot.run(Config.DISCORD_TOKEN)
