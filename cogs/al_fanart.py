from typing import Any, Coroutine
from dotenv import dotenv_values as dv
from collections import deque
import asyncio
import math
from PIL import Image, ImageDraw, ImageFont
from time import perf_counter
import requests 
from io import BytesIO

import discord
from discord import app_commands as ac
from discord.ext import commands as cmd, tasks

from functions import Danbooru, Time_Log, Discord_Stdout

class Al_fanart(cmd.Cog):
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    self._ENV: dict[str, str | None] = dv('.env')
    self._time: Time_Log = Time_Log()
    self._out: Discord_Stdout = Discord_Stdout(self._bot)
    
    self._danbooru: Danbooru = Danbooru()
    
  def cog_unload(self) -> Coroutine[Any, Any, None]:
    pass
    
  @cmd.Cog.listener()
  async def on_ready(self) -> None:
    await self._bot.wait_until_ready() 

  @cmd.command(name='alart')
  async def al_art(self, ctx, tag: str | None = None) -> None:
    await self._time.now()

    results = await self.parse_image(1, tag)
    await self._out.send_file(ctx, results)

    await self._time.print_time('An AL fanart was sent.')

  @cmd.command(name='albomb')
  async def al_art_bomb(self, ctx, tag: str | None = None) -> None:
    await self._time.now()

    results = await self.parse_image(5, tag)
    await self._out.send_file(ctx, results)

    await self._time.print_time('An AL bomb of fanart was launched.')
  
  async def parse_image(self, number_of_files: int, tag: str | None = None) -> dict[str, BytesIO]:
    tasks: list[asyncio.Task] = []
    
    for _ in range(number_of_files):
      task = asyncio.create_task(self.fetch_and_process_image(tag))
      tasks.append(task)
      
    results: dict[str, BytesIO] = await asyncio.gather(*tasks)
    
    return results
    
  async def fetch_and_process_image(self, tag: str | None = None) -> dict[str, BytesIO]:
    file_name, image = await self._danbooru.start(tag)
    return await self.process_image(file_name, image)
      
  async def process_image(self, file_name: str, image: bytes) -> tuple[str, BytesIO]:
    return file_name, BytesIO(image)
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Al_fanart(bot))