from discord.ext.commands import Bot

from Vraagslaaf import comms
from Vraagslaaf.cogs.VraagslaafCog import VraagslaafCog
from Vraagslaaf.comms import Comms


class TestCog(VraagslaafCog):

    def __init__(self, bot: Bot, comms: Comms):
        super().__init__(bot, comms)
