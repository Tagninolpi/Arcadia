from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks
from .db_helper import get_games, delete_game

class GameCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_games.start()

    def cog_unload(self):
        self.cleanup_games.cancel()

    @tasks.loop(minutes=5)  # run daily
    async def cleanup_games(self):
        games = get_games()
        now = datetime.now(timezone.utc)  # make sure we’re timezone-aware

        for g in games:
            try:
                # Supabase usually returns ISO8601 strings, e.g. "2025-09-23T18:45:00.123456+00:00"
                last_update = datetime.fromisoformat(g["updated_at"])
            except Exception:
                continue

            if now - last_update > timedelta(days=1):
                delete_game(g["id"])
                #send message

async def setup(bot):
    await bot.add_cog(GameCleaner(bot))
