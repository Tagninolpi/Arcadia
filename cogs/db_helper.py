from supabase import create_client
import os
from datetime import datetime

# ------------------ Supabase Client ------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ Functions ------------------

def get_games():
    """Fetch all games from the table and format them as a list of dictionaries."""
    response = supabase.table("games").select("*").execute()

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
        return False

    data["updated_at"] = datetime.utcnow().isoformat()
    supabase.table("games").update(data).eq("id", game_id).execute()
    return True


def reset_game_table():
    """Deletes all games and resets the table."""
    supabase.table("games").delete().neq("id", 0).execute()
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
        "updated_at": datetime.utcnow().isoformat()
    }

    response = supabase.table("games").insert(new_game).execute()
    return response.data[0] if response.data else None  # return first inserted row or None


def delete_game(game_id: int):
    """Delete a specific game instance by its ID."""
    supabase.table("games").delete().eq("id", game_id).execute()
    return True

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
        return False

    data["updated_at"] = datetime.utcnow().isoformat()
    supabase.table("games").update(data).eq("id", game_id).execute()
    return True


def reset_game_table():
    """Deletes all games and resets the table."""
    supabase.table("games").delete().neq("id", 0).execute()
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
        "updated_at": datetime.utcnow().isoformat()
    }

    response = supabase.table("games").insert(new_game).execute()
    return response.data[0] if response.data else None  # return first inserted row or None


def delete_game(game_id: int):
    """Delete a specific game instance by its ID."""
    supabase.table("games").delete().eq("id", game_id).execute()
    return True
