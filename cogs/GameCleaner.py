from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks
from .db_helper import get_games, delete_game

class GameCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_games.start()

    def cog_unload(self):
        self.cleanup_games.cancel()

    @tasks.loop(hours=24)  # run daily
    async def cleanup_games(self):
        games = get_games()
        now = datetime.now(timezone.utc)

        for g in games:
            # Skip games with no active players
            if not g.get("active_players"):
                continue

            try:
                last_update = datetime.fromisoformat(g["updated_at"])
                if last_update.tzinfo is None:  # fix naive datetimes
                    last_update = last_update.replace(tzinfo=timezone.utc)
            except Exception:
                continue

            if now - last_update > timedelta(days=1):
                delete_game(g["id"])
                # TODO: send message to log channel if needed

async def setup(bot):
    await bot.add_cog(GameCleaner(bot))
