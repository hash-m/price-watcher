import discord

async def send_error_msg(interaction : discord.Interaction, msg : str,title : str = "Error"):
    embed = discord.Embed(color=discord.Colour.red())
    embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )

    embed.title = "Fail"
    embed.description = msg    
    await interaction.response.send_message(embed=embed)