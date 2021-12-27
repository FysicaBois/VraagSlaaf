import os
import random

import discord
from discord.ext import commands
#changed something

class Study(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tomstatistiekstelling = os.listdir(
            "Vraagslaaf/studytomstatistiek/stellingen"
        )
        self.tomstatistiekbewijs = os.listdir(
            "Vraagslaaf/studytomstatistiek/bewijzen"
        )

    @commands.command()
    async def stat(self, ctx, num=None):
        if num is None:
            stelling = random.choice(self.tomstatistiekstelling)
            size = len(stelling)
            bewijs = f"{stelling[:size - 4]}" + "bewijs" + ".jpg"
            spoiler = discord.File(
                "Vraagslaaf/studytomstatistiek/bewijzen/{}".format(
                    bewijs
                )
            )
            spoiler.filename = f"SPOILER_{spoiler.filename}"
            await ctx.reply(
                file=discord.File(
                    "Vraagslaaf/studytomstatistiek/stellingen/{}".format(
                        stelling
                    )
                )
            )
            await ctx.send(file=spoiler)
            await ctx.message.add_reaction(emoji="✅")

            return

        else:
            if len(num) > 1 or num not in "123456789":
                await ctx.send("Baguette kon dit niet interpreteren...")
                return
            new_stellingen = []
            for x in self.tomstatistiekstelling:
                if x.startswith(num):
                    new_stellingen.append(x)
            stelling = random.choice(new_stellingen)
            size = len(stelling)
            bewijs = f"{stelling[:size - 4]}" + "bewijs" + ".jpg"
            spoiler = discord.File(
                "Vraagslaaf/studytomstatistiek/bewijzen/{}".format(
                    bewijs
                )
            )
            spoiler.filename = f"SPOILER_{spoiler.filename}"
            await ctx.reply(
                file=discord.File(
                    "Vraagslaaf/studytomstatistiek/stellingen/{}".format(
                        stelling
                    )
                )
            )
            await ctx.send(file=spoiler)
            await ctx.message.add_reaction(emoji="✅")

            return
