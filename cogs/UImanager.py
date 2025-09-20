import discord
from discord.ui import Button, View
from .main_menu import players  # your players dict

# ---------------- Embed Functions ----------------
def main_menu_embed(user_id: int):
    """
    Main menu embed: welcome player, show basic instructions.
    """
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


# ---------------- Button Class ----------------
class MenuButton(Button):
    def __init__(self, label: str, style=discord.ButtonStyle.gray):
        super().__init__(label=label, style=style, custom_id=f"menu_{label.lower()}")
        self.menu_name = label.lower()  # store lowercase for consistency ✅

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # Always store lowercase menu name
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

        # Update to new embed + view
        embed = MenuViews.get_embed(user_id)
        view = MenuViews.get_view(user_id)
        await interaction.response.edit_message(embed=embed, view=view)


# ---------------- Views Class ----------------
class MenuViews:
    """
    Manages embeds and dynamic menu views.
    """

    # Define which menu buttons are visible for each menu
    MENU_BUTTONS_CONFIG = {
        "main_menu": ["Join", "Create", "Exit"],
        "join": ["Main_Menu","Exit"],
        "create": ["Main_Menu","Exit"]
        
    }

    # ------------------ Embed Getter ------------------
    @staticmethod
    def get_embed(user_id: int):
        menu_name = players.get(user_id, {}).get("menu", "main_menu")
        # Return embed based on current menu
        if menu_name == "main_menu":
            return main_menu_embed(user_id)
        # Default/fallback
        return main_menu_embed(user_id)

    # ------------------ View Getter ------------------
    @staticmethod
    def get_view(user_id: int) -> View:
        """
        Returns a View containing buttons visible for the player's current menu.
        """
        menu_name = players.get(user_id, {}).get("menu", "main_menu")
        button_labels = MenuViews.MENU_BUTTONS_CONFIG.get(menu_name, ["MainMenu", "Exit"])

        view = View(timeout=None)
        for label in button_labels:
            # Exit button is red, others gray
            style = discord.ButtonStyle.red if label.lower() == "exit" else discord.ButtonStyle.gray
            button = MenuButton(label, style)
            view.add_item(button)

        return view
