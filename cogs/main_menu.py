import discord
from discord import app_commands
from discord.ext import commands
from bot.config import Config as c
from .db_helper import get_games

players = {}
arcadia_join_dict = {
    "name": "unknown",
    "menu": "main menu",
}

# ------------------ Embed Functions ------------------
def main_menu_embed(user_id: int):
    player_name = players.get(user_id, {}).get("name", "Player")
    embed = discord.Embed(
        title=f"🎮 Welcome to Arcadia, {player_name}!",
        description="You can **join an existing game** or **create a new one**.\n\nChoose an option below to start your adventure!",
        color=discord.Color.blurple()
    )
    return embed

def join_menu_embed(user_id: int):
    embed = discord.Embed(
        title="📥 Join a Game",
        description="If a game is available (Green), or if it is full (Red) you can spectate.",
        color=discord.Color.green()
    )
    return embed

def create_menu_embed(user_id: int):
    embed = discord.Embed(
        title="🛠️ Create a New Game",
        description="Choose a game type to create a new instance:",
        color=discord.Color.orange()
    )
    return embed

menu_embeds = {
    "main menu": main_menu_embed,
    "join": join_menu_embed,
    "create": create_menu_embed,
}

menu_button_dict = {
    "main menu": ("join", "create", "exit"),
    "join": ("main menu", "exit"),
    "create": ("main menu", "exit"),
}


# ------------------ Dynamic View ------------------
class MenuView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        current_menu = players[user.id]["menu"]

        # Add buttons dynamically from the dict
        for button_name in menu_button_dict[current_menu]:
            self.add_item(MenuButton(button_name))


class MenuButton(discord.ui.Button):
    def __init__(self, name: str):
        super().__init__(label=name.capitalize(), style=discord.ButtonStyle.primary)
        self.name = name

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        if self.name == "exit":
            players.pop(user.id, None)
            await interaction.response.edit_message(
                content="Arcadia closed. See you soon!",
                embed=None,
                view=None
            )
            return

        # Update the player's menu
        players[user.id]["menu"] = self.name

        # Get the correct embed + new view
        embed_func = menu_embeds[self.name]
        embed = embed_func(user.id)
        new_view = MenuView(user)

        await interaction.response.edit_message(embed=embed, view=new_view)


# ------------------ Cog ------------------
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
        await interaction.response.send_message(
            "",
            embed=main_menu_embed(user.id),
            view=MenuView(user),
            ephemeral=True
        )


# ------------------ Load Cog ------------------
async def setup(bot):
    await bot.add_cog(MainMenu(bot))
