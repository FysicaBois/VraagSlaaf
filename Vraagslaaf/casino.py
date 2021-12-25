import discord
from discord.ext import commands
from discord.ext import tasks
import json
import requests
import asyncio
import random

import logging
Log = logging.getLogger(__name__)


class Casino(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot_spam_channel_id = 758614747800666143  # todo change this for deployment
        self.form = None
        self.smh = self.SlotMachineHandler()
        self.blackjackplayers = []

        with open("Vraagslaaf/players.json", "r") as playersfile:
            if playersfile.read(1):
                playersfile.seek(0)
                self.players = json.load(playersfile)
                if len(self.players) == 0:
                    self.started = False
                else:
                    self.started = True
            else:
                self.started = False
                self.players = list()

    @commands.Cog.listener()
    async def on_ready(self):
        Log.info("Casino Cog is Loaded")
        self.spam_chann = discord.utils.get(self.bot.get_all_channels(), id=self.bot_spam_channel_id)
        self.smh.spam_chann = self.spam_chann
        self.update_players_file.start()

    @tasks.loop(seconds=10)
    async def update_players_file(self):
        with open("players.json", "w") as playersfile:
            playersfile.write(json.dumps(self.players))


    @commands.command(name="casino")
    async def casino_commands(self, ctx, *, argv):
        if argv == "join":
            try:
                member_name = ctx.author.name
                if member_name in self.players:
                    await ctx.channel.send(":x: __Je kan maar 1 keer je startbudget krijgen!__, gij cheeky bastard.")
                else:
                    await self.spam_chann.send(f"!pac {ctx.author.mention} 200")
                    await ctx.channel.send(":white_check_mark: __Je hebt 200C Ontvangen.__ Go on and play!",
                                           mention_author=True)
                    self.players.append(member_name)
            except:
                await ctx.channel.send(":question: __Er is iets foutgegaan__. probeer opnieuw!")


    async def get_balans(self, ctx) -> int:
        await self.spam_chann.send(f"!pw {ctx.author.mention}")

        # this help function
        def is_correct(before: discord.Message, after: discord.Message):
            try:
                if after.channel == self.spam_chann:
                    if after.embeds:
                        person_id = int(after.embeds[0].description.split("<")[1].split(">")[0][1:])
                        if ctx.author.id == person_id:
                            return True
                return False
            except:  # if an error occurs, likewise return false
                return False

        _, after = await self.bot.wait_for("message_edit", check=is_correct, timeout=5)

        amount = int(after.embeds[0].description.split("**")[1].rstrip(" chips"))
        return amount


    async def check_no_balansen(self, ctx) -> bool:
        await self.spam_chann.send(f"!pcr")

        # this help function
        def is_correct(before: discord.Message, after: discord.Message):
            try:
                if after.channel == self.spam_chann:
                    if after.embeds:
                        if after.embeds[0].title == ":black_joker: **Poker Now Discord Club TOP 10 chips leaderboard** :black_joker:":
                           return True
            except:  # if an error occurs, likewise return false
                return False

        _, after = await self.bot.wait_for("message_edit", check=is_correct, timeout=5)

        if after.embeds[0].description == "":
            return True
        return False

    @commands.command(name="rol")
    async def slot_machine(self, ctx, *, argv):
        try:
            amount = int(argv)
        except:
            await ctx.send(":x: __Verkeerd geld ingegeven__, probeer opnieuw.")
            return

        if amount <= 0:
            await ctx.send(":x: __Je moet minstens 1 coin gokken__, probeer opnieuw.")
            return

        if amount > await self.get_balans(ctx):
            await ctx.send(":x: __Je hebt niet genoeg geld__, probeer opnieuw.")
            return

        await self.spam_chann.send(f"!prc {ctx.author.mention} {amount}")
        self.smh.queue.append((ctx, amount))

    class SlotMachineHandler:

        def __init__(self):
            self.queue = list()
            self.busy = False
            self.current = None
            self.form = None
            self.spam_chann = None
            self.server_message = None

            self.check_if_nonempty_queue.start()


        @tasks.loop(seconds=1)
        async def check_if_nonempty_queue(self):
            if not self.busy:
                if len(self.queue) > 0:
                    self.busy = True
                    self.current = self.queue.pop()
                    await self.set_server_message()

        async def set_server_message(self):
          rolls = [random.randint(1,15) for _ in range(3)]
          self.server_message = json.dumps({"name": self.current[0].author.name, "rolls": rolls})
          await asyncio.sleep(0.5)
          self.server_message = None
          await asyncio.sleep(8)
          await self.result(rolls, self.current[1])
          

        async def result(self, results, amount):
              if len(set(results)) == 3:
                await self.current[0].send(":grimacing: __Geen enkele figuur hetzelfde__, misschien de volgende keer meer geluk chief.")
              if len(set(results)) == 2:
                await self.spam_chann.send(f"!pac {self.current[0].author.mention} {self.current[1] * 8}")
                await self.current[0].send(":rocket: __Twee dezelfde figuren__, Goed gedaan chief!.")
              if len(set(results)) == 1:
                await self.spam_chann.send(f"!pac {self.current[0].author.mention} {self.current[1] * 25}")
                await self.current[0].send(":fireworks: __Drie dezelde figuren__, Lucky bastard!")

              self.busy = False
              self.current = None
              self.form = None
            
           



                    
