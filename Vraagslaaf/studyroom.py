"""
Async implementation of the calendar stuff i had previously
"""
# read client and user creds
import logging

import discord
from discord import Role, Forbidden
from discord.ext import tasks

Log = logging.getLogger(__name__)

from discord.ext.commands import Cog


class StudyRoom(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.room_id = 846437226190864425
        self.role_id = 859760521292152852
        self.een_id = 758627609499926538
        self.twee_id = 884803430311424041
        self.eerstejaars = set()
        self.tweedejaars = set()


    @Cog.listener()
    async def on_ready(self):
        Log.info("Studyroom Cog loaded")
        self.room = discord.utils.get(self.bot.get_all_channels(), id=self.room_id)
        self.role: Role = discord.utils.get(self.room.guild.roles, id=self.role_id)
        self.een = discord.utils.get(self.room.guild.roles, id=self.een_id)
        self.twee = discord.utils.get(self.room.guild.roles, id=self.twee_id)


    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is self.room and not after.channel is self.room:
            await member.add_roles(self.role)
            if member in self.eerstejaars:
                await member.add_roles(self.een)
            if member in self.tweedejaars:
                await member.add_roles(self.twee)

        if after.channel is self.room and not before.channel is self.room:
            await member.remove_roles(self.role)
            if self.een in member.roles:
                self.eerstejaars.add(member)
                await member.remove_roles(self.een)
            if self.twee in member.roles:
                self.tweedejaars.add(member)
                await member.remove_roles(self.twee)

