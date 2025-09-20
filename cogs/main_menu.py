import discord
from discord import app_commands
from discord.ext import commands
from bot.config import Config as c

players = {}
arcadia_join_dict = {
    "name" : "unknown",
    "menu" : "main menu",


}
class MainMenu(commands.Cog):
    """Main menu commands for Arcadia."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="arcadia", description="Open the main menu")
    async def main_menu(self, interaction: discord.Interaction):
        channel = interaction.channel
        if not(channel.id in c.allowed_channel_ids):
            await interaction.response.send_message("You can't use this command in this channel, use it in -bot-commands or -gaming", ephemeral=True)
            return 
        user = interaction.user
        if user.id in players:
            await interaction.response.send_message("You already joined arcadia, You can't use this command now", ephemeral=True)
            return
        else:
            players[user.id] = arcadia_join_dict.copy()
            players[user.id]["name"] = user.display_name or user.name
        
        await interaction.response.send_message(f"Welcome to Arcadia! {user.mension}, {players[user.id]["name"]} ", ephemeral=True)

# Function to load the cog
async def setup(bot):
    await bot.add_cog(MainMenu(bot))
