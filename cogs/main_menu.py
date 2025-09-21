import discord
from discord import app_commands
from discord.ext import commands
from bot.config import Config as c
from .db_helper import initialize_game, get_games
from .connect4 import show_connect4

players = {}
arcadia_join_dict = {
    "name": "unknown",
    "menu": "main menu",
}

# ------------------ Embed Functions ------------------
def main_menu_embed(user_id: int):
    player_name = players.get(user_id, {}).get("name", "Player")
    return discord.Embed(
        title=f"🎮 Welcome to Arcadia, {player_name}!",
        description="You can **join an existing game** or **create a new one**.\n\nChoose an option below to start your adventure!",
        color=discord.Color.blurple()
    )

def join_menu_embed(user_id: int):
    return discord.Embed(
        title="📥 Join a Game",
        description="Select a game below to join or spectate.",
        color=discord.Color.green()
    )

def create_menu_embed(user_id: int):
    return discord.Embed(
        title="🛠️ Create a New Game",
        description="Choose a game type to create a new instance:",
        color=discord.Color.orange()
    )

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

create_buttons_dict = {
    "connect4": lambda user_id: initialize_game(
        game_name="connect4",
        active_players=[user_id],
        waiting_players=[],
        game_state=[["⬜" for _ in range(6)] for _ in range(7)]
    ),
    "battleship": None,
    "tictactoe": None,
    "hangman": None,
}

# ------------------ Dynamic Views ------------------
class MenuView(discord.ui.View):
    """Main menu buttons view."""
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        current_menu = players[user.id]["menu"]

        for button_name in menu_button_dict[current_menu]:
            if button_name == "create":
                self.add_item(CreateMenuOpenerButton(user))
            elif button_name == "join":
                self.add_item(JoinMenuOpenerButton(user))
            else:
                self.add_item(MenuButton(button_name))

class MenuButton(discord.ui.Button):
    def __init__(self, name: str):
        style = discord.ButtonStyle.primary if name != "exit" else discord.ButtonStyle.danger
        super().__init__(label=name.capitalize(), style=style)
        self.name = name

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        if user.id not in players:
            await interaction.response.send_message("You are not in Arcadia!", ephemeral=True)
            return

        if self.name == "exit":
            players.pop(user.id, None)
            await interaction.response.edit_message(
                content="Arcadia closed. See you soon!",
                embed=None,
                view=None
            )
            return

        players[user.id]["menu"] = self.name
        embed = menu_embeds[self.name](user.id)
        await interaction.response.edit_message(embed=embed, view=MenuView(user))


# ------------------ Create Menu ------------------
class CreateMenuOpenerButton(discord.ui.Button):
    def __init__(self, user: discord.User):
        super().__init__(label="Create", style=discord.ButtonStyle.success)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        players[self.user.id]["menu"] = "create"
        embed = create_menu_embed(self.user.id)
        await interaction.response.edit_message(embed=embed, view=CreateMenuView(self.user))

class CreateMenuView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user

        for game_name in create_buttons_dict.keys():
            self.add_item(CreateMenuButton(game_name))

        for button_name in menu_button_dict["create"]:
            self.add_item(MenuButton(button_name))

class CreateMenuButton(discord.ui.Button):
    def __init__(self, game_name: str):
        super().__init__(label=game_name.capitalize(), style=discord.ButtonStyle.primary)
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        if user.id not in players:
            await interaction.response.send_message("You are not in Arcadia!", ephemeral=True)
            return

        creation_func = create_buttons_dict[self.game_name]
        if creation_func is None:
            await interaction.response.send_message(f"{self.game_name.capitalize()} is not available yet.", ephemeral=True)
            return

        creation_func(user.id)

        if self.game_name.lower() == "connect4":
            await show_connect4(interaction, "connect4", user.id)
        else:
            players[user.id]["menu"] = f"{self.game_name}_menu"
            embed = discord.Embed(
                title=f"🎮 {self.game_name.capitalize()} Menu",
                description="Game menu will be implemented here.",
                color=discord.Color.blurple()
            )
            await interaction.response.edit_message(embed=embed, view=None)


# ------------------ Join Menu ------------------
class JoinMenuOpenerButton(discord.ui.Button):
    def __init__(self, user: discord.User):
        super().__init__(label="Join", style=discord.ButtonStyle.success)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        players[self.user.id]["menu"] = "join"
        embed = join_menu_embed(self.user.id)
        await interaction.response.edit_message(embed=embed, view=JoinMenuView(self.user))

class JoinMenuView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user

        # Show all available games
        games = get_games()
        for g in games:
            self.add_item(JoinMenuButton(g["game_name"]))

        # Add back/exit
        for button_name in menu_button_dict["join"]:
            self.add_item(MenuButton(button_name))

class JoinMenuButton(discord.ui.Button):
    def __init__(self, game_name: str):
        super().__init__(label=f"Join {game_name.capitalize()}", style=discord.ButtonStyle.primary)
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        if user.id not in players:
            await interaction.response.send_message("You are not in Arcadia!", ephemeral=True)
            return

        if self.game_name.lower() == "connect4":
            await show_connect4(interaction, "connect4", user.id)
        else:
            await interaction.response.send_message(f"Joining {self.game_name} not supported yet.", ephemeral=True)


# ------------------ Main Cog ------------------
class MainMenu(commands.Cog):
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

        players[user.id] = arcadia_join_dict.copy()
        players[user.id]["name"] = user.display_name or user.name

        await interaction.response.send_message(
            "",
            embed=main_menu_embed(user.id),
            view=MenuView(user),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(MainMenu(bot))
