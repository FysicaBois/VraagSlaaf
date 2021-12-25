import asyncio
import inspect
import logging
import os
from asyncio import Queue
from collections.abc import Callable
from typing import List, Awaitable

import websockets
from discord.ext import commands, tasks

Log = logging.getLogger(__name__)


class Comms(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue: Queue = None
        self.leeseners: List = list()

        environment = os.environ.get("ENVIRONMENT")
        if environment == "DEV":
            self.uri = "ws://localhost:5000/ws"
            # self.uri = "wss://vraagslaaf.be/ws"
        elif environment == "PROD":
            self.uri = "wss://vraagslaaf.be/ws"  # fyi in prod the websocket connection gets automatically upgraded to wss
            # using nginx, but we can just assume in the code that we are handling with an unencrypted socket.

    @commands.Cog.listener()
    async def on_ready(self):
        # connect to the server
        self.debug_print_leeseners.start()
        self.connect.start()

    @tasks.loop(seconds=10)
    async def debug_print_leeseners(self):
        Log.debug(self.leeseners)

    @tasks.loop(count=1)
    async def connect(self):
        async def server_logic():
            async with websockets.connect(self.uri) as websocket:
                Log.info("Websocket connected")
                self.queue = asyncio.Queue()
                await asyncio.gather(
                    self._send_message(websocket),
                    self._receive_message(websocket)
                )

        await server_logic()

    async def _send_message(self, websocket):
        while True:
            data = await self.queue.get()
            await websocket.send(data)
            Log.debug("Sent data")

    async def _receive_message(self, websocket):
        while True:
            data = await websocket.recv()
            event, message = data.split("💩")
            for leesener in self.leeseners:
                # call all listeners that don't have specific events
                if leesener.event == event or leesener.event == "message":
                    await leesener.call(message)  # todo this should probably be in parallel over all listeners

    async def send(self, event, message):
        """
        Sends a message to the webserver.

        @param event: event HAS to be provided. (use "message" event if sending a general message).
        @param message: String or bytes
        """
        Log.debug(f"trying {event}-{message} in the queue")
        await self.queue.put(event + "💩" + message)
        Log.debug(f"put {event}-{message} in the queue")

    async def receive(self, event=None) -> str:
        """
        Blocks the thread until a receival of a message from the webserver

        @param event: Event to listen to. By default, listens to all messages (on_message)
        @return: the message sent from the server.
        """

    @commands.command(name="send")
    async def send_command(self, ctx):
        text = str(ctx.message.content)
        await self.queue.put("message💩" + text)


class Leesener():
    """
    A Leeseneer is a object that can listen for messages (events) that the webserver sends to the bot.
    By preference the Comms.leesener decorator should be used in favor of instantiating this class.
    """

    def __init__(self, comms: Comms, func: Callable[[str], Awaitable], event: str = None, add=True):
        """
        Creates a listener. By default automatically active.
        @param comms: Comms object.
        @param func: async callback function
        @param event: event to listen to. Defaults to all messages.
        @param add: If the listener becomes active on instantiation. If not, the activate() method has to be called.
        """

        Log.debug("A new leesener init was made")
        self.comms = comms
        self.func = func
        self.event = event or "message"

        if add:
            self.comms.leeseners.append(self)

    async def call(self, message):
        await self.func(message)

    async def activate(self):
        self.comms.leeseners.append(self)

    async def dispose(self):
        self.comms.leeseners.remove(self)


def leesener(f: object, comms: object = None, event: object = None) -> object:
    """
    Leesener decorator that makes it easy to add leeseners to Cogs and other objects.

    @param f: function
    @param comms: Comms object to add Leesener to. When in a VraagslaafCog environment,
     automatically gets the correct comms, so no need to provide it in the arguments.
    @param event: event to listen to. If none provided, defaults to the function's name without "on_". So the function
    name "on_login" would listen to "login" events
    @return: f wrapped
    """

    Log.debug("Maybe this should be called in here?")
    def wrapper(*args): # the function arguments
        print("tester")
        if not comms and not args[0]:
            Log.error(
                "When not using the leesener decorator inside a VraagslaafCog environment, a comms object has to be "
                "provided")
            raise AttributeError("Comms object has to be provided")

        if not comms and not args[0].comms:
            Log.error(
                "When not using the leesener decorator inside a VraagslaafCog environment, a comms object has to be "
                "provided")
            raise TypeError("Comms object has to be provided")

        if not event and not f.__name__.startswith("on_"):
            Log.warning("No event provided and function name doesn't start with *on_* for leesener function; "
                        "defaulting to listening to all events.")

        com = comms or args[0].comms
        ev = event or f.__name__.substring(3)

        actual = f
        if isinstance(actual, staticmethod):
            actual = actual.__func__
        if not inspect.iscoroutinefunction(actual):
            raise TypeError('Listener function must be a coroutine function.')

        Leesener(com, actual, ev)
        return f

    return wrapper
