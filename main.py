import os

import dotenv
import discord
from discord.ext import commands

from utility.logging import init_logging
from utility.config import config

log = init_logging("INFO")

class Bot(discord.Bot):
    def __init__(self, *args, **kwargs):
        self.log = log
        super().__init__(*args, **kwargs)

    def add_cog(self, cog: discord.Cog, *, override=False):
        log.info(f"load cog {cog.__class__.__name__} class in the {cog.__module__}")
        super().add_cog(cog, override=override)
    
    async def on_ready(self):
        log.info("機器人版本: v 1.0")
        log.info(f"登入身分: {bot.user} ({bot.user.id})")
        log.info(">>> BOT IS RUNNING <<<")

    @discord.Cog.listener()
    async def on_command_error(ctx: commands.Context, error):
        log.error(f"[例外][{ctx.author.id}]on_command_error: {error}")

intents = discord.Intents.all()
bot = Bot(intents=intents)

if isinstance(loads := bot.load_extension("cogs", recursive=True), dict):
    for key, error in dict.items(loads):
        if isinstance(error, Exception):
            log.error(f"load cog error {error}")

bot.run(config.bot_token)
