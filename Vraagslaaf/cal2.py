"""
Async implementation of the calendar stuff i had previously
"""
# read client and user creds
import json
import logging
from datetime import date, timedelta, datetime, time
from typing import Union

import discord
from discord.ext import commands, tasks
from discord_slash import cog_ext
from discord_slash.context import InteractionContext
from discord_slash.utils.manage_commands import create_option, create_choice

Log = logging.getLogger(__name__)

from aiogoogle import Aiogoogle
from discord.ext.commands import Cog, Context


class Cal2(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.first_year_calendar_id = "6gfsokdo2qvegsq1bvc9q1vh4c@group.calendar.google.com"
        self.first_year_channel_id = 886578235452817438
        self.second_year_calendar_id = "ukdb7bc41o10be4si33ib5g3rs@group.calendar.google.com"
        self.second_year_channel_id = 811263526005506048
        self.time_to_send_daily_message = time(hour=5, minute=30)
        self.interval = 10  # If you change this interval, also change the parameter in the tasks.loop decorator below.

    @Cog.listener()
    async def on_ready(self):
        with open("Vraagslaaf/env/client_creds.json") as client_creds_file:
            self.client_creds = json.load(client_creds_file)

        with open("Vraagslaaf/env/user_creds.json") as user_creds_file:
            self.user_creds = json.load(user_creds_file)

        self.second_year_channel = discord.utils.get(self.bot.get_all_channels(), id=self.second_year_channel_id)
        self.first_year_channel = discord.utils.get(self.bot.get_all_channels(), id=self.first_year_channel_id)

        self.print_in_the_mornings.start()

        Log.info("Cal2 Cog loaded")

    @tasks.loop(minutes=10)
    async def print_in_the_mornings(self):
        timelower = (datetime.combine(date.today(), self.time_to_send_daily_message) - timedelta(
            minutes=self.interval / 2)).time()
        timehigher = (datetime.combine(date.today(), self.time_to_send_daily_message) + timedelta(
            minutes=self.interval / 2)).time()
        if timelower < datetime.now().time() < timehigher:
            await self.kalender(self.second_year_channel, year="2")
            await self.kalender(self.first_year_channel, year="1")

    def get_str_rep_of_day(self, date: date):
        if date == date.today():
            return "Vandaag"
        elif date == date.today() + timedelta(days=1):
            return "Morgen"
        else:
            return date.__str__()

    async def fetch_events(self, calendar_id, start_date: date, duration: timedelta):
        async with Aiogoogle(client_creds=self.client_creds, user_creds=self.user_creds) as aiogoogle:
            calendar_v3 = await aiogoogle.discover('calendar', 'v3')

            startdt = datetime.combine(start_date, datetime.min.time())
            start_string = startdt.isoformat() + "Z"  # to interface with the google calendar api, you need a Z at the end

            enddt = (startdt + duration)
            end_string = enddt.isoformat() + "Z"

            response = await aiogoogle.as_user(
                calendar_v3.events.list(calendarId=calendar_id,
                                        singleEvents=True,
                                        orderBy="startTime",
                                        timeMin=start_string,
                                        timeMax=end_string
                                        )
            )

            data = response
            all_events = data.get("items", [])

            # group events by day
            by_day = dict()
            for event in all_events:
                startdate = datetime.fromisoformat(event['start']['dateTime']).date()
                by_day.get(startdate, list()).append(event)

            print(all_events)
            print(by_day)
            message = ""

            # add a title
            for day, events in by_day.items():
                message += f'**{self.get_str_rep_of_day(day)}**\n'

                # color id 1 is lavendel
                schoolge = [x for x in events if x.get("colorId", "0") == "1"]
                other = [x for x in events if not x.get("colorId", "0") == "1"]

                if len(other) == 0 and len(schoolge) == 0:
                    message += "*geen evenementen vandaag*\n"
                    return message

                if len(schoolge) > 0:
                    message += "    :bookmark: *__UGent-gerelateerd__*\n"

                for event in schoolge:
                    start_time = datetime.fromisoformat(event['start']['dateTime']).time()
                    end_time = datetime.fromisoformat(event['end']['dateTime']).time()
                    summary = event['summary']

                    message += f'       :arrow_forward: {start_time} tot {end_time} : {summary}\n\n'

                if len(other) > 0:
                    message += "    :game_die: *__Varia__*\n"

                for event in other:
                    start_time = datetime.fromisoformat(event['start']['dateTime']).time()
                    end_time = datetime.fromisoformat(event['end']['dateTime']).time()
                    summary = event['summary']

                    message += f':arrow_forward: {start_time} tot {end_time} : {summary}\n\n'

            return message

    @commands.command(name="kalender")
    async def kalender(self, ctx: Union[discord.TextChannel, Context], year="2", duur="vandaag"):  #
        if year == "1":
            aid = self.first_year_calendar_id
        elif year == "2":
            aid = self.second_year_calendar_id
        else:
            await ctx.send("Ik begreep niet welke kalender je wou chief, gebruik 'slaaf kalender 1' voor Bachelor 1 en " \
                           "'slaaf kalender 2' voor Bachelor 2 ")
            return

        if duur == "vandaag":
            st = date.today()
            td = timedelta(days=1)
        elif duur == "morgen":
            st = date.today() + timedelta(days=1)
            td = timedelta(days=1)
        elif duur == "week":
            st = date.today()
            days = 6 - date.today().weekday()
            td = timedelta(days=days)
        elif duur == "volgendeweek":
            vandaag = date.today().weekday()
            st = date.today() + timedelta(7 - vandaag)  # volgende maandag
            td = timedelta(days=7)
        else:
            await ctx.send("Ik begreep niet welke tijdsduratie je wou chief")
            return

        await ctx.send(embed=discord.Embed(description=await self.fetch_events(aid, st, td)))

    @commands.command(name="morgen")
    async def morgen(self, ctx, year="2"):
        await self.kalender(ctx, year, "morgen")

    @commands.command(name="vandaag")
    async def vandaag(self, ctx, year="2"):
        await self.kalender(ctx, year, "vandaag")

    @commands.command(name="week")
    async def week(self, ctx, year="2"):
        await self.kalender(ctx, year, "week")

    @cog_ext.cog_slash(name="kalender",
                       description="Geeft de kalender weer voor vandaag.",
                       guild_ids=[790602506429923328,  # test server
                                  757496517065048124  # main server
                                  ],
                       options=[
                           create_option(
                               name="jaar",
                               description="Kalender opvragen van een specifiek jaar",
                               option_type=3,
                               required=False,
                               choices=[
                                   create_choice(name="Bachelor 1", value="1"),
                                   create_choice(name="Bachelor 2", value="2"),
                               ]),
                           create_option(
                               name="duur",
                               description="Voor welke dag(en) de kalender moet opgehaald worden.",
                               option_type=3,
                               required=False,
                               choices=[
                                   create_choice(name="Vandaag", value="vandaag"),
                                   create_choice(name="De week", value="week"),
                                   create_choice(name="Morgen", value="morgen"),
                                   create_choice(name="Volgende Week", value="volgendeweek")
                               ]),
                       ]
                       )
    async def _kalender(self, ctx: InteractionContext, jaar="2", duur="vandaag"):
        await self.kalender(ctx, jaar, duur)
