import logging
import urllib

import aiohttp
import requests
from discord.ext import commands
from discord.ext.commands import Cog
from discord_slash import cog_ext
from discord_slash.context import InteractionContext
from discord_slash.utils.manage_commands import create_option


Log = logging.getLogger(__name__)


class WolframAlpha(commands.Cog):

    def __init__(self):
        import os
        self.key = os.environ.get("WA_APPID")

    @Cog.listener()
    async def on_ready(self):
        Log.info("Wolfram Alpha cog ready")

    @commands.command(name="wa")
    async def wa(self, ctx, *, arg):
        try:
            que = arg
            query = urllib.parse.quote_plus(que)
            query_url = f"http://api.wolframalpha.com/v2/query?" \
                        f"appid={self.key}" \
                        f"&input={query}" \
                        f"&podstate=Result__Step-by-step+solution" \
                        f"&output=json"

            r = requests.get(query_url).json()  # TODO async (aiohttp?)
            if r["queryresult"]["success"] is False:
                await ctx.send("Mn buddies bij Wolframalpha konden geen antwoord vinden :sadge:")
            else:
                data = r["queryresult"]["pods"][:2]  # max 2 pods
                for pod in data:
                    await ctx.channel.send(pod["title"])
                    for subpod in pod["subpods"]:
                        await ctx.channel.send(subpod["img"]["src"])
        except:
            await ctx.channel.send("Mn buddies bij Wolframalpha konden geen antwoord vinden :sadge:")

    @commands.command(name="wm")
    async def wm(self, ctx, *, arg):
        try:
            que = arg
            query = urllib.parse.quote_plus(que)
            query_url = f"http://api.wolframalpha.com/v2/query?" \
                        f"appid={self.key}" \
                        f"&input={query}" \
                        f"&podstate=Result__Step-by-step+solution" \
                        f"&output=json"

            r = requests.get(query_url).json()  # TODO async
            if r["queryresult"]["success"] is False:
                await ctx.send("Mn buddies bij Wolframalpha konden geen antwoord vinden :sadge:")
            else:
                data = r["queryresult"]["pods"]  # no limit on pods
                for pod in data:
                    await ctx.channel.send(pod["title"])
                    for subpod in pod["subpods"]:
                        await ctx.channel.send(subpod["img"]["src"])
        except:
            await ctx.channel.send("Mn buddies bij Wolframalpha konden geen antwoord vinden :sadge:")


    @cog_ext.cog_slash(name="wa",
                           description="Vraagt een Wolfram Alpha query op.",
                       guild_ids=[790602506429923328,  # test server
                                  757496517065048124  # main server
                                  ],
                           options=[
                               create_option(
                                   name="query",
                                   description="Een vraag voor Wolfram alpha. Bijvoorbeeld: integrate 4x+1.",
                                   option_type=3,
                                   required=True),
                               create_option(
                                   name="uitgebreid",
                                   description="Indien ja, geeft meer informatie weer over je query.",
                                   option_type=5,
                                   required=False)
                           ])
    async def _wolfram(self, ctx: InteractionContext, query: str, uitgebreid: bool = False):
        await ctx.defer()
        parsed_query = urllib.parse.quote_plus(query)
        try:
            query_url = f"http://api.wolframalpha.com/v2/query?" \
                        f"appid={self.key}" \
                        f"&input={parsed_query}" \
                        f"&podstate=Result__Step-by-step+solution" \
                        f"&output=json"

            # Quick note on the usage of ctx.defer, ctx.send and ctx.channel.send. ctx.send will ping the user for
            # every message and is really ugly for responses that contain multiple messages (like this one),
            # and will also not show up to other users; so usage of ctx.channel.send is preferred. When deferring a
            # message however, it will not delete the deferment, so we have to call ctx.send atleast once.
            async with aiohttp.ClientSession() as session:
                async with session.get(query_url) as r:
                    if not r.status == 200:
                        await ctx.send("Mn buddies bij Wolframalpha konden geen antwoord vinden.")
                    else:
                        response = await r.json() # unintuitively, this is actualy returns dict format than string json.
                        if response["queryresult"]["success"] is False:
                            await ctx.send("Mn buddies bij Wolframalpha konden geen antwoord vinden.")
                        else:
                            data = response["queryresult"]["pods"]
                            for i, pod in enumerate(data):
                                await ctx.channel.send(pod["title"])
                                for subpod in pod["subpods"]:
                                    await ctx.channel.send(subpod["img"]["src"])
                                if i >= 2 and uitgebreid is False:
                                    break
                            await ctx.send("Succes!")
        except:  # something else went wrong with the request
            await ctx.send("Mn buddies bij Wolframalpha konden geen antwoord vinden.")



