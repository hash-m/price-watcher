import discord

from bot.database.queries import get_snapshots,get_product
from discord.ext          import commands
from discord              import app_commands

class PricesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="price", description="Retrieve the current price of a product")
    async def price(self, interaction : discord.Interaction, url : str):
        embed = discord.Embed(
            color=16777215
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_icon
        )

        product = await get_product(url,interaction.user.id)

        if not product:
            embed.title = "Fail"
            embed.description = "Product isn't being watched."
            await interaction.response.send_message(embed=embed)
            return

        snapshots = await get_snapshots(product[0])
        newest_snapshot = snapshots[0] if snapshots else None

        if newest_snapshot:
            embed.title = "Success"
            embed.description = f"Current Price: £{newest_snapshot[2]}"
        else:
            embed.title = "Fail"
            embed.description = f"No price is available yet. Try again later."

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="history", description="Retrieve the price history of a product")
    async def history(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Here is the price history..")

    @app_commands.command(name="stats", description="Some statistics of a product")
    async def stats(self, interaction : discord.Interaction, url : str):
        await interaction.response.send_message(f"Here are some stats..")
    
async def setup(bot : commands.Bot):
    await bot.add_cog(PricesCog(bot))