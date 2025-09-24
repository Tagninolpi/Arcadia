import discord
from .db_helper import get_games, update_game
from .main_menu import players, BaseView  # import global session/exit handling

CIRCLE = ["🔴", "🟡"]  # player 1, player 2
EMPTY = "⬜"
ROWS = 6
COLS = 7


# ------------------ Helper Functions ------------------

def get_player_color_index(user_id, active_players):
    """Return 0 or 1 depending on player index in active_players"""
    try:
        return active_players.index(user_id) % 2
    except ValueError:
        return 0  # fallback


def render_board(game_state):
    """Convert the game_state (list of columns) into a string for Discord embed."""
    lines = []
    for r in reversed(range(ROWS)):
        line = ""
        for c in range(COLS):
            line += game_state[c][r]
        lines.append(line)
    return "\n".join(lines)


# ------------------ Entry Point ------------------

async def show_connect4(interaction: discord.Interaction, game_name: str, user_id: int):
    games = get_games()
    game = next((g for g in games if g["game_name"] == game_name), None)

    if game is None:
        await interaction.response.send_message("No Connect 4 game found. Create one first!", ephemeral=True)
        return

    # If player not in game, try to join as second player
    if user_id not in game["active_players"] and user_id not in game["waiting_players"]:
        if len(game["active_players"]) + len(game["waiting_players"]) >= 2:
            # Full → spectator
            embed = discord.Embed(
                title=f"🎮 {game_name.capitalize()} (Spectating)",
                description=render_board(game["game_state"]),
                color=discord.Color.greyple()
            )
            await interaction.response.send_message(
                embed=embed,
                view=ExitOnlyView(user_id),  # uses BaseView logic
                ephemeral=True
            )
            return
        else:
            waiting = game["waiting_players"] + [user_id]
            update_game(game["id"], waiting_players=waiting)
            game["waiting_players"] = waiting

    embed = discord.Embed(
        title=f"🎮 {game_name.capitalize()}",
        description=render_board(game["game_state"]),
        color=discord.Color.blurple()
    )

    if game.get("turn") == user_id:
        await interaction.response.send_message(
            embed=embed,
            view=Connect4View(game, user_id),
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            embed=embed,
            view=ExitOnlyView(user_id),
            ephemeral=True
        )


# ------------------ Views ------------------

class ExitOnlyView(BaseView):
    """Exit-only view for spectators or waiting players."""
    def __init__(self, user_id):
        super().__init__(user_id)
        self.add_item(ExitButton())


class ExitButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Exit", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        players.pop(user_id, None)
        await interaction.response.edit_message(
            content="You have left the game.",
            embed=None,
            view=None
        )


class Connect4View(BaseView):
    """Main Connect 4 interactive view."""
    def __init__(self, game, user_id):
        super().__init__(user_id)
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
        # Enforce turn order
        if self.user_id != self.game.get("turn"):
            await interaction.response.send_message("Not your turn!", ephemeral=True)
            return

        circle = CIRCLE[0] if self.user_id == self.game["active_players"][0] else CIRCLE[1]
        column = self.game["game_state"][self.col_index]

        # Drop disc
        for i in range(ROWS):
            if column[i] == EMPTY:
                column[i] = circle
                break
        else:
            await interaction.response.send_message("Column full!", ephemeral=True)
            return

        # Determine opponent for next turn
        if self.user_id in self.game["active_players"]:
            if self.game["waiting_players"]:
                opponent = self.game["waiting_players"][0]
            else:
                opponent = None
        else:
            opponent = self.game["active_players"][0]

        update_game(
            self.game["id"],
            game_state=self.game["game_state"],
            turn=opponent
        )

        embed = discord.Embed(
            title=f"🎮 {self.game['game_name'].capitalize()}",
            description=render_board(self.game["game_state"]),
            color=discord.Color.blurple()
        )
        await interaction.response.edit_message(embed=embed, view=None)
