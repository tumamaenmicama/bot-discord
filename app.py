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

# Load environment variables
load_dotenv()

# Bot intents
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

# Flask Setup
app = Flask(__name__)
bot_name = "Loading..."

@app.route('/')
def home():
    return f"Bot {bot_name} is operational"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Discord Bot Class
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        try:
            await self.load_extension("cogs.infoCommands")
            print("✅ Successfully loaded InfoCommands cog")
        except Exception as e:
            print(f"❌ Failed to load cog: {e}")
            traceback.print_exc()

        await self.tree.sync()
        self.update_status.start()

    async def on_ready(self):
        global bot_name
        bot_name = str(self.user)
        print(f"\n🔗 Connected as {bot_name}")
        print(f"🌐 Serving {len(self.guilds)} servers")

        if os.environ.get('RENDER'):
            import threading
            threading.Thread(target=run_flask, daemon=True).start()
            print("🚀 Flask server started in background")

    @tasks.loop(minutes=5)
    async def update_status(self):
        try:
            statuses = [
                "👁️ Escaping Limits | Conzada.cc",
                f"📡 Connected to {len(self.guilds)} networks",
                f"⚙️ Operating across {len(self.guilds)} servers",
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
            await self.change_presence(activity=activity)
        except Exception as e:
            print(f"⚠️ Status update failed: {e}")

    @update_status.before_loop
    async def before_status_update(self):
        await self.wait_until_ready()

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

# Main entry point
async def main():
    bot = Bot()
    try:
        await bot.start(os.getenv("TOKEN"))
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        print(f"⚠️ Critical error: {e}")
        traceback.print_exc()
        await bot.close()

if __name__ == "__main__":
    if os.environ.get('RENDER'):
        asyncio.run(main())
    else:
        bot = Bot()
        bot.run(os.getenv("TOKEN"))
