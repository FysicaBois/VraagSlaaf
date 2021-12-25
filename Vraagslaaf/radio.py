import logging

from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.ext import tasks
from discord_slash import cog_ext
from discord_slash.context import InteractionContext
from discord_slash.utils.manage_commands import create_option, create_choice

Log = logging.getLogger(__name__)

stations = {"radio 1": "http://icecast.vrtcdn.be/radio1-high.mp3",
            "radio 2": "http://icecast.vrtcdn.be/ra2wvl-high.mp3",
            "klara": "http://icecast.vrtcdn.be/klara-high.mp3",
            "klara continuo": "http://icecast.vrtcdn.be/klaracontinuo-high.mp3",
            "studio brussel": "http://icecast.vrtcdn.be/stubru-high.mp3",
            "mnm": "http://icecast.vrtcdn.be/mnm-high.mp3",
            "qmusic": "https://20853.live.streamtheworld.com/QMUSIC.mp3"
            }


class Radio(commands.Cog):

    def __init__(self):
        self.player = None


    @commands.Cog.listener()
    async def on_ready(self):
        self.check_alone.start()
        Log.info("music bot is up, make sure to have ffmpeg on your path or this will not work!")

    @tasks.loop(seconds=10)
    async def check_alone(self):
        if self.player:
            if len(self.player.channel.voice_states) == 1:
                await self.player.disconnect()
                self.player = None

    @commands.command(name="radio")
    async def radio(self, ctx, *, arg: str):
        if self.player is not None:
            current_channel = self.player.channel
            await ctx.send(f"Sorry chief maar ik ben al aant het draaien in `{current_channel.name}`")
            return

        try:
            channel = ctx.message.author.voice.channel
        except AttributeError:
            await ctx.send("Je moet in een voice channel zitten om dit command te gebruiken")
            return

        if arg.startswith("http"): # link provided instead of stations
            try:
                url = arg
                self.player = await channel.connect()
                self.player.play(FFmpegPCMAudio(url))
                return
            except:
                await ctx.send("De link die je gegeven hebt werkt niet chief! (Links moeten beginnen met http en "
                               "eindigen op MP3")


        if arg.lower() in stations:
            url = stations[arg.lower()]
            self.player = await channel.connect()
            self.player.play(FFmpegPCMAudio(url))
            return


        await ctx.send(f"Ik herkende niet welke zender je wou chief, opties zijn: {', '.join(stations.keys())}, of een custom link <3")

    @cog_ext.cog_slash(name="radio",
                       description="Speelt een zender af ",
                       guild_ids=[790602506429923328,  # test server
                                  757496517065048124  # main server
                                  ],
                       options=[
                           create_option(
                               name="zender",
                               description="Zender.",
                               option_type=3,
                               required=True,
                               choices=[
                                    create_choice(name="Radio 1" , value="http://icecast.vrtcdn.be/radio1-high.mp3"),
                                    create_choice(name="Radio 2", value="http://icecast.vrtcdn.be/ra2wvl-high.mp3"),
                                    create_choice(name="Klara", value="http://icecast.vrtcdn.be/klara-high.mp3"),
                                    create_choice(name="Klara continuo", value="http://icecast.vrtcdn.be/klaracontinuo-high.mp3"),
                                    create_choice(name="Studio Brussel", value="http://icecast.vrtcdn.be/stubru-high.mp3"),
                                    create_choice(name="MNM", value="http://icecast.vrtcdn.be/mnm-high.mp3"),
                                   create_choice(name="QMusic", value="https://20853.live.streamtheworld.com/QMUSIC.mp3")
                                    ]),
                       ])
    async def _radio(self, ctx: InteractionContext, zender: str):
        if self.player is not None:
            current_channel = self.player.channel
            await ctx.send(f"Sorry chief maar ik ben al aant het draaien in `{current_channel.name}`")
            return

        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("Je moet in een voice channel zitten om dit commando te gebruiken!")
            return


        self.player = await channel.connect()
        self.player.play(FFmpegPCMAudio(zender))
        await ctx.send("Enjoy de beats chief :musical_note: ")
        return


    #@commands.command(name="stop")
    #@commands.has_role("management andy")
    async def stop(self, ctx):
        if self.player is not None:
            self.player.stop()
            await self.player.disconnect()
            self.player = None

