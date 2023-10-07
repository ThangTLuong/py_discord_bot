from typing import Any, Coroutine
from dotenv import dotenv_values as dv
import asyncio
import discord
import sys

from discord.ext import commands as cmd
from discord.app_commands import AppCommand
from discord.ext.commands import MissingPermissions

ENV = dv('.env')
TOKEN = ENV['DISCORD_TOKEN']

class Discord_Bot(cmd.Bot):
  def __init__(self) -> None:
    super().__init__(
      command_prefix=cmd.when_mentioned_or('>'),
      intents=discord.Intents().all(),
      help_command=None
    )
    
    self._cogs: list[str] = ['cogs.al_news', 'cogs.al_fanart', 'cogs.help']
  
  async def on_ready(self) -> None:
    print(f'Logged in as {self.user.name} ({self.user.id})')
    synced: Coroutine[Any, Any, list[AppCommand]] = await self.tree.sync()
    print('Slash CMDs Synced ' + str(len(synced)) + ' Commands')
    
  async def setup_hook(self) -> None:
    for ext in self._cogs:
      await self.load_extension(ext)
    
def main(args=None):
  bot = Discord_Bot()
  
  try:
    bot.run(TOKEN)
  except KeyboardInterrupt:
    print('Ctrl+C pressed. Exiting gracefully')

    al_news_cog = bot.get_cog('al_news')
    if al_news_cog:
      loop = asyncio.get_event_loop()
      twitter = loop.run_until_complete(al_news_cog.get_twitter())
      
      if twitter:
        loop.run_until_complete(twitter.quit())