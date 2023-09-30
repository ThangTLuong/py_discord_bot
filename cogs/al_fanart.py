from dotenv import dotenv_values as dv
import asyncio
import io

import discord
from discord import app_commands as ac
from discord.ext import commands as cmd, tasks

from functions import Pixiv, Time_Log

class Al_fanart(cmd.Cog):
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    self._ENV: dict[str, str | None] = dv('.env')
    self._time: Time_Log = Time_Log()
    
    self._pixiv: Pixiv = Pixiv()
    
  @cmd.Cog.listener()
  async def on_ready(self):
    await self._bot.wait_until_ready()
    
  @cmd.command(name='alart')
  async def al_art(self, ctx):
    await self._time.now()
    await self._pixiv.start()
    await self.send_image(ctx)
    await self._time.print_time('An AL fanart was sent.')
    
  async def send_image(self, ctx):
    image_data = io.BytesIO(await self._pixiv.get_image())
    await ctx.channel.send(file=discord.File(image_data, filename=await self._pixiv.get_name()))
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Al_fanart(bot))