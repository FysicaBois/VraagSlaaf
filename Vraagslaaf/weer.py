import logging

import aiofiles
import aiohttp
import discord
from PIL import Image
from discord.ext import commands
from discord.ext.commands import Cog

Log = logging.getLogger()


class Weer(Cog):

    def __init__(self):

        self.width = 550
        self.height = 512
        self.amount = 12
        self.link = f"https://image.buienradar.nl/2.0/image/sprite/RadarMapRainBE?extension=png&width={self.width}&height={self.height}" \
                    f"&renderText=False&renderBranding=False&renderBackground=True&history=0&forecast={self.amount}&skip=0"

    @Cog.listener()
    async def on_ready(self):
        # await self.download_image()
        Log.info("Weer Cog ready")

    @commands.command()
    async def buien(self, ctx):
        filename = await self.download_image()
        gifname = await self.create_gif(filename)
        await ctx.send(file=discord.File(gifname))

    async def download_image(self):
        # i know this is a oneliner with requests, but async :heart_eyes: and I don't know if requests supports redirects
        async with aiohttp.ClientSession() as session:
            url = self.link
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open('tempweer.png', mode='wb+')
                    await f.write(await resp.read())
                    await f.close()
                    return 'tempweer.png'
                else:
                    Log.error("Couldnt downlaod image", resp.status)

    async def create_gif(self, filename):
        # todo IO blocking image events should run in asyncio.run_in_executor
        im = Image.open(filename)
        w, h = im.size
        unit = w // self.amount
        images = []
        for n in range(self.amount):
            images.append(im.crop((unit * n, 0, unit * (n + 1), h)))

        images[0].save('tempweer.gif',
                       save_all=True, append_images=images[1:], optimize=False, duration=400, loop=0)
        return 'tempweer.gif'
