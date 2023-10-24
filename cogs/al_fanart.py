import random
from typing import Any, Coroutine, List, Tuple
from dotenv import dotenv_values as dv
import asyncio
import math
from time import perf_counter
import requests 
from io import BytesIO

import discord
from discord import app_commands as ac
from discord.ext import commands as cmd, tasks
from discord.ext.commands import Context

from functions import Scrape, Danbooru, Konachan, Time_Log, Discord_Stdout

class Al_fanart(cmd.Cog):
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    self._ENV: dict[str, str | None] = dv('.env')
    
    self._lock: asyncio.Lock = asyncio.Lock()
    
    self._fanart_rate: float = 0.0
    self._fanart_rate_limit: float = 30.0
    self._fanart_limit_reached: bool = False
    
    self._time: Time_Log = Time_Log()
    self._out: Discord_Stdout = Discord_Stdout(self._bot)

    self._scrape_websites: List = [Danbooru(), Konachan()]
    
  def cog_unload(self) -> Coroutine[Any, Any, None]:
    self.resting.cancel()
    
  @cmd.Cog.listener()
  async def on_ready(self) -> None:
    await self._bot.wait_until_ready()
    self.resting.start()

  @tasks.loop(minutes=1.0)
  async def resting(self):
    async with self._lock:
      # Get Lock
      if self._fanart_rate > 1:
        self._fanart_rate -= 1
      else:
        self._fanart_rate = 0
        self._fanart_limit_reached = False

  @cmd.command(name='alart')
  async def al_art(self, ctx: Context, tag: str | None = None) -> None:
    await self._time.now()
    if await self.is_exhausted(ctx, 0.2):
      return

    results = await self.parse_image(1, tag)
    await self._out.send_file(ctx, results)

    await self._time.print_time('An AL fanart was sent.')

  @cmd.command(name='albomb')
  async def al_art_bomb(self, ctx: Context, tag: str | None = None) -> None:
    await self._time.now()
    if await self.is_exhausted(ctx, 1.0):
      return

    results = await self.parse_image(5, tag)
    await self._out.send_file(ctx, results)

    await self._time.print_time('An AL bomb of fanart was launched.')   
  
  @cmd.command(name='alstrike')
  async def al_art_airstrike(self, ctx: Context, tag: str | None = None):
    await self._time.now()
    if await self.is_exhausted(ctx, 10.0):
      return
    
    results = await self.parse_image(30, tag)
    await self._out.send_file(ctx, results)
    
    await self._time.print_time('An AL air strike of fanart was launched.')
  
  async def parse_image(self, number_of_files: int, tag: str | None = None) -> dict[str, BytesIO]:
    tasks: list[asyncio.Task] = []
    
    for _ in range(number_of_files):
      task = asyncio.create_task(self.fetch_and_process_image(tag))
      tasks.append(task)
      await asyncio.sleep(0.001)
      
    results: dict[str, BytesIO] = await asyncio.gather(*tasks)
    
    return results
    
  async def fetch_and_process_image(self, tag: str | None = None) -> dict[str, BytesIO]:
    website: Scrape = random.choice(self._scrape_websites)
    file_name, image = await website.start(tag)
    return await self.process_image(file_name, image)
      
  async def process_image(self, file_name: str, image: bytes) -> Tuple[str, BytesIO]:
    return file_name, BytesIO(image)
  
  async def is_exhausted(self, ctx, rate: float) -> bool:
    if not self._fanart_limit_reached and self._fanart_rate < self._fanart_rate_limit:
      async with self._lock:
        # Get Lock
        self._fanart_rate += rate
        # Release Lock
      return False
    
    await self._time.now()
    await self._time.print_time(f'I\'m sorry. This one must take a breather. Will be back in {math.floor(self._fanart_rate)} min...')
    
    embed = await self._out.set_embed(
      add_fields=[['', f'I\'m sorry. This one must take a breather. Will be back in {math.floor(self._fanart_rate)} min...', False]],
      set_image='https://img-9gag-fun.9cache.com/photo/aR7qQZQ_460s.jpg')

    await self._out.send_message(ctx=ctx, embed=embed)
    
    self._fanart_limit_reached = True
    return True
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Al_fanart(bot))