import discord
from discord.ext import commands, tasks
from discord import app_commands
import os, traceback, aiohttp, asyncio, random
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot intents
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

# Flask setup
app = Flask(__name__)
bot_name = "Loading..."

@app.route('/')
def home():
    return f"Bot {bot_name} is operational"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        try:
            await self.load_extension("cogs.infoCommands")
            print("✅ Loaded InfoCommands cog")
        except Exception as e:
            print(f"❌ Cog load failed: {e}")
            traceback.print_exc()

        # Sync application (slash) commands per guild
        await self.wait_until_ready()
        for guild in self.guilds:
            try:
                await self.tree.sync(guild=discord.Object(id=guild.id))
                print(f"🔄 Synced slash commands for {guild.name} ({guild.id})")
            except Exception as e:
                print(f"❌ Failed to sync for guild {guild.id}: {e}")

        # Start presence updater
        self.update_status.start()

    async def on_ready(self):
        global bot_name
        bot_name = str(self.user)
        print(f"\n🔗 Connected as {bot_name}")
        print(f"🌐 Serving {len(self.guilds)} servers")

        if os.getenv('RENDER'):
            import threading
            threading.Thread(target=run_flask, daemon=True).start()
            print("🚀 Flask web server started")

    @tasks.loop(seconds=5)
    async def update_status(self):
        try:
            target = self.get_guild(int(os.getenv("STATUS_GUILD_ID", 0)))
            total = sum(1 for m in target.members if not m.bot) if target else 0
            statuses = [
                f"({total}) members in Conzada",
                f"Operating in {len(self.guilds)} servers — Trusted by communities",
                "Conzada.cc | Secure option for main accs",
                "System Status: Safe",
            ]
            choice = random.choice(statuses)
            print(f"🔄 Activity: {choice}")
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=choice))
        except Exception as e:
            print(f"⚠️ Status update error: {e}")

    @update_status.before_loop
    async def before_status_update(self):
        await self.wait_until_ready()

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

bot = Bot()

# Register the /setup command globally
@bot.tree.command(name="setup", description="Choose a channel to send the info embed to.")
@app_commands.describe(channel="Select the target text channel")
async def setup(interaction: discord.Interaction, channel: discord.TextChannel):
    embed = discord.Embed(
        title="📢 Welcome to Conzada!",
        description="Your secure solution for premium services.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Thank you for choosing us!")
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Embed sent to {channel.mention}.", ephemeral=True)

async def main():
    try:
        await bot.start(os.getenv("TOKEN"))
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        print(f"⚠️ Critical error: {e}")
        traceback.print_exc()
        await bot.close()

if __name__ == "__main__":
    if os.getenv('RENDER'):
        asyncio.run(main())
    else:
        bot.run(os.getenv("TOKEN"))
