import logging

from discord.ext.commands import Cog, Bot

from Vraagslaaf.comms import Comms


class VraagslaafCog(Cog):

    def __init__(self, bot: Bot, comms: Comms):
        self.bot = bot
        self.comms = comms

        bot.add_cog(self)
