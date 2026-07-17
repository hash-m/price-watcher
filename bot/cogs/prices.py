import discord
import math
import asyncio

from bot.analytics.charts import convert_chart_to_png,create_history_chart
from bot.analytics.stats  import get_stats
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
            icon_url=interaction.user.display_avatar.url
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
        embed = discord.Embed(
            color=16777215
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        product = await get_product(url,interaction.user.id)

        if not product:
            embed.title = "Fail"
            embed.description = "Product isn't being watched."
            await interaction.response.send_message(embed=embed)
            return

        snapshots = await get_snapshots(product[0])
        
        if not snapshots:
            embed.title = "Fail"
            embed.description = "Product hasn't gotten any of its scrapes stored."
            await interaction.response.send_message(embed=embed)
            return

        fig = await asyncio.to_thread(create_history_chart, product[1], snapshots)
        file = await asyncio.to_thread(convert_chart_to_png, fig)

        embed.set_image(url="attachment://chart.png")   
        await interaction.response.send_message(embed=embed,file=file)


    @app_commands.command(name="stats", description="Some statistics of a product")
    async def stats(self, interaction : discord.Interaction, url : str):
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

        if not snapshots:
            embed.title = "Fail"
            embed.description = "Product hasn't gotten any of its scrapes stored."
            await interaction.response.send_message(embed=embed)
            return

        high, low, mean, percentage = get_stats(snapshots)

        def format_price(value):
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return "N/A"
            return f"£{value:.2f}"

        def format_signed(value, suffix=""):
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return "N/A"
            return f"{value:+.2f}{suffix}"

        embed.title = "Product Stats"
        embed.url = url

        embed.add_field(name="All-Time High", value=format_price(high), inline=True)
        embed.add_field(name="All-Time Low", value=format_price(low), inline=True)

        embed.add_field(name="All-Time Mean", value=format_price(mean), inline=True)
        embed.add_field(name="Change Since First Recorded", value=format_signed(percentage, "%"), inline=True)

        await interaction.response.send_message(embed=embed)
        
    
async def setup(bot : commands.Bot):
    await bot.add_cog(PricesCog(bot))