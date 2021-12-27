# Gemaakt door Anton Leagre (https://github.com/aap007freak)

# Lock code vriendelijk geïnspireerd en/of gestolen van https://github.com/renevds/DisLocker/blob/main/locker.py
import os
import random
from threading import Thread

import fitz
import requests
import urllib.parse
import datetime
import asyncio
import time

from discord.ext.commands import Bot
from discord_slash import SlashCommand

import json

from Vraagslaaf.cal2 import Cal2
from Vraagslaaf.cogs.testcog import TestCog
from Vraagslaaf.comms import Comms
from Vraagslaaf.lock import Lockdown
from Vraagslaaf.music import Music
from Vraagslaaf.radio import Radio
from Vraagslaaf.opl import Oplossing
from Vraagslaaf.casino import Casino
from discord_components import DiscordComponents

from Vraagslaaf.study import Study
from Vraagslaaf.studyroom import StudyRoom
from Vraagslaaf.ufora import Ufora
from Vraagslaaf.verify import Verify
from Vraagslaaf.wolfram import WolframAlpha


import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv

import logging


# load secrets into environment variables
from Vraagslaaf.wolfram import WolframAlpha

load_dotenv(dotenv_path="Vraagslaaf/env/.env")

environment = os.environ.get("ENVIRONMENT")
if environment == "DEV":
    logging.basicConfig(level=logging.DEBUG)
    bot = commands.Bot(command_prefix=["slaf ", "Slaf "])

elif environment == "PROD":
    logging.basicConfig(level=logging.WARNING)
    bot = commands.Bot(command_prefix=["slaaf ", "Slaaf "])

Log = logging.getLogger("Vraagslaaf.main")


if environment == "PROD":
    slash = SlashCommand(bot, sync_commands=True) # Declares slash commands through the client.

bot.remove_command('help')  # we will create our own help command later on

bot.add_cog(Radio())
# casino_cog = Casino(bot)
# bot.add_cog(casino_cog)
bot.add_cog(Oplossing())

comms = Comms(bot)
bot.add_cog(comms)

verify_cog = Verify(bot, comms)
bot.add_cog(verify_cog)

wolfram = WolframAlpha()
bot.add_cog(wolfram)

lockdown = Lockdown(bot)
bot.add_cog(lockdown)

cal2 = Cal2(bot)
bot.add_cog(cal2)

studyroom = StudyRoom(bot)
bot.add_cog(studyroom)

ufora = Ufora(bot, comms)

stat = Study(bot)
bot.add_cog(stat)

testCog = TestCog(bot, comms)

@bot.event
async def on_ready():
    DiscordComponents(bot)
    Log.info(bot.cogs)
    Log.info('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="jullie vragen"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if message.guild in lockdown.locking_guilds:
        await message.delete()
        lockdown.log += str(message.author) + "\n\n" + message.content + "\n------------\n"


# ----------------------------------------------BEGIN COMMANDS----------------------------------------------------------
# ----------------------------------------------PING--------------------------------------------------------------------
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send('Pong!')

# ----------------------------------------------VRAAG (MECH)------------------------------------------------------------

def readVragen():
    with open("Vraagslaaf/vragen.txt", "r") as file:
        return file.read().split("$$")


vragen = readVragen()


@bot.command(name="vraag")
async def vraag(ctx):
    vraag = random.choice(vragen)

    # handle fotos
    fotos = [x[2:len(x) - 1] for x in vraag.split("\n") if x.startswith("<!")]
    await ctx.send("".join(line for line in vraag.split("\n") if not line.startswith("<!")))
    for foto in fotos:
        await ctx.send(file=discord.File(f'Vraagslaaf/images/{foto}'))


def writeVraag(string):
    with open("Vraagslaaf/vragen.txt", "a") as file:  # a voor append
        file.write("\n$$\n")
        file.write(string)


@bot.command(name="add")
async def add(ctx, *, arg):
    vragen.append(arg)  # we don't check for swearwords and such, you can't add images
    writeVraag(arg)

    await ctx.send("Je vraag zit erin chief")


@bot.command(name="hoeveel", help="printdit")
async def hoeveel(ctx):
    await ctx.send(f'er zitten nu {len(vragen)} in chief!')


@bot.command(name="dump")
async def dump(ctx):
    await ctx.send(file=discord.File("Vraagslaaf/vragen.txt"))


# vragen voor theo
@bot.command(name="theo")
async def theo(ctx):
    await ctx.send(file=discord.File("Vraagslaaf/saved/" + random.choice(os.listdir("Vraagslaaf/saved/"))))


# ----------------------------------------------HELP--------------------------------------------------------------------

@bot.command(name="help")
async def help(ctx):
    await ctx.send(
        """
        Hallo chief! Ik ben de vraagslaaf :blush: . Hieronder kan je een paar veel gebruikte commando's zien.
:heavy_check_mark: `slaaf wa <text>`: 
    Port de mn buddies van Wolframalpha :robot:  om te kijken of zij een antwoord (soms met stappen) hebben op jouw vraagstuk; bijvoorbeeld *slaaf wa integral sin 2x*
:heavy_check_mark: `slaaf wm <text>`: 
    Doet hetzelfde as het vorige commando, maar met meer details **dit kan een hele chat volspammen!** *slaaf wm integral sin 2x*
:heavy_check_mark: `slaaf opl <HS>.<Vraag>`: 
    geeft een screen uit de oplossingenbundel van Giancoli 1/2 met desbetreffende oplossing; bijvoorbeeld *slaaf opl 9.50*
:heavy_check_mark: `slaaf dag`: 
    print een dagplanning.
:heavy_check_mark: `slaaf week`: 
    print een weekplanning. (weekplanningen komen pas in het weekend online; het is een manueel proces)
:heavy_check_mark: `slaaf play <zender>`: 
    de slaaf zal je voice channel joinen en de desbetreffende radio zender afspelen. 
     (de meeste radio zenders zitten erin); bijvoorbeeld *slaaf play radio 2* 
     Een custom radio-feed afspelen is ook mogelijk, je kan bijvoorbeeld doen *slaaf play http://icecast.vrtcdn.be/mnm-high.mp3*; zorg ervoor 
     dat je link begint in "http" en eindigt in "mp3" (of een ander muziekformaat).
:heavy_check_mark: `slaaf ping`: 
    pingt me om te kijken of ik nog leef.
:heavy_check_mark: `slaaf help`
    geeft deze handige lijst
----------------------------- Minder gebruikte of deprecated commando's ------------------------------------
:heavy_check_mark: `slaaf vraag`: 
    ik geef je een random vraag mech uit de lijst.
:heavy_check_mark: `slaaf add <text>`: 
    steekt een nieuwe vraag mech in de lijst; bijvoorbeeld *slaaf add hoeveel euro kost je moeder per nacht?*

Deze commando's werken ook in Private messages, als je liever privé converseert. (Niet bang zijn, ik bijt niet, behalve als je dat wilt uwu)
        """
    )
# ----------------------------------------------KALENDER----------------------------------------------------------------
# this involves google calendar and authentication, so is abstracted to another file
# @bot.command(name="vandaag")

"""
async def vandaag(ctx):
    tod = datetime.date.today()
    titl, mess = cal.oneday(tod)
    await ctx.send(embed=discord.Embed(title=titl, description=mess))


# @bot.command(name="morgen")
async def morgen(ctx):
    tod = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
    titl, mess = cal.oneday(tod)
    await ctx.send(embed=discord.Embed(title=titl, description=mess))


# @bot.command(name="week")
async def week(ctx):
    tod = datetime.date.today()
    titl, mess = cal.week(tod)
    Log.debug(mess)
    await ctx.send(embed=discord.Embed(title=titl, description=mess))


# @bot.command(name="volgendeweek")
async def volgende_week(ctx):
    tod = (datetime.datetime.now() + datetime.timedelta(days=7)).date()
    titl, mess = cal.week(tod)
    await ctx.send(embed=discord.Embed(title=titl, description=mess))


# utc time, TODO: this should be fixable to CET/CEST
timetosend = datetime.time(hour=5, minute=30)
interval = 10


@tasks.loop(minutes=interval)
async def print_in_the_mornings():
    timelower = (datetime.datetime.combine(datetime.date.today(), timetosend) - datetime.timedelta(
        minutes=interval / 2)).time()
    timehigher = (datetime.datetime.combine(datetime.date.today(), timetosend) + datetime.timedelta(
        minutes=interval / 2)).time()
    if timelower < datetime.datetime.now().time() < timehigher:
        await bot.wait_until_ready()  # make sure the bot is up (shouldn't be neccesary honestly)
        channel = bot.get_channel(811263526005506048)  # TODO: hardcoded IDs
        tod = datetime.date.today()
        titl, mess = cal.oneday(tod)
        await channel.send(embed=discord.Embed(title=titl, description=mess))


# print_in_the_mornings.start()
"""


# ----------------------------------------------SVEN GELUIDJES----------------------------------------------------------

geluidjes_dir = "Vraagslaaf/sg/"


@bot.command(name="sv")
async def svengeluidje(ctx):
    fil = random.choice(os.listdir(geluidjes_dir))  # change dir name to whatever

    await ctx.send(file=discord.File(geluidjes_dir + fil))


# ----------------------------------------------END COMMANDS------------------------------------------------------------


TOKEN = os.environ.get("BOT_SECRET")
bot.run(TOKEN)
