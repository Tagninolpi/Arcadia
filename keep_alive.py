from flask import Flask
from threading import Thread

# Create Flask app
app = Flask('')

@app.route('/')
def home():
    return "Arcadia bot is alive ✅"

def run():
    # Render automatically sets PORT environment variable
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # Run Flask app in a separate thread so it doesn't block the bot
    t = Thread(target=run)
    t.start()
