from __future__ import print_function
import datetime

from discord.ext import commands
from discord.ext.commands import Cog
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os

import logging

Log = logging.getLogger(__name__)

class Calendar(commands.Cog):

    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/calendar.readonly"]

    @Cog.listener()
    async def on_ready(self):
        Log.info("Calendar cog ready.")
        await self.login_service()



    async def login_service(self):
        creds = None

        if os.path.exists('Vraagslaaf/env/calendar_token.json'):
            creds = Credentials.from_authorized_user_file(
                "Vraagslaaf/env/calendar_token.json", scopes=self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request()) # todo can this be aysnc?
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'Vraagslaaf/env/client_secret.json', scopes=self.scopes)
                creds = flow.run_local_server(port=6969)
                # Save the credentials for the next run
            with open('Vraagslaaf/env/calendar_token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)
        return service


    def dag_str(self, date: datetime.date):
        if date == datetime.date.today():
            return "Vandaag"
        elif date == datetime.date.today() + datetime.timedelta(days=1):
            return "Morgen"
        else:
            return date.__str__()


    def oneday(self, date):
        service = self.login_service()
        id = "kp6u8g1ges324ptifto6krr6vk@group.calendar.google.com"
        # get all events for today
        nowdt = datetime.datetime.combine(date, datetime.datetime.min.time())
        now = nowdt.isoformat() + "Z"
        one_day_from_now = (nowdt + datetime.timedelta(days=1)).isoformat() + "Z"

        events_result = service.events().list(calendarId=id, singleEvents=True,
                                              orderBy='startTime', timeMax=one_day_from_now, timeMin=now).execute()
        events = events_result.get('items', [])

        title = f'**{self.dag_str(date)}**\n'
        out = ""
        # color id 1 is lavendel
        schoolge = [x for x in events if x.get("colorId", "0") == "1"]
        other = [x for x in events if not x.get("colorId", "0") == "1"]

        if len(other) == 0 and len(schoolge) == 0:
            out += "*geen evenementen vandaag*\n"
            return title, out

        if len(schoolge) > 0:
            out += "    :bookmark: *__UGent-gerelateerd__*\n"

        for event in schoolge:
            start_time = datetime.datetime.fromisoformat(event['start']['dateTime']).time()
            end_time = datetime.datetime.fromisoformat(event['end']['dateTime']).time()
            summary = event['summary']
            if 'location' in event:
                if event['location'].startswith("http"):
                    link = event['location']
                    out += f'       :arrow_forward: {start_time} tot {end_time} : [{summary}]({link})\n\n'

            else:
                out += f'       :arrow_forward: {start_time} tot {end_time} : {summary}\n\n'
        if len(other) > 0:
            out += "    :game_die: *__Varia__*\n"
        for event in other:
            start_time = datetime.datetime.fromisoformat(event['start']['dateTime']).time()
            end_time = datetime.datetime.fromisoformat(event['end']['dateTime']).time()
            summary = event['summary']
            if 'location' in event:
                if event['location'].startswith("http"):
                    link = event['location']
                    out += f'       :arrow_forward: {start_time} tot {end_time} : [{summary}]({link})\n\n'

            else:
                out += f'       :arrow_forward: {start_time} tot {end_time} : {summary}\n\n'

        return title, out


    def week(self, dat: datetime.date):
        dates = [dat + datetime.timedelta(days=i) for i in range(0 - dat.weekday(), 7 - dat.weekday())]
        out = ""
        for date in dates:
            out += ((self.oneday(date)[1]) + "\n")
        return "weekplanning", out
