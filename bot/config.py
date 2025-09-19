import os

class Config:
    # Discord bot token (set in Render environment variables)
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Command prefix (not used for slash commands, but kept for reference)
    COMMAND_PREFIX = "/"

    @staticmethod
    def validate():
        """Ensure all required environment variables are set."""
        if not Config.DISCORD_TOKEN:
            raise ValueError("❌ DISCORD_TOKEN is not set in environment variables")
