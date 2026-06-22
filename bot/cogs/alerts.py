import discord
from discord.ext import commands
from discord import app_commands

class AlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="alert", description="Make a condition for you to be alerted")
    async def alert(self, interaction : discord.Interaction, url : str, conditions : str):
        await interaction.response.send_message(f"I will alert you for {url}\ntrust me bro")

    @app_commands.command(name="unalert", description="Remove an alert")
    async def unalert(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"I will remove the alert you for {url}\ntrust me bro")
    
async def setup(bot : commands.Bot):
    await bot.add_cog(AlertsCog(bot))