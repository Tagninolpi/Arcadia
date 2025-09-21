import discord
from discord.ui import Button, View
from datetime import datetime
from .main_menu import players
from .db_helper import get_games, initialize_game

# ------------------ Connect 4 Initial State ------------------
def connect4_initial_state():
    """Return a 6x7 Connect 4 board filled with empty squares."""
    return [["⬜" for _ in range(6)] for _ in range(7)]

menu_embeds = {
    "main menu":main_menu_embed()
}





# ------------------ Menu Button ------------------
class MenuButton(Button):
    def __init__(self, label: str, style=discord.ButtonStyle.gray):
        super().__init__(label=label, style=style, custom_id=f"menu_{label.lower()}")
        self.menu_name = label.lower()

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        players.setdefault(user_id, {})["menu"] = self.menu_name

        # Defer response to avoid "already acknowledged" error
        await interaction.response.defer()

        # ---------------- Exit Button ----------------
        if self.menu_name == "exit":
            for child in self.view.children:
                child.disabled = True
            await interaction.edit_original_response(content="Arcadia closed, see you soon 👋", embed=None, view=None)
            players.pop(user_id)
            return

        # ---------------- Create Button Click ----------------
        if players[user_id]["menu"] == "create" and self.menu_name not in ["main_menu", "exit"]:
            # Initialize game state depending on type
            if self.menu_name == "connect4":
                initial_game_state = {
                    "board": connect4_initial_state()
                }
            else:
                initial_game_state = {
                    "status": "waiting_for_players"}
            new_game = initialize_game(
                game_name=self.menu_name,
                active_players=[user_id],
                waiting_players=[],
                game_state=initial_game_state
            )
            if new_game:
                await interaction.followup.send(f"✅ Created a new **{self.menu_name}** game!", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Failed to create game **{self.menu_name}**.", ephemeral=True)
            # Automatically go to Join menu
            players[user_id]["menu"] = "join"

        # ---------------- Update Embed + View ----------------
        embed = MenuViews.get_embed(user_id)
        view = MenuViews.get_view(user_id)
        await interaction.edit_original_response(embed=embed, view=view)

# ------------------ Views Class ------------------
class MenuViews:
    MENU_BUTTONS_CONFIG = {
        "main_menu": ["Join", "Create", "Exit"],
        "join": [],  # dynamically filled with game names + Back
        "create": ["connect4", "tic tac toe", "battleship", "hangman", "Exit"]
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
        return main_menu_embed(user_id)

    @staticmethod
    def get_view(user_id: int) -> View:
        menu_name = players.get(user_id, {}).get("menu", "main_menu")
        labels = []

        if menu_name == "join":
            games = get_games()
            if games:
                labels = [g["game_name"] for g in games]
            labels += ["Main_Menu", "Exit"]
        else:
            labels = MenuViews.MENU_BUTTONS_CONFIG.get(menu_name, ["Main_Menu", "Exit"])

        view = View(timeout=None)
        for label in labels:
            style = discord.ButtonStyle.red if label.lower() == "exit" else discord.ButtonStyle.gray
            button = MenuButton(label, style)
            view.add_item(button)
        return view
