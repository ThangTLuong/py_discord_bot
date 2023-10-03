from typing import Any, Coroutine
from dotenv import dotenv_values as dv
from collections import deque
import asyncio
import math
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
    
    self._explosive_rate: int = 0
    self._explosive_rate_limit: int = 30
    self._explosive_limit_reached: bool = False
    
    self._parsing_rate: int = 0
    self._parsing_rate_limit: int = 10
    self._recent_reset: bool = False
    self._second_storage_is_full: bool = False
    
    self._storages_are_full: bool = False
    
    self._danbooru: Danbooru = Danbooru()
    self._new_images: deque = deque()
    self._ready_images: deque = deque()
    self._lock = asyncio.Lock()
    
    self._condition: asyncio.Condition = asyncio.Condition()
    self._semaphore: asyncio.Semaphore = asyncio.Semaphore(1)
    
    self.replenishing_fanart.start()
    self.al_art_bomb_cooldown.start()
    self.storage_is_full.start()
    
  def cog_unload(self) -> Coroutine[Any, Any, None]:
    self.replenishing_fanart.stop()
    self.al_art_bomb_cooldown.stop()
    self.storage_is_full.stop()  
    
  @cmd.Cog.listener()
  async def on_ready(self) -> None:
    
    tasks: list[asyncio.Task] = []
    
    for _ in range(5):
      task = asyncio.create_task(self._danbooru.start())
      tasks.append(task)
      
    results = await asyncio.gather(*tasks)
    
    async with self._lock:
      # Get lock
      for file_name, image in results:
        if len(self._ready_images) >= 100:
          break
        
        self._ready_images.append((file_name, image))
      # Release lock
      
    await self._bot.wait_until_ready() 
    
  @tasks.loop(minutes=1.0)
  async def replenishing_fanart(self) -> None:
    if self._storages_are_full or self._second_storage_is_full:
      return
    
    if self._parsing_rate >= self._parsing_rate_limit:
      self.replenishing_fanart.change_interval(seconds=60.0)
      self._parsing_rate = 0
      self._recent_reset = True
      return
    
    if self._parsing_rate < self._parsing_rate_limit and self._recent_reset:
      self.replenishing_fanart.change_interval(seconds=30.0)
      self._recent_reset = False
    
    await self.parse_images(5)
    self._parsing_rate += 1
    
  @replenishing_fanart.before_loop
  async def before_replenishing_fanart(self) -> None:
    await self._bot.wait_until_ready()
    
  @tasks.loop(minutes=1.0)
  async def al_art_bomb_cooldown(self) -> None:
    if self._explosive_rate > 0:
      self._explosive_rate -= 1
      return
    
    self._explosive_limit_reached = False
    
  @al_art_bomb_cooldown.before_loop
  async def before_al_art_bomb_cooldown(self) -> None:
    await self._bot.wait_until_ready()
    await asyncio.sleep(30)
  
  @tasks.loop(minutes=5.0)
  async def storage_is_full(self) -> None:
    if self._storages_are_full:
      return
    
    async with self._lock:
      # Get lock
      if len(self._ready_images) >= 100 and len(self._new_images) >= 100:
        await self._time.now()
        await self._time.print_time('Both storage is full.')
        self._storages_are_full = True
        return
      # Release lock
    
    if self._second_storage_is_full and self._explosive_rate <= 0:
      await self._time.now()
      async with self._lock:
        # Get lock
        self._ready_images, self._new_images = self._new_images, self._ready_images
        # Release lock
      await self._time.print_time('No activity detected. Switching...')
      self._second_storage_is_full = False
  
  @storage_is_full.before_loop
  async def before_storage_is_full(self) -> None:
    await self._bot.wait_until_ready()
    await asyncio.sleep(300)
    
  @cmd.command(name='alart')
  async def al_art(self, ctx, tag: str | None = None) -> None:
    await self._time.now()
    
    if tag:
      await self.send_requested_image(ctx, 1, tag)
    else:
      await self.send_image(ctx, 1)
      
    await self._time.print_time('An AL fanart was sent.')

  @cmd.command(name='albomb')
  async def al_art_bomb(self, ctx, tag: str | None = None) -> None:
    await self._time.now()
    if self._explosive_rate >= self._explosive_rate_limit:
      await self._time.print_time('The limit for the command \'>albomb\' has been reached.')
      self._explosive_limit_reached = True
      return
    
    if self._explosive_limit_reached:
      await self._time.print_time(f'\'>albomb\' limit reached. Current rate: {self._explosive_rate}')
      embed = discord.Embed()
      embed.add_field(name='', value=f'I\'m sorry. This one must take a breather. Will be back in {math.floor(self._explosive_rate)} min...')
      embed.set_image(url='https://img-9gag-fun.9cache.com/photo/aR7qQZQ_460s.jpg')
      await ctx.channel.send(embed=embed)
      return
    
    async with self._lock:
      # Get lock
      self._explosive_rate += 1
      # Release lock
    
    if tag:
      await self.send_requested_image(ctx, 5, tag)
    else:
      await self.send_image(ctx, 5)
      
    await self._time.print_time('An AL bomb of fanart was launched.')
    
  async def send_image(self, ctx, number_of_loops: int) -> None:
    tasks: list[asyncio.Task] = []
    files: list[discord.File] = []

    async with self._condition:
      await self._condition.wait_for(lambda: len(self._ready_images) >= number_of_loops)
    
    async with self._lock:
      # Get lock
      for _ in range(number_of_loops):
        file_name, image = self._ready_images.popleft()
        task = asyncio.create_task(self.process_image(file_name, image))
        tasks.append(task)
      # Release lock
    self._storages_are_full = False  
    async with self._lock:
      if len(self._ready_images) < number_of_loops:
        print(f'There are {len(self._ready_images)} images left in self._ready_images. Switching...')
        self._ready_images, self._new_images = self._new_images, self._ready_images
        self._second_storage_is_full = False
      else:
        print(f'There are {len(self._ready_images)} images left in self._ready_images.')
      
    results = await asyncio.gather(*tasks)
    
    for file_name, image in results:
      file = discord.File(image, filename=file_name)
      files.append(file)
      
    await ctx.channel.send(files=files)
    
  async def send_requested_image(self, ctx, number_of_loops: int, tag: str) -> None:
    tasks: list[asyncio.Task] = []
    files: list[discord.File] = []
    
    for _ in range(number_of_loops):
      task = asyncio.create_task(self.fetch_and_process_image(tag))
      tasks.append(task)
      
    results = await asyncio.gather(*tasks)
    
    for file_name, image in results:
      file = discord.File(image, filename=file_name)
      files.append(file)
      
    await ctx.channel.send(files=files)
    
  async def parse_images(self, limit: int = 0) -> None:
    images_to_get: int

    async with self._lock:
      images_to_get = min(100 - len(self._new_images), limit if limit else 10)
    
    # Returns in new_images is full
    if images_to_get <= 0:
      self._second_storage_is_full = True
      return
    
    self._second_storage_is_full = False
    
    tasks: list[asyncio.Task] = []

    for _ in range(images_to_get):
      task = asyncio.create_task(self._danbooru.start())
      tasks.append(task)
      
    results = await asyncio.gather(*tasks)
    
    async with self._lock:
      # Get lock
      for file_name, image in results:
        if len(self._new_images) >= 100:
          break
        
        self._new_images.append((file_name, image))
      # Release lock
  
  async def fetch_and_process_image(self, tag: str | None = None) -> tuple[str, BytesIO]:
    file_name, image = await self._danbooru.start(tag)
    return await self.process_image(file_name, image)
      
  async def process_image(self, file_name: str, image: bytes) -> tuple[str, BytesIO]:
    return file_name, BytesIO(image)
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Al_fanart(bot))