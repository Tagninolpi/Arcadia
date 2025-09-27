import discord
from discord import app_commands
from discord.ext import commands
from bot.config import Config as c
from cogs.db_helper import get_games, update_game


# ------------------ Views & Buttons ------------------
class GameMenuView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    async def populate_buttons(self):
        """Populate buttons based on current DB games."""
        games = get_games()
        self.clear_items()

        # Track position for row assignment
        buttons_added = 0
        max_per_row = 5
        max_rows = 5

        for g in games:
            if buttons_added >= max_per_row * max_rows:
                break  # Limit to 25 buttons max

            name = g["game_name"]
            active_players = g.get("active_players", [])
            state = g.get("game_state", {})
            max_players = state.get("max_players", 2)

            if not active_players:
                style = discord.ButtonStyle.gray
            elif len(active_players) < max_players:
                style = discord.ButtonStyle.green
            else:
                style = discord.ButtonStyle.red

            row = buttons_added % max_per_row  # row is 0-4
            self.add_item(GameButton(name=name, style=style, row=row))
            buttons_added += 1

        # Exit button always on last position (row 4)
        self.add_item(ExitButton(user_id=self.user_id, row=max_rows - 1))


class GameButton(discord.ui.Button):
    def __init__(self, name, style, row=0):
        super().__init__(label=name, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        # Find the Connect4 cog
        connect4_cog = interaction.client.get_cog("Connect4")
        if connect4_cog:
            # Open Connect 4 view for this user, passing the game name
            await connect4_cog.open_game(
                interaction,
                user_id=interaction.user.id,
                game_name=self.label  # pass the button label as the game name
            )
        else:
            await interaction.response.send_message(
                "Connect4 cog not loaded.", ephemeral=True
            )




class ExitButton(discord.ui.Button):
    def __init__(self, user_id, row=0):
        super().__init__(label="Exit", style=discord.ButtonStyle.red, row=row)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        # Remove player from active_players in all games
        games = get_games()
        for g in games:
            if self.user_id in g.get("active_players", []):
                updated_players = [p for p in g["active_players"] if p != self.user_id]
                update_game(g["id"], active_players=updated_players)

        # Remove player session and replace view
        c.players.pop(self.user_id, None)
        await interaction.response.edit_message(
            content="You have exited all games. ✅",
            view=None
        )


# ------------------ Cog ------------------
class MainMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="arcadia", description="Open the Arcadia menu")
    async def arcadia(self, interaction: discord.Interaction):
        # Restrict to allowed channels
        if interaction.channel.id not in c.allowed_channel_ids:
            await interaction.response.send_message(
                "❌ You can only use this command in game channels.",
                ephemeral=True
            )
            return

        # One session per user
        if interaction.user.id in c.players:
            await interaction.response.send_message(
                "⚠️ You already have an active Arcadia session.",
                ephemeral=True
            )
            return

        # Init player session
        c.players[interaction.user.id] = True

        # Build embed
        embed = discord.Embed(
            title="🎮 Welcome to Arcadia",
            description=(
                "Join a game:\n"
                "• Gray: Empty game\n"
                "• Green: Waiting for player\n"
                "• Red: Full game (spectate only)"
            ),
            color=discord.Color.blurple()
        )

        # Build and populate view
        view = GameMenuView(user_id=interaction.user.id)
        await view.populate_buttons()

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MainMenu(bot))
