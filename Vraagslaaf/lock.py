import asyncio
from datetime import datetime, time

import discord
from discord.ext import commands
from discord.ext.commands import Cog

import logging

Log = logging.getLogger(__name__)


class Lockdown(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.locking_guilds = set()
        self.log = ""

    @Cog.listener()
    async def on_ready(self):
        Log.info("Lockdown cog ready")

    async def lock(self, minuten, guild):
        timing = datetime.datetime.now() + datetime.timedelta(minutes=minuten)
        sent_messages = []

        self.lockingGuilds.add(guild)
        for c in guild.text_channels:
            sent_messages.append(await c.send(":lock: Dit kanaal is vanaf nu in **Lockdown** :lock:"))

        class Done(Exception):
            pass  # this is a horrible way to do things, but fuck it

        try:
            while True:
                if datetime.datetime.now() > timing:  # The end of the Lock
                    raise Done
                await asyncio.sleep(1)
        except Done:
            self.lockingGuilds.remove(guild)
            with open("Vraagslaaf/logs/log{}.txt".format(time.strftime("%Y%m%d-%H%M%S")), "w+") as f:
                f.write(self.log)
            for c in guild.text_channels:
                m = await c.send(":ok_hand: Dit kanaal is vanaf nu niet meer in in **Lockdown** :ok_hand:")
                sent_messages.append(m)

            await asyncio.sleep(60)
            for m in sent_messages:
                await m.delete()

    @commands.command(name="lock")
    @commands.has_role("management andy")
    async def locker(self, ctx):
        splits = ctx.message.content.split()
        guild = discord.utils.get(self.bot.guilds, name=" ".join(splits[2:len(splits) - 1]))
        minuten = float(splits[len(splits) - 1])
        self.bot.loop.create_task(self.lock(minuten, guild))
        await ctx.send(f"We locken nu {guild} voor {minuten} minuten")

    async def _locker(self, ctx):
        splits = ctx.message.content.split()
        guild = discord.utils.get(self.bot.guilds, name=" ".join(splits[2:len(splits) - 1]))
        minuten = float(splits[len(splits) - 1])
        self.bot.loop.create_task(self.lock(minuten, guild))
        await ctx.send(f"We locken nu {guild} voor {minuten} minuten")
