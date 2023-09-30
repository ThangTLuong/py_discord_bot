from asyncio import sleep
from typing import Any, Coroutine
from dotenv import dotenv_values as dv
from datetime import datetime
import random
import pytz

import discord
from discord import app_commands as ac
from discord.ext import commands as cmd, tasks

from functions import Twitter

class Al_news(cmd.Cog):
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    self._ENV: dict[str, str | None] = dv('.env')
    self._timezone = pytz.timezone('America/Los_Angeles')
    
    self._twitter: Twitter = Twitter('JP_AZUR_LANE')
    
    self.al_updates.start()
    
  def cog_unload(self) -> Coroutine[Any, Any, None]:
    self.al_updates.cancel()
  
  # @ac.command(name='al', description='Sends Azur Lane updates.')
  # async def al_news(self, interaction: discord.Interaction):
  #   for tweet in self._twitter.get_urls():
  #     await interaction.response.send_message(content=tweet)
  #     await sleep(5)
  
  @cmd.Cog.listener()
  async def on_ready(self):
    await self._bot.wait_until_ready()
      
  @tasks.loop(minutes = 15.0)
  async def al_updates(self):
    timenow = datetime.now(self._timezone).strftime("%m/%d/%Y %H:%M:%S %Z%z")
    next_timer: int = random.randint(15, 60)
    
    if await self._twitter.start():
      await self.send_tweets(int(self._ENV['JP_AL_CHANNEL']))
      print(f'[{timenow}]: New Azur Lane tweet(s) posted. The next scan will be in {next_timer} minutes')
    else:
      print(f'[{timenow}]: No new Azur Lane tweet detected. The next scan will be in {next_timer} minutes')
      
    self.al_updates.change_interval(minutes = float(next_timer))
    
  @al_updates.before_loop
  async def before_al_updates(self):
    await self._bot.wait_until_ready()
    
  async def send_tweets(self, channel_id: int):
    channel = self._bot.get_channel(channel_id)
    
    for tweet in self._twitter.get_urls():
      await channel.send(content=f'{self._ENV["JP_AL_ROLE"]}\n\n{tweet}')
      await sleep(5)
  
  async def get_twitter(self) -> Twitter:
    return self._twitter  
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Al_news(bot))