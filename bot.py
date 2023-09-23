from dotenv import dotenv_values
import discord

from discord.ext import commands as cmd
from discord.ext.commands import MissingPermissions

class Discord_Bot():
  intents = discord.Intents.default()
  intents.message_content = True
  intents.members = True
  client = discord.Client(intents=intents)
  
  def __init__(self) -> None:
    self._env = dotenv_values('.env')
    self._TOKEN = self._env['DISCORD_TOKEN']
    
  def start(self) -> None:
    self.client.run(self._TOKEN)
    
  @client.event
  async def on_ready():
    print('Bot is ready')
    
def main(args=None):
  bot = Discord_Bot()
  bot.start()
  