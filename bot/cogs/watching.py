import discord

from bot.utils            import send_error_msg
from bot.logic            import watch_product,unwatch_product
from bot.scraper.core     import get_functions 
from bot.database.queries import get_products
from discord.ext          import commands
from discord              import app_commands
    

class WatchingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="watch", description="Watch a product")
    async def watch(self, interaction : discord.Interaction, url : str):

        if not get_functions(url):
            await send_error_msg(interaction,"Not a valid URL.","Fail")
            return

        embed = discord.Embed(color=discord.Colour.green())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.title = "Watching 👀"
        msg = await watch_product(url,interaction.channel_id,interaction.user.id)
        embed.description = msg

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unwatch", description="Remove a watcher on a product")
    async def unwatch(self, interaction : discord.Interaction, url : str):
        if not get_functions(url):
            await send_error_msg(interaction,"Not a valid URL.","Fail")
            return

        embed = discord.Embed(color=discord.Colour.green())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.title = "Removed"
        msg = await unwatch_product(url,interaction.user.id)
        embed.description = msg

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list", description="List all products being watched")
    async def list_items(self, interaction : discord.Interaction):
        embed = discord.Embed(
            title="Watchlist 👀",
            color=discord.Colour.green(),
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        products = await get_products(interaction.user.id)
        description = ""

        for product in products:
            product_name = product[1] or "Waiting For Name.." #product name will be there right after /watch once I add something to make the polls faster
            product_link = product[2]
            description += f"[**{product_name}**]({product_link})\n"

        embed.description = description

        await interaction.response.send_message(embed=embed)
    
async def setup(bot : commands.Bot):
    await bot.add_cog(WatchingCog(bot))