import discord
from discord import app_commands as ac
from discord.ext import commands as cmd

from functions import Twitter

class Al_news(cmd.Cog):
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    
    self._twitter: Twitter = Twitter()
    self._twitter.start()
  
  @ac.command(name='al', description='Sends Azur Lane updates.')
  async def al_news(self, interaction: discord.Interaction):
    await interaction.response.send_message(content=self._twitter.get_url())
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Al_news(bot))