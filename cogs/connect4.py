import discord
from discord.ext import commands
from .db_helper import get_games, update_game
from . import players

CIRCLE = ["🔴", "🟡"]  # player 1, player 2
EMPTY = "⬜"
ROWS = 6
COLS = 7

def get_player_color_index(user_id, active_players):
    """Return 0 or 1 depending on player index in active_players"""
    try:
        return active_players.index(user_id) % 2
    except ValueError:
        return 0  # fallback

def render_board(game_state):
    """Convert the game_state (list of columns) into a string for Discord embed."""
    # Build row by row (top to bottom)
    lines = []
    for r in reversed(range(ROWS)):
        line = ""
        for c in range(COLS):
            line += game_state[c][r]
        lines.append(line)
    return "\n".join(lines)


async def show_connect4(interaction: discord.Interaction, game_name: str, user_id: int):
    """
    Fetch the game from the DB with this player as active, show the current board,
    and send a view with 7 buttons for columns.
    """
    # Find the game
    games = get_games()
    game = None
    for g in games:
        if g["game_name"] == game_name and user_id in g["active_players"]:
            game = g
            break

    if game is None:
        await interaction.response.send_message("No game found for you.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🎮 {game_name.capitalize()}",
        description=render_board(game["game_state"]),
        color=discord.Color.blurple()
    )

    view = Connect4View(game, user_id)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class Connect4View(discord.ui.View):
    """View with 7 buttons for Connect4 columns"""
    def __init__(self, game, user_id):
        super().__init__(timeout=None)
        self.game = game
        self.user_id = user_id

        for i in range(COLS):
            self.add_item(ColumnButton(i, game, user_id))


class ColumnButton(discord.ui.Button):
    """Button for a single column"""
    def __init__(self, col_index, game, user_id):
        super().__init__(label=str(col_index+1), style=discord.ButtonStyle.primary)
        self.col_index = col_index
        self.game = game
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        # Determine player's circle
        color_index = self.game["active_players"].index(self.user_id) % 2
        circle = CIRCLE[color_index]

        # Drop the disc in the selected column
        column = self.game["game_state"][self.col_index]
        for i in range(ROWS):
            if column[i] == EMPTY:
                column[i] = circle
                break
        else:
            # Column full
            await interaction.response.send_message("Column full!", ephemeral=True)
            return

        # Update DB
        update_game(self.game["id"], game_state=self.game["game_state"])

        # Render new board
        embed = discord.Embed(
            title=f"🎮 {self.game['game_name'].capitalize()}",
            description=render_board(self.game["game_state"]),
            color=discord.Color.blurple()
        )

        # Close menu like "exit"
        await interaction.response.edit_message(embed=embed, view=None)
