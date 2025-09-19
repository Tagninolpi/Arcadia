import discord
from discord import app_commands
from discord.ext import commands

class MainMenu(commands.Cog):
    """Main menu commands for Arcadia."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="main_menu", description="Open the main menu")
    async def main_menu(self, interaction: discord.Interaction):
        # Example response
        await interaction.response.send_message("Welcome to Arcadia! 🎮", ephemeral=True)

# Function to load the cog
async def setup(bot):
    await bot.add_cog(MainMenu(bot))
