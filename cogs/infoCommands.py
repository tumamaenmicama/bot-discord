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

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return {"servers": {}, "global_settings": {"default_cooldown": 5}}
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f, indent=4)

    # ─────────────────────────────────────────────────────
    # Slash command /setup
    # ─────────────────────────────────────────────────────
    @app_commands.command(name="setup", description="Set the channel where info embeds will be sent")
    async def setup_slash(self, interaction: discord.Interaction):
        class ChannelSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label=channel.name,
                        description="Text channel",
                        value=str(channel.id)
                    )
                    for channel in interaction.guild.text_channels[:25]  # Discord limits to 25 options
                ]
                super().__init__(placeholder="Choose a channel", min_values=1, max_values=1, options=options)

            async def callback(self, select_interaction: discord.Interaction):
                selected_channel_id = self.values[0]
                guild_id = str(interaction.guild.id)

                # Update config
                if guild_id not in self.view.cog.config_data["servers"]:
                    self.view.cog.config_data["servers"][guild_id] = {
                        "info_channels": [],
                        "config": {}
                    }

                self.view.cog.config_data["servers"][guild_id]["info_channels"] = [selected_channel_id]
                self.view.cog.save_config()

                selected_channel = interaction.guild.get_channel(int(selected_channel_id))
                await select_interaction.response.send_message(
                    f"✅ Info embed channel set to {selected_channel.mention}", ephemeral=True)

                # Send confirmation embed in selected channel
                embed = discord.Embed(
                    title="✅ Info Channel Setup",
                    description="This channel has been registered to receive info commands.",
                    color=discord.Color.green()
                )
                await selected_channel.send(embed=embed)

        class SetupView(discord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=60)
                self.cog = cog
                self.add_item(ChannelSelect())
        
        await interaction.response.send_message("Select a channel to set as the info target:", view=SetupView(self), ephemeral=True)

    # ─────────────────────────────────────────────────────
    # Legacy hybrid command to list info channels
    # ─────────────────────────────────────────────────────
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
