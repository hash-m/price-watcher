import discord
from discord.ext import commands
from discord import app_commands

class PricesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="price", description="Watch and record the price of a product")
    async def price(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Watching the price of {url}\ntrust me bro")

    @app_commands.command(name="history", description="Retrieve the price history of a product")
    async def history(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Here is the price history..")

    @app_commands.command(name="stats", description="Some statistics of a product")
    async def stats(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Here are some stats..")
    
async def setup(bot : commands.Bot):
    await bot.add_cog(PricesCog(bot))