import os

class Config:
    # Discord bot token (set in Render environment variables)
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Command prefix (not used for slash commands, but kept for reference)
    COMMAND_PREFIX = "/"

    
    ### Variables
    allowed_channel_ids = (1406937106458345623,1406937107624235028)#(1096043268669702225,1281729821503914106)
    
    @staticmethod
    def validate():
        """Ensure all required environment variables are set."""
        if not Config.DISCORD_TOKEN:
            raise ValueError("❌ DISCORD_TOKEN is not set in environment variables")
    
