import discord
from discord import app_commands
from discord.ext import commands
from bot.config import Config as c

players = {}

def arcadia_embed(title: str, desc: str):
    return discord.Embed(title=title, description=desc, color=discord.Color.blurple())

class ArcadiaView(discord.ui.View):
    def __init__(self, user: discord.User, timeout: int = 600):
        super().__init__(timeout=timeout)
        self.user = user
        self.message: discord.Message | None = None

        # Decide what to show based on current menu
        current_menu = players.get(user.id, {}).get("menu", "mainmenu")

        if current_menu == "mainmenu":
            self.add_item(self.CreateButton(self))
            self.add_item(self.JoinButton(self))
        elif current_menu in ("create", "join"):
            self.add_item(self.MainMenuButton(self))
        # If menu is a game (e.g. connect4), no menu buttons

        # Exit is always visible
        self.add_item(self.ExitButton(self))

    async def on_timeout(self):
        players.pop(self.user.id, None)
        if self.message:
            await self.message.edit(
                content="⏳ Session closed.",
                embed=None,
                view=None
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ This menu isn’t yours!", ephemeral=True)
            return False
        return True

    # ------------------ Buttons ------------------
    class MainMenuButton(discord.ui.Button):
        def __init__(self, parent: "ArcadiaView"):
            super().__init__(label="Main Menu", style=discord.ButtonStyle.primary)
            self.parent = parent

        async def callback(self, interaction: discord.Interaction):
            players[self.parent.user.id]["menu"] = "mainmenu"
            embed = arcadia_embed("🎮 Main Menu", "Choose an option below:")
            new_view = ArcadiaView(self.parent.user)
            await interaction.response.edit_message(embed=embed, view=new_view)
            new_view.message = await interaction.original_response()

    class CreateButton(discord.ui.Button):
        def __init__(self, parent: "ArcadiaView"):
            super().__init__(label="Create", style=discord.ButtonStyle.success)
            self.parent = parent

        async def callback(self, interaction: discord.Interaction):
            players[self.parent.user.id]["menu"] = "create"
            embed = arcadia_embed("🛠️ Create Menu", "Here you could pick a game (e.g. Connect4).")
            new_view = ArcadiaView(self.parent.user)
            await interaction.response.edit_message(embed=embed, view=new_view)
            new_view.message = await interaction.original_response()

    class JoinButton(discord.ui.Button):
        def __init__(self, parent: "ArcadiaView"):
            super().__init__(label="Join", style=discord.ButtonStyle.success)
            self.parent = parent

        async def callback(self, interaction: discord.Interaction):
            players[self.parent.user.id]["menu"] = "join"
            embed = arcadia_embed("📥 Join Menu", "Here you could join a game.")
            new_view = ArcadiaView(self.parent.user)
            await interaction.response.edit_message(embed=embed, view=new_view)
            new_view.message = await interaction.original_response()

    class ExitButton(discord.ui.Button):
        def __init__(self, parent: "ArcadiaView"):
            super().__init__(label="Exit", style=discord.ButtonStyle.danger)
            self.parent = parent

        async def callback(self, interaction: discord.Interaction):
            players.pop(self.parent.user.id, None)
            await interaction.response.edit_message(
                content="👋 Arcadia closed.",
                embed=None,
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
        if interaction.user.id in players:
            await interaction.response.send_message(
                "⚠️ You already have an active Arcadia session.",
                ephemeral=True
            )
            return

        # Init player state with menu = mainmenu
        players[interaction.user.id] = {"menu": "mainmenu"}

        # Show menu
        view = ArcadiaView(interaction.user)
        embed = arcadia_embed("🎮 Arcadia", "Choose an option below:")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(MainMenu(bot))
