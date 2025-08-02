import discord
from discord.ext import commands, tasks
from discord import app_commands
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
intents.presences = True

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

        for guild in self.guilds:
            try:
                await self.tree.sync(guild=discord.Object(id=guild.id))
                print(f"🔄 Synced slash commands for guild: {guild.name} ({guild.id})")
            except Exception as e:
                print(f"❌ Failed to sync in guild {guild.id}: {e}")

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

    @tasks.loop(seconds=5)
    async def update_status(self):
        try:
            target_guild_id = 1399923106075771022
            target_guild = self.get_guild(target_guild_id)

            total_members = 0
            if target_guild:
                total_members = sum(1 for member in target_guild.members if not member.bot)

            statuses = [
                f"({total_members}) members in Conzada",
                f"Operating in {len(self.guilds)} servers — Trusted by communities",
                "Conzada.cc | Your Secure option for main accs",
                "System Status: Safe",
            ]

            chosen = random.choice(statuses)
            print(f"🔄 Updating status to: {chosen.replace(chr(10), ' / ')}")
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=chosen
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

bot = Bot()

@bot.tree.command(name="setup", description="Choose a channel to send the info embed to.")
@app_commands.describe(channel="Select the target channel")
async def setup(interaction: discord.Interaction, channel: discord.TextChannel):
    embed = discord.Embed(
        title="Welcome to Conzada!",
        description="Your secure solution for premium services.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Thank you for choosing us!")
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Embed sent to {channel.mention}.", ephemeral=True)

# Main entry point
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
    if os.environ.get('RENDER'):
        asyncio.run(main())
    else:
        bot.run(os.getenv("TOKEN"))
