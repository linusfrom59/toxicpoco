import os
import random
import sys
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
load_dotenv(project_root / '.env')

from database.db import init_db, link_discord_account

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "1482089357165854891"))
PANEL_CHANNEL_ID = int(os.getenv("PANEL_CHANNEL_ID", "1491183745904939080"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://deine-domain.de")

welcome_messages = [
    "Welcome to Toxic! Ready to brawl and dominate the arena? 💀🔥",
    "A new brawler has joined Toxic! Let’s climb trophies together! 🏆",
    "Welcome to Toxic Club! Time to show your Brawl Stars skills! 🎮",
    "Another fighter enters Toxic! Let the chaos begin! ⚡",
    "Welcome to Toxic! Stay toxic, play smart, and win big! 💥",
    "A new challenger appears in Toxic! Ready for battle? 🔫",
    "Welcome to Toxic Club! Let’s push trophies and destroy enemies! 🏆🔥",
    "Toxic just got stronger! Welcome and let’s brawl! 💀",
    "Welcome to Toxic! May your aim be sharp and your wins legendary! 🎯",
    "A new legend joins Toxic! Let’s dominate Brawl Stars together! 👑"
]


class WebsitePanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Zum Web-Formular",
                style=discord.ButtonStyle.link,
                url=WEBSITE_URL,
                emoji="🌐",
            )
        )


@bot.event
async def on_ready():
    init_db()
    bot.add_view(WebsitePanelView())
    print(f"Bot is online as {bot.user}")


@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"{member.mention} {random.choice(welcome_messages)}")


@bot.command(name="link")
async def link(ctx: commands.Context, link_code: str):
    success = link_discord_account(link_code.strip().upper(), ctx.author.id)

    if success:
        await ctx.reply(
            "Dein Website-Formular wurde erfolgreich mit deinem Discord-Account verbunden. ✅",
            mention_author=False,
        )
    else:
        await ctx.reply(
            "Link-Code ungültig oder schon verwendet. Bitte prüfe den Code von der Website.",
            mention_author=False,
        )


@bot.command(name="panel")
@commands.has_permissions(administrator=True)
async def panel(ctx: commands.Context):
    panel_channel = bot.get_channel(PANEL_CHANNEL_ID)
    if panel_channel is None:
        await ctx.reply("Panel-Kanal nicht gefunden.", mention_author=False)
        return

    embed = discord.Embed(
        title="Bewerbung / Verifizierung",
        description=(
            "Klicke auf den Button, um das Web-Formular zu öffnen.\n\n"
            "Dort trägst du deine Daten ein und bekommst danach deinen Link-Code für `!link CODE`."
        ),
    )
    await panel_channel.send(embed=embed, view=WebsitePanelView())
    await ctx.reply("Panel wurde gesendet. ✅", mention_author=False)


@panel.error
async def panel_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("Dafür brauchst du Administrator-Rechte.", mention_author=False)
        return
    raise error


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN fehlt in der .env")
    bot.run(DISCORD_TOKEN)
