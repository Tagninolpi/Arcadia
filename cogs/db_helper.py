from supabase import create_client
import os

# ------------------ Supabase Client ------------------
SUPABASE_URL = os.getenv("https://srkcqfvhchfyasmaglcs.supabase.co")  # your project URL
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNya2NxZnZoY2hmeWFzbWFnbGNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzNjEwNDEsImV4cCI6MjA3MzkzNzA0MX0.qVAaIbhNu9O0mNLXGNpDwEvKTgobXsZ4RBwzBRcTSP4")  # service key
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ Functions ------------------

def get_games():
    """
    Fetch all games from the table and format them as a list of dictionaries.
    Each dict contains: id, game_name, active_players, waiting_players, game_state, updated_at
    """
    response = supabase.table("games").select("*").execute()
    if response.error:
        print("Error fetching games:", response.error)
        return []

    # Format each game nicely
    games_list = []
    for game in response.data:
        games_list.append({
            "id": game["id"],
            "game_name": game["game_name"],
            "active_players": game["active_players"],
            "waiting_players": game["waiting_players"],
            "game_state": game["game_state"],
            "updated_at": game["updated_at"]
        })
    return games_list


def update_game(game_id: int, active_players=None, waiting_players=None, game_state=None):
    """
    Update a specific game row by id. Only provide the fields you want to update.
    """
    data = {}
    if active_players is not None:
        data["active_players"] = active_players
    if waiting_players is not None:
        data["waiting_players"] = waiting_players
    if game_state is not None:
        data["game_state"] = game_state

    if not data:
        print("No data provided to update.")
        return False

    # Always update the timestamp
    data["updated_at"] = "NOW()"

    response = supabase.table("games").update(data).eq("id", game_id).execute()
    if response.error:
        print("Error updating game:", response.error)
        return False
    return True


def reset_game_table():
    """
    Optional: Deletes all games and resets the table.
    WARNING: This will erase all data.
    """
    response = supabase.table("games").delete().neq("id", 0).execute()
    if response.error:
        print("Error resetting table:", response.error)
        return False
    print("Game table reset successfully.")
    return True


def initialize_game(game_name: str, active_players=None, waiting_players=None, game_state=None):
    """
    Add a new game instance to the table.
    """
    if active_players is None:
        active_players = []
    if waiting_players is None:
        waiting_players = []
    if game_state is None:
        game_state = {}

    new_game = {
        "game_name": game_name,
        "active_players": active_players,
        "waiting_players": waiting_players,
        "game_state": game_state,
        "updated_at": "NOW()"
    }
    response = supabase.table("games").insert(new_game).execute()
    if response.error:
        print("Error initializing game:", response.error)
        return None
    return response.data[0]  # return the newly created game row

def delete_game(game_id: int):
    """
    Delete a specific game instance by its ID.
    Returns True if successful, False otherwise.
    """
    response = supabase.table("games").delete().eq("id", game_id).execute()
    if response.error:
        print("Error deleting game:", response.error)
        return False
    print(f"Game with ID {game_id} deleted successfully.")
    return True
