import discord

from discord.ext import commands
from discord     import app_commands

from bot.utils.helper_functions import send_error_msg
from bot.database.queries       import get_snapshots,get_product

class GetCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    get_group = app_commands.Group(name = "get", description="get something about a product")

    @get_group.command(name="price", description="Get the current price of a product")
    async def price(self, interaction : discord.Interaction, url : str):
        product = await get_product(url)

        if not product:
            await send_error_msg(interaction,"Product isn't being watched.","Fail")
            return

        snapshots = await get_snapshots(product[0])
        newest_snapshot = snapshots[0] if snapshots else None

        if newest_snapshot:
            embed = discord.Embed(color=discord.Colour.green())
            embed.set_author(name=interaction.user.display_name,icon_url=interaction.user.display_avatar.url)
            embed.title = f"{product[1] if product[1] else "Price"}"
            embed.url   = product[2]
            embed.description = f"Current Price: £{newest_snapshot[2]:.2f}"

            await interaction.response.send_message(embed=embed)
        else:
            await send_error_msg(interaction,"No price is available yet. Try again later.","Fail")

    @get_group.command(name="availability", description="Get the availability status of the product")
    async def availability(self, interaction : discord.Interaction, url : str):
        product = await get_product(url)
            
        if not product:
            await send_error_msg(interaction,"Product isn't being watched.","Fail")
            return

        availability = product[3]

        if availability is not None:
            embed = discord.Embed(color=discord.Colour.green() if availability else discord.Colour.red())
            embed.set_author(name=interaction.user.display_name,icon_url=interaction.user.display_avatar.url)
            embed.title = f"{product[1] if product[1] else "Availability"}"
            embed.url   = product[2]
            embed.description = f"Status: {"Available" if availability else "Unavailable"}"

            await interaction.response.send_message(embed=embed)
        else:
            await send_error_msg(interaction,"Unable to determine its availability yet. Try again later.","Fail")

async def setup(bot : commands.Bot):
    await bot.add_cog(GetCog(bot))