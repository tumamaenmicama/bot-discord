import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from datetime import datetime
import json
import os
import asyncio
import io
import uuid
import gc

CONFIG_FILE = "info_channels.json"

class InfoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://api.discord.bio/v1/user/"
        self.config_data = self.load_config()

        @app_commands.command(name="setup", description="Register info channels for this server")
        async def setup_slash(interaction: discord.Interaction):
            await interaction.response.send_message("Use `!setinfochannel` to set allowed channels.", ephemeral=True)

        self.bot.tree.add_command(setup_slash)

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return {"servers": {}, "global_settings": {"default_cooldown": 5}}
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f, indent=4)

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

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))
