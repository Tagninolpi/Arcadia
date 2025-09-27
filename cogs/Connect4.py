import discord
from discord.ext import commands
from cogs.db_helper import get_games, update_game
from bot.config import Config as c # separate module to avoid circular import

# ---------------- Connect 4 Buttons ----------------
class Connect4Button(discord.ui.Button):
    def __init__(self, label, row, view_ref):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, row=row)
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        game = self.view_ref.game
        user_id = self.view_ref.user_id

        # Determine player color
        if game["active_players"][0] == user_id:
            color = "🟡"
        else:
            color = "🔴"

        col = int(self.label) - 1
        for row_idx in range(6):
            if game["game_state"]["state"][col][row_idx] == "⬜":
                game["game_state"]["state"][col][row_idx] = color
                break

        # Remove user from waiting
        if user_id in game["waiting_players"]:
            game["waiting_players"].remove(user_id)

        # Update DB
        update_game(
            game_id=game["id"],
            active_players=game["active_players"],
            waiting_players=game["waiting_players"],
            game_state=game["game_state"]
        )

        # Remove from players dict
        c.players.pop(user_id, None)

        # Close view
        await interaction.response.edit_message(content="Move registered ✅", view=None)


class ExitButton(discord.ui.Button):
    def __init__(self, user_id):
        super().__init__(label="Exit", style=discord.ButtonStyle.red, row=1)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        # Remove user from all games
        games = get_games()
        for g in games:
            changed = False
            if self.user_id in g.get("active_players", []):
                g["active_players"].remove(self.user_id)
                changed = True
            if self.user_id in g.get("waiting_players", []):
                g["waiting_players"].remove(self.user_id)
                changed = True
            if changed:
                update_game(
                    game_id=g["id"],
                    active_players=g.get("active_players"),
                    waiting_players=g.get("waiting_players"),
                    game_state=g.get("game_state")
                )

        # Remove from players dict
        c.players.pop(self.user_id, None)

        await interaction.response.edit_message(content="You have exited all games ✅", view=None)


# ---------------- Connect 4 View ----------------
class Connect4View(discord.ui.View):
    def __init__(self, user_id, game):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.game = game

        active = game.get("active_players", [])
        waiting = game.get("waiting_players", [])

        if user_id not in active and len(active) < 2:
            active.append(user_id)
            waiting.append(user_id)
        elif user_id not in waiting and len(active) >= 2:
            # Game full → only exit button
            self.add_item(ExitButton(user_id=user_id))
            return

        # Add Connect 4 buttons
        for i in range(2, 7):
            self.add_item(Connect4Button(label=str(i), row=0, view_ref=self))
        self.add_item(Connect4Button(label="1", row=1, view_ref=self))
        self.add_item(Connect4Button(label="7", row=1, view_ref=self))

        # Exit button
        self.add_item(ExitButton(user_id=user_id))

        # Update DB
        game["active_players"] = active
        game["waiting_players"] = waiting
        update_game(
            game_id=game["id"],
            active_players=active,
            waiting_players=waiting,
            game_state=game["game_state"]
        )

    async def on_timeout(self):
        # Remove from players dict when view times out
        c.players.pop(self.user_id, None)


# ---------------- Connect4 Cog ----------------
class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def open_game(self, interaction, user_id, game_name):
        game = next((g for g in get_games() if g["game_name"] == game_name), None)
        if not game:
            await interaction.response.send_message("Game not found ❌", ephemeral=True)
            return

        board = game["game_state"]["state"]
        board_str = "\n".join("".join(board[col][row] for col in range(7)) for row in range(5, -1, -1))

        embed = discord.Embed(
            title=f"Connect 4: {game_name}",
            description=board_str,
            color=discord.Color.blue()
        )

        view = Connect4View(user_id=user_id, game=game)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Connect4(bot))
