from dotenv import dotenv_values as dv
from collections import deque
import asyncio
from io import BytesIO

import discord
from discord import app_commands as ac
from discord.ext import commands as cmd, tasks

from functions import Danbooru, Time_Log

class Al_fanart(cmd.Cog):
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    self._ENV: dict[str, str | None] = dv('.env')
    self._time: Time_Log = Time_Log()
    
    self._danbooru: Danbooru = Danbooru()
    self._list_of_images: deque = deque()
    self._lock = asyncio.Lock()
    
  @cmd.Cog.listener()
  async def on_ready(self):
    await self._bot.wait_until_ready()
    
    await self._time.now()
    await self._time.print_time('Initializing AL fanarts...')
    
    tasks: list[asyncio.Task] = []
    
    for _ in range(10):
      task = asyncio.create_task(self._danbooru.start())
      tasks.append(task)
      
    results = await asyncio.gather(*tasks)
    
    async with self._lock:
      # Get lock  
      for file_name, image in results:
        self._list_of_images.append((file_name, image))
      # Release lock
      
    await self._time.now()
    await self._time.print_time('AL fanarts initialization complete.')
    
  @cmd.command(name='alart')
  async def al_art(self, ctx):
    await self._time.now()
    await self.send_image(ctx, 1)
    await self._time.print_time('An AL fanart was sent.')
    
    async with self._lock:
      # Get lock
      file_name, image = await self._danbooru.start()
      self._list_of_images.append((file_name, image))
      # Release lock
      
  @cmd.command(name='albomb')
  async def al_art_bomb(self, ctx):
    await self._time.now()
    await self.send_image(ctx, 5)
    await self._time.print_time('An AL bomb of fanart was launched.')
    
    tasks: list[asyncio.Task] = []
    for _ in range(5):
      task = asyncio.create_task(self._danbooru.start())
      tasks.append(task)
        
    results = await asyncio.gather(*tasks)
    
    async with self._lock:
      # Get lock
      for file_name, image in results:
        self._list_of_images.append((file_name, image))
      # Release lock
    
  async def send_image(self, ctx, number_of_loops: int):
    tasks: list[asyncio.Task] = []
    files: list[discord.File] = []
    
    async with self._lock:
      # Get lock
      for _ in range(number_of_loops):
        file_name, image = self._list_of_images.popleft()
        task = asyncio.create_task(self.process_image(file_name, image))
        tasks.append(task)
      # Release lock
      
    results = await asyncio.gather(*tasks)
    
    for file_name, image in results:
      file = discord.File(image, filename=file_name)
      files.append(file)
      
    await ctx.channel.send(files=files)
      
  async def process_image(self, file_name: str, image: bytes) -> tuple[str, BytesIO]:
    return file_name, BytesIO(image)
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Al_fanart(bot))