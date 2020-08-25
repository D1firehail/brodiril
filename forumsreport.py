import asyncio
import discord
from discord.ext import commands
import staticconfig


async def try_delete(bot: commands.Bot, payload: discord.RawReactionActionEvent) -> None:
    if payload.user_id != staticconfig.bot_id:
        if payload.emoji.id == staticconfig.Vandiland.emoji_kekban:
            if payload.channel_id == staticconfig.Vandiland.forums_channel_id:

                vandiland:            discord.Guild = bot.get_guild(staticconfig.Vandiland.vandiland_id)
                member:              discord.Member = vandiland.get_member(payload.user_id)
                channel:        discord.TextChannel = bot.get_channel(payload.channel_id)
                bug_admin_role:        discord.Role = vandiland.get_role(staticconfig.Vandiland.bug_administrator)

                if bug_admin_role in member.roles:
                    message:        discord.Message = await channel.fetch_message(payload.message_id)

                    await channel.delete_messages([message])
