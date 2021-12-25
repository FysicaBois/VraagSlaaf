import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import discord
from discord.ext import tasks
from discord.ext.commands import Cog, command
from discord_components import DiscordComponents, Button, InteractionType, ButtonStyle

import logging

from Vraagslaaf import comms
from Vraagslaaf.comms import Comms, Leesener


Log = logging.getLogger(__name__)

class Verify(Cog):

    def __init__(self, bot, comms):
        self.bot = bot
        self.verify_channel_id = 859538363237007390
        self.guild_id = 757496517065048124
        self.verified_role_id = 859760521292152852
        self.mod_role_id = 757570945299775540
        self.comms = comms

        with open("Vraagslaaf/database.json", "r") as databasefile:
            if databasefile.read(1):
                databasefile.seek(0)
                self.verify_database = json.load(databasefile)
            else:
                self.verify_database = dict(
                    {"started": list(), "pending": list(), "approved": list(), "blacklist": list()})

    @Cog.listener()
    async def on_ready(self):
        self.verify_channel = discord.utils.get(self.bot.get_all_channels(), id=self.verify_channel_id)
        self.guild = self.bot.get_guild(self.guild_id)
        self.verified_role = discord.utils.get(self.guild.roles, id=self.verified_role_id)
        self.mod_role = discord.utils.get(self.guild.roles, id=self.mod_role_id)

        self.update_database_file.start()

        Log.info("verify cog ready")

        async def on_verify(message):
            data: dict = json.loads(message)
            memb = await self.guild.fetch_member(data["id"])
            await memb.add_roles(self.verified_role)
            # add user to role given
            self.verify_database["approved"].append(data)
            self.verify_database["pending"].remove(data)
            self.verify_database["started"].remove(data["id"])

        self.comms.leeseners.append(Leesener(self.comms, on_verify, "verify"))

    @tasks.loop(seconds=10)
    async def update_database_file(self):
        with open("Vraagslaaf/database.json", "w") as databasefile:
            databasefile.write(json.dumps(self.verify_database))

    @command()
    async def drop(self, ctx):
        await ctx.send(
            "klik op onderstaande knop om geverifieerd te worden!",
            components=[
                Button(style=ButtonStyle.blue, label="Verifieer mij!")
            ])

    async def email_procedure(self, user):
        await user.send("""** Het automatische verificatieproces**

:one:  Stuur hieronder je __UGent Emailadres__ naar de bot (vermijd spaties voor of na het emailadres).

:two:  De mods controleren je emailadres, dit kan even duren (om te vermijden dat men expres personeelemails instuurt).

:three:  Als de mods je email goed bevinden, krijg je een verificatiemail. Daarin klik je op de verificatielink.

:four:  Je zou dan toegang moeten krijgen tot alle kanalen. Veel plezier!

*N.B.  in verband met privacy*: je emailadres wordt versleuteld opgeslagen en zal alleen gebruikt worden voor
identificatie. We zullen nooit mails sturen naar je Ugent emailadres.""")
        message = await self.bot.wait_for('message',
                                          check=lambda message: message.author == user and isinstance(message.channel,
                                                                                                      discord.DMChannel))
        email_adres = message.content
        await self.send_email_address_to_mods(user, email_adres)

    async def send_email_address_to_mods(self, user, email):
        await self.verify_channel.send(
            #f"{self.mod_role.mention}\n"
            f"Een gebruiker: {user} probeert te verifieren met emailadres {email}\n"
            f"Als je toelaat, dan wordt een mail gestuurd naar de gebruiker om zich te verifiëren.\n"
            f"Als je negeert, dan wordt de gebruiker op een blacklist gezet en kan hij/zij "
            f"zich niet meer automatisch verifiëren.\n"
            f"Als de interactie mislukt, dan heeft een andere mod al op de knop gedrukt.",
            components=[
                [
                    Button(style=ButtonStyle.green, label="Toelaten"),
                    Button(style=ButtonStyle.red, label="Negeren"),
                ],
            ])

        interaction = await self.bot.wait_for("button_click", check=lambda i: (i.component.label.startswith(
            "Toelaten") or i.component.label.startswith("Negeren") )and email in  i.message.content)

        if interaction.component.label.startswith("Toelaten"):
            self.verify_database["pending"].append({"id": user.id, "email": email})
            await user.send(":information_source: De mods hebben je mail goed bevonden, kijk in je email voor een "
                            "bevestigingsmail!")
            await interaction.respond(type=InteractionType.ChannelMessageWithSource,
                                      content=":white_check_mark: De gebruiker krijgt binnenkort de "
                                              "bevestigingsmail in "
                                              "z'n inbox chief.")
            await self.send_email(user.id, email)

        elif interaction.component.label.startswith("Negeren"):
            self.verify_database["blacklist"].append({"id": id, "email": email})
            self.verify_database["started"].remove(user.id)

            await user.send(":x: Je bent op de blacklist gezet! Je zal niet meer kunnen verifiëren")
            await interaction.respond(type=InteractionType.ChannelMessageWithSource,
                                      content=":white_check_mark: De gebruiker wordt uit "
                                              "alle rijksarchieven gebrand!")

    async def send_email(self, id, email_adress):
        hashstring = (str(id) + "%" + email_adress).encode("utf-8").hex()
        Log.debug(hashstring)

        url = f"https://vraagslaaf.be/verify/{hashstring}"

        gmail_password = os.environ.get("VRAAGSLAAF_GOOGLE_PASSWORD")
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login("vraagslaaf@gmail.com", gmail_password)

        msg = MIMEMultipart()  # create a message

        # add in the actual person name to the message template
        message = f"Hallo daar!\n" \
                  f"Klik op deze link om je verificatie te voltooien: {url}\n\n" \
                  f"Veel plezier! De VraagSlaaf"

        # setup the parameters of the message
        msg['From'] = "vraagslaaf@gmail.com"
        msg['To'] = email_adress
        msg['Subject'] = "Verificatie Fysica Discord Server"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        s.send_message(msg)

    @Cog.listener()
    async def on_button_click(self, res):
        """
        Possible interaction types:
        - Pong
        - ChannelMessageWithSource
        - DeferredChannelMessageWithSource
        - DeferredUpdateMessage
        - UpdateMessage
        """
        if res.component.label == "Verifieer mij!":
            if res.user.id in [entries["id"] for entries in
                               self.verify_database["pending"]]:  # the first element of an entry is its id
                await res.respond(type=InteractionType.ChannelMessageWithSource,
                                  content=f":x: Er is al een aanmeldingspoging gedaan, dus je kan geen nieuwe "
                                          f"opstarten. \n "
                                          f"Stuur een berichtje aan een admin ({self.mod_role.mention}) om verder "
                                          f"geholpen te worden.")
            elif res.user.id in [entries["id"] for entries in self.verify_database["blacklist"]]:
                await res.respond(type=InteractionType.ChannelMessageWithSource,
                                  content=f":x: Je kan geen verifieerpoging meer doen omdat je op de blacklist staat! \n"
                                          f"Stuur een berichtje aan een admin ({self.mod_role.mention}) om verder "
                                          f"geholpen te worden.")
            elif res.user.id in [entries["id"] for entries in self.verify_database["approved"]]:
                await res.respond(type=InteractionType.ChannelMessageWithSource,
                                  content=f":question: Je kan geen verifieerpoging meer doen omdat je al geverifieerd "
                                          f"bent! \n "
                                          f"Stuur een berichtje aan een admin ({self.mod_role.mention}) om verder "
                                          f"geholpen te worden.")
            elif res.user.id in [entries for entries in self.verify_database["started"]]:
                await res.respond(type=InteractionType.ChannelMessageWithSource,
                                  content=f":question: Je kan geen verifieerpoging meer doen omdat je al bezig bent met  een verifieerpoging!"
                                          f"Stuur een berichtje aan een admin ({self.mod_role.mention}) om verder "
                                          f"geholpen te worden.")
            else:  # this nested if else is necessary because you can't have async statements in if predicates as far
                # as i am aware, which is a shame
                memb = await self.guild.fetch_member(res.user.id)
                member_roles = memb.roles
                if self.verified_role in member_roles:
                    await res.respond(type=InteractionType.ChannelMessageWithSource,
                                      content=f":question: Je kan geen verifieerpoging meer doen omdat je al geverifieerd "
                                              f"bent! \n "
                                              f"Stuur een berichtje aan een admin ({self.mod_role.mention}) om verder geholpen te worden.")
                else:
                    await res.respond(type=InteractionType.ChannelMessageWithSource,
                                      content=":information_source: Verifieerprocedure opgestart, check je private messages om verder te gaan.")
                    self.verify_database["started"].append(res.user.id)
                    await self.email_procedure(res.user)
