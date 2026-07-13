import discord

from bot.database.queries import get_snapshots,get_product
from discord.ext          import commands
from discord              import app_commands

class PricesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="price", description="Retrieve the current price of a product")
    async def price(self, interaction : discord.Interaction, url : str):
        product = await get_product(url,interaction.user.id)

        if not product:
            await interaction.response.send_message(f"That product isn't being watched")
            return

        snapshots = await get_snapshots(product[0])
        newest_snapshot = snapshots[0] if snapshots else None

        await interaction.response.send_message(f"Here is the current price..\n {newest_snapshot}")

    @app_commands.command(name="history", description="Retrieve the price history of a product")
    async def history(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Here is the price history..")

    @app_commands.command(name="stats", description="Some statistics of a product")
    async def stats(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Here are some stats..")
    
async def setup(bot : commands.Bot):
    await bot.add_cog(PricesCog(bot))