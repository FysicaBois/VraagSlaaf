import re
import textwrap

import discord
import feedparser

from discord.ext import commands, tasks
from discord.ext.commands import Bot

from Vraagslaaf.cogs.VraagslaafCog import VraagslaafCog
from Vraagslaaf.comms import Comms


class Ufora(VraagslaafCog):

    def __init__(self, bot: Bot, comms: Comms):
        super().__init__(bot, comms)

        self.first_year_links = set()

        self.first_year_channel_id = 886578406085521458

        self.second_year_links = {
            "https://ufora.ugent.be/d2l/le/news/rss/439516/course?token=a0qvbudg77ub90l815d0d&ou=439516",  # exp 2
            "https://ufora.ugent.be/d2l/le/news/rss/451084/course?token=a0qvbudg77ub90l815d0d&ou=451084",  # g&p
            "https://ufora.ugent.be/d2l/le/news/rss/443154/course?token=a0qvbudg77ub90l815d0d&ou=443154",  # r,e&m
            "https://ufora.ugent.be/d2l/le/news/rss/448634/course?token=a0qvbudg77ub90l815d0d&ou=448634",  # materiaal
            "https://ufora.ugent.be/d2l/le/news/rss/450490/course?token=a0qvbudg77ub90l815d0d&ou=450490",  # sterren
            "https://ufora.ugent.be/d2l/le/news/rss/450508/course?token=a0qvbudg77ub90l815d0d&ou=450508",  # thermische
            "https://ufora.ugent.be/d2l/le/news/rss/441064/course?token=a0qvbudg77ub90l815d0d&ou=441064",  # kwantum 1
            "https://ufora.ugent.be/d2l/le/news/rss/438282/course?token=a0qvbudg77ub90l815d0d&ou=438282",  # v&f ruimten
            "https://ufora.ugent.be/d2l/le/news/rss/451101/course?token=a0qvbudg77ub90l815d0d&ou=451101",  # statistiek
            "https://ufora.ugent.be/d2l/le/news/rss/445590/course?token=a0qvbudg77ub90l815d0d&ou=445590",  # python
        }
        self.second_year_channel_id = 807709321357819904

    @commands.Cog.listener()
    async def on_ready(self):
        # get channels
        self.first_year_channel = discord.utils.get(self.bot.get_all_channels(), id=self.first_year_channel_id)
        self.second_year_channel = discord.utils.get(self.bot.get_all_channels(), id=self.second_year_channel_id)

        # setup the feeds
        self.first_year_feeds = await self.setup_feeds(self.first_year_links)
        self.second_year_feeds = await self.setup_feeds(self.second_year_links)

        # setup tasks
        self.check_feeds.start()

    async def setup_feeds(self, linkslist: set):
        out = []
        for list in linkslist:
            temp = feedparser.parse(list)
            out.append([temp, list, [j.id for j in temp.entries]])

        return out

    @tasks.loop(minutes=5)
    async def check_feeds(self):
        for feed in self.first_year_feeds:  # todo this could be async using async for
            feed_update = feedparser.parse(feed[1])
            for j in feed_update.entries:
                if j.id not in feed[2]:
                    feed[0] = feed_update
                    feed[2].append(j.id)
                    await self.post(j, self.first_year_channel)

        for feed in self.first_year_feeds:
            feed_update = feedparser.parse(feed[1])
            for j in feed_update.entries:
                if j.id not in feed[2]:
                    feed[0] = feed_update
                    feed[2].append(j.id)
                    await self.post(j, self.second_year_channel)

    async def post(self, feed, channel):
        regex = re.compile('<.*?>')
        content = re.sub(regex, "", textwrap.wrap(feed.summary, width=300)[0])
        embed = discord.Embed(
            title=feed.title,
            description="\n" + content + "...",
            url=feed.link,
            color=1991880,
            footer={"text": feed.published}
        )

        await channel.send(embed=embed)
