import discord
from discord import app_commands
from discord.ext import commands
from bot.config import Config as c
from mainmenu_views import MenuViews  # the class we defined for embeds + views

players = {}
arcadia_join_dict = {
    "name": "unknown",
    "menu": "main_menu",  # standardize menu key
}
print("main_menu.py loaded")
class MainMenu(commands.Cog):
    """Main menu commands for Arcadia."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="arcadia", description="Open the main menu")
    async def main_menu(self, interaction: discord.Interaction):
        channel = interaction.channel
        if channel.id not in c.allowed_channel_ids:
            await interaction.response.send_message(
                "You can't use this command in this channel, use it in -bot-commands or -gaming", 
                ephemeral=True
            )
            return

        user = interaction.user
        if user.id in players:
            await interaction.response.send_message(
                "You already joined Arcadia. You can't use this command now.", 
                ephemeral=True
            )
            return

        # Initialize player
        players[user.id] = arcadia_join_dict.copy()
        players[user.id]["name"] = user.display_name or user.name

        # Send main menu embed + buttons
        embed = MenuViews.get_embed(user.id)
        view = MenuViews.get_view(user.id)
        await interaction.response.send_message(
            f"Welcome to Arcadia! {user.mention}, {players[user.id]['name']}", 
            embed=embed,
            view=view,
            ephemeral=True
        )

# ---------------- Load Cog ----------------
async def setup(bot):
    await bot.add_cog(MainMenu(bot))
