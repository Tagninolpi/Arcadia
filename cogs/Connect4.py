import discord
from discord.ext import commands

class Connect4View(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

        # Add buttons 2-6 on the first row (row=0)
        for i in range(2, 7):
            self.add_item(Connect4Button(label=str(i), row=0))

        # Add buttons 1 and 7 on the second row (row=1)
        self.add_item(Connect4Button(label="1", row=1))
        self.add_item(Connect4Button(label="7", row=1))


class Connect4Button(discord.ui.Button):
    def __init__(self, label, row):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, row=row)

    async def callback(self, interaction: discord.Interaction):
        # For now, just close the view
        await interaction.response.edit_message(content="Connect 4 button pressed! ✅", view=None)


# ------------------ Cog ------------------
class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def open_game(self, interaction, user_id):
        """Send a placeholder Connect 4 view."""
        # Create initial board string (6 rows x 7 columns)
        board_str = "🟦" * 7 + "\n"
        board_str += "\n".join(["⬜"*7 for _ in range(6)])  # empty slots

        embed = discord.Embed(
            title="Connect 4",
            description=board_str,
            color=discord.Color.blue()
        )

        view = Connect4View(user_id=user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Connect4(bot))
