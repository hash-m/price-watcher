import discord
from discord.ext import commands
from discord import app_commands

class WatchingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="watch", description="Watch for a product to go on sale")
    async def watch(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Watching {url}\ntrust me bro")

    @app_commands.command(name="unwatch", description="Remove a watcher on a link")
    async def unwatch(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Removed watchter on {url}\ntrust me bro")

    @app_commands.command(name="list", description="List all urls being watched")
    async def list_items(self, interaction : discord.Interaction):
        await interaction.response.send_message(f"Here is the list of watches")
    
async def setup(bot : commands.Bot):
    await bot.add_cog(WatchingCog(bot))