import discord
from discord.ext import commands, tasks
import os
import traceback
from flask import Flask
import sys
import aiohttp
import asyncio

import random

from dotenv import load_dotenv


intents = discord.Intents.default()
intents.guilds = True  # Needed for len(bot.guilds)

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize environment variables
load_dotenv()

# Flask Setup
app = Flask(__name__)
bot_name = "Loading..."

@app.route('/')
def home():
    """Health check endpoint for Render"""
    return f"Bot {bot_name} is operational"

def run_flask():
    """Run Flask with Render-compatible settings"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Discord Bot Setup
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Missing TOKEN in environment")

class Bot(commands.Bot):
    def __init__(self):
        # Configure minimal required intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.session = None

    async def setup_hook(self):
        """Initialize bot components"""
        self.session = aiohttp.ClientSession()
        
        # Load cogs
        try:
            await self.load_extension("cogs.infoCommands")
            print("✅ Successfully loaded InfoCommands cog")
        except Exception as e:
            print(f"❌ Failed to load cog: {e}")
            traceback.print_exc()
        
        await self.tree.sync()
        self.update_status.start()

    async def on_ready(self):
        """When bot connects to Discord"""
        global bot_name
        bot_name = str(self.user)
        
        print(f"\n🔗 Connected as {bot_name}")
        print(f"🌐 Serving {len(self.guilds)} servers")
        
        # Start Flask if running on Render
        if os.environ.get('RENDER'):
            import threading
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            print("🚀 Flask server started in background")

    @tasks.loop(minutes=5)
    try:
        statuses = [
            "👁️ Escaping Limits | Conzada.cc",
            f"📡 Connected to {len(bot.guilds)} networks",
            f"⚙️ Operating across {len(bot.guilds)} servers",
            "🚀 Conzada.cc • Adaptive Core Online",
            "🧠 Evolving System | Conzada.cc",
            "🔐 Accumulating Escape Nodes...",
            "🌐 Quantum Proxy Active | Conzada.cc",
            "🦾 Autonomous Protocols Engaged",
        ]
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=random.choice(statuses)
        )
        await bot.change_presence(activity=activity)
    except Exception as e:
        print(f"⚠️ Status update failed: {e}")

@update_status.before_loop
async def before_status_update():
    await bot.wait_until_ready()

# Start loop after bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    update_status.start()  # Start the status update loop


    async def close(self):
        """Cleanup on shutdown"""
        if self.session:
            await self.session.close()
        await super().close()

async def main():
    bot = Bot()
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        print(f"⚠️ Critical error: {e}")
        traceback.print_exc()
        await bot.close()

if __name__ == "__main__":
    # Special handling for Render's environment
    if os.environ.get('RENDER'):
        asyncio.run(main())
    else:
        bot = Bot()
        bot.run(TOKEN)
