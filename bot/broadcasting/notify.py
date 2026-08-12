import discord
from bot.instance import bot

async def send_embed_to_user(channel_id,user_id,embed):
    channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
    await channel.send(content=f"<@{user_id}>", embed=embed)