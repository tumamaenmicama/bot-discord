import discord
from discord.ext import commands
from discord import app_commands
import json
import os

CONFIG_FILE = "info_channels.json"

class InfoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_data = self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return {"servers": {}, "global_settings": {"default_cooldown": 5}}
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f, indent=4)

    # ────── 🟦 SLASH COMMAND: /setup channel ──────
    @app_commands.command(name="setup", description="Register an info channel to send messages to")
    @app_commands.describe(channel="Select a channel to register as info channel")
    async def setup_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        channel_id = str(channel.id)

        # Store in config
        if guild_id not in self.config_data["servers"]:
            self.config_data["servers"][guild_id] = {
                "info_channels": [],
                "config": {}
            }

        if channel_id not in self.config_data["servers"][guild_id]["info_channels"]:
            self.config_data["servers"][guild_id]["info_channels"].append(channel_id)
            self.save_config()

        # Send embed to selected channel
        embed = discord.Embed(
            title="✅ Info Channel Registered",
            description=f"This channel has been registered for `!info` commands.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

        # Respond to user
        await interaction.response.send_message(
            f"✅ Channel {channel.mention} registered and notified!",
            ephemeral=True
        )

    # ────── HYBRID: /infochannels ──────
    @commands.hybrid_command(name="infochannels", description="List allowed channels")
    async def list_info_channels(self, ctx: commands.Context):
        guild_id = str(ctx.guild.id)

        if guild_id in self.config_data["servers"] and self.config_data["servers"][guild_id]["info_channels"]:
            channels = []
            for channel_id in self.config_data["servers"][guild_id]["info_channels"]:
                channel = ctx.guild.get_channel(int(channel_id))
                channels.append(f"• {channel.mention if channel else f'ID: {channel_id}'}")

            embed = discord.Embed(
                title="Allowed channels for !info",
                description="\n".join(channels),
                color=discord.Color.blue()
            )
            cooldown = self.config_data["servers"][guild_id]["config"].get("cooldown", self.config_data["global_settings"]["default_cooldown"])
            embed.set_footer(text=f"Current cooldown: {cooldown} seconds")
        else:
            embed = discord.Embed(
                title="Allowed channels for !info",
                description="All channels are allowed (no restriction configured)",
                color=discord.Color.blue()
            )

        await ctx.send(embed=embed)

    # Required to sync the slash command
    async def cog_load(self):
        self.bot.tree.add_command(self.setup_slash)

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))
