from supabase import create_client
import os

# ------------------ Supabase Client ------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ Functions ------------------

def get_games():
    """Fetch all games from the table and format them as a list of dictionaries."""
    response = supabase.table("games").select("*").execute()

    # Check status_code
    if response.status_code not in (200, 201):
        print(f"[get_games] Error fetching games: status {response.status_code}, data: {response.data}")
        return []

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
    """Update a specific game row by id. Only provide the fields you want to update."""
    data = {}
    if active_players is not None:
        data["active_players"] = active_players
    if waiting_players is not None:
        data["waiting_players"] = waiting_players
    if game_state is not None:
        data["game_state"] = game_state

    if not data:
        print("[update_game] No data provided to update.")
        return False

    data["updated_at"] = "NOW()"

    response = supabase.table("games").update(data).eq("id", game_id).execute()
    if response.status_code not in (200, 201):
        print(f"[update_game] Error updating game: status {response.status_code}, data: {response.data}")
        return False
    return True


def reset_game_table():
    """Deletes all games and resets the table."""
    response = supabase.table("games").delete().neq("id", 0).execute()
    if response.status_code not in (200, 201):
        print(f"[reset_game_table] Error resetting table: status {response.status_code}, data: {response.data}")
        return False
    print("[reset_game_table] Game table reset successfully.")
    return True


def initialize_game(game_name: str, active_players=None, waiting_players=None, game_state=None):
    """Add a new game instance to the table."""
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

    if response.status_code not in (200, 201):
        print(f"[initialize_game] Error creating game: status {response.status_code}, data: {response.data}")
        return None

    # Return first inserted row
    if response.data:
        return response.data[0]
    print("[initialize_game] No data returned after insert.")
    return None


def delete_game(game_id: int):
    """Delete a specific game instance by its ID."""
    response = supabase.table("games").delete().eq("id", game_id).execute()
    if response.status_code not in (200, 201):
        print(f"[delete_game] Error deleting game: status {response.status_code}, data: {response.data}")
        return False
    print(f"[delete_game] Game with ID {game_id} deleted successfully.")
    return True
