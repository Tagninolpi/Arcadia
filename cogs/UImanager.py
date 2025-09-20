import discord
from discord.ui import Button, View
from .main_menu import players  # your players dict

# ---------------- Embed Functions ----------------
def main_menu_embed(user_id: int):
    player_name = players.get(user_id, {}).get("name", "Player")
    embed = discord.Embed(
        title=f"🎮 Welcome to Arcadia, {player_name}!",
        description=(
            "You can **join an existing game** or **create a new one**.\n\n"
            "Choose an option below to start your adventure!"
        ),
        color=discord.Color.blurple()
    )
    return embed

def join_menu_embed(user_id: int):
    embed = discord.Embed(
        title="🟢 Join a Game",
        description=(
            "This is the **joining menu**.\n\n"
            "• You can **join green matches** (available games).\n"
            "• Or **spectate red matches** (ongoing games)."
        ),
        color=discord.Color.green()
    )
    return embed

def create_menu_embed(user_id: int):
    embed = discord.Embed(
        title="🛠️ Create a Game",
        description=(
            "This is the **create menu**.\n\n"
            "• You can **create a new game** here.\n"
            "• Customize your game settings and invite players!"
        ),
        color=discord.Color.orange()
    )
    return embed


# ---------------- Button Class ----------------
class MenuButton(Button):
    def __init__(self, label: str, style=discord.ButtonStyle.gray):
        super().__init__(label=label, style=style, custom_id=f"menu_{label.lower()}")
        self.menu_name = label.lower()

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        players.setdefault(user_id, {})["menu"] = self.menu_name

        if self.menu_name == "exit":
            for child in self.view.children:
                child.disabled = True
            await interaction.response.edit_message(
                content="Arcadia closed, see you soon 👋",
                embed=None,
                view=None
            )
            return

        # Update with the correct embed + buttons
        embed = MenuViews.get_embed(user_id)
        view = MenuViews.get_view(user_id)
        await interaction.response.edit_message(embed=embed, view=view)


# ---------------- Views Class ----------------
class MenuViews:
    MENU_BUTTONS_CONFIG = {
        "main_menu": ["Join", "Create", "Exit"],
        "join": ["Main_Menu", "Exit"],
        "create": ["Main_Menu", "Exit"]
    }

    @staticmethod
    def get_embed(user_id: int):
        menu_name = players.get(user_id, {}).get("menu", "main_menu")
        if menu_name == "main_menu":
            return main_menu_embed(user_id)
        elif menu_name == "join":
            return join_menu_embed(user_id)
        elif menu_name == "create":
            return create_menu_embed(user_id)
        return main_menu_embed(user_id)  # fallback

    @staticmethod
    def get_view(user_id: int) -> View:
        menu_name = players.get(user_id, {}).get("menu", "main_menu")
        button_labels = MenuViews.MENU_BUTTONS_CONFIG.get(menu_name, ["Main_Menu", "Exit"])

        view = View(timeout=None)
        for label in button_labels:
            style = discord.ButtonStyle.red if label.lower() == "exit" else discord.ButtonStyle.gray
            button = MenuButton(label, style)
            view.add_item(button)

        return view
