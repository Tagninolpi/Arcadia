import discord
from discord.ui import Button, View
from datetime import datetime, timezone
from .main_menu import players
from .db_helper import get_games, initialize_game
 
# ---------------- Embed Functions ----------------
def main_menu_embed(user_id: int):
    """
    Embed for Main Menu: welcome player, show instructions.
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

def join_menu_embed(user_id: int):
    """
    Embed for Join Menu: list available games to join.
    """
    games = get_games()
    description = ""
    if not games:
        description = "No games available to join right now."
    else:
        for g in games:
            description += f"**{g['game_name']}** — Active: {len(g['active_players'])}, Waiting: {len(g['waiting_players'])}\n"

    embed = discord.Embed(
        title="📥 Join a Game",
        description=description,
        color=discord.Color.green()
    )
    return embed

def create_menu_embed(user_id: int):
    """
    Embed for Create Menu: choose game type to create.
    """
    embed = discord.Embed(
        title="🛠️ Create a New Game",
        description="Choose a game type to create a new instance:",
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
            # Close menu
            for child in self.view.children:
                child.disabled = True
            await interaction.response.edit_message(
                content="Arcadia closed, see you soon 👋",
                embed=None,
                view=None
            )
            players.popitem(user_id)
            return

        # Handle Create button click: create a new game
        if players[user_id]["menu"] == "create" and self.menu_name not in ["main_menu", "exit"]:
            # Create game in Supabase
            initial_game_state = {
                "status": "waiting_for_players",
                "turn": 0
            }
            new_game = initialize_game(
                game_name=self.menu_name,
                active_players=[user_id],
                waiting_players=[],
                game_state=initial_game_state
            )
            if new_game:
                await interaction.response.send_message(
                    f"✅ Created a new **{self.menu_name}** game!", 
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ Failed to create game **{self.menu_name}**.", 
                    ephemeral=True
                )
            # Update menu to Join menu automatically
            players[user_id]["menu"] = "join"

        # Update the view & embed
        embed = MenuViews.get_embed(user_id)
        view = MenuViews.get_view(user_id)
        await interaction.response.edit_message(embed=embed, view=view)

# ---------------- Views Class ----------------
class MenuViews:
    """
    Dynamic embeds + views for all menus.
    """

    # Menu configuration
    MENU_BUTTONS_CONFIG = {
        "main_menu": ["Join", "Create", "Exit"],
        "join": [],  # filled dynamically with game names + Back
        "create": ["connect4", "tic tac toe", "battleship", "hangman", "Exit"]  # list game types
    }

    # ---------------- Embed Getter ------------------
    @staticmethod
    def get_embed(user_id: int):
        menu_name = players.get(user_id, {}).get("menu", "main_menu")
        if menu_name == "main_menu":
            return main_menu_embed(user_id)
        elif menu_name == "join":
            return join_menu_embed(user_id)
        elif menu_name == "create":
            return create_menu_embed(user_id)
        # fallback
        return main_menu_embed(user_id)

    # ---------------- View Getter ------------------
    @staticmethod
    def get_view(user_id: int) -> View:
        menu_name = players.get(user_id, {}).get("menu", "main_menu")
        labels = []

        if menu_name == "join":
            # Fetch games dynamically
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
