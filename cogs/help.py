import discord
from discord import ClientUser, User, app_commands as ac
from discord.ext import commands as cmd, tasks

from dotenv import dotenv_values as dv
from thefuzz import fuzz
from thefuzz import process

class Help(cmd.Cog):
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    self._ENV: dict[str, str | None] = dv('.env')
    self._commands: list[str] = [
      'alart', 'albomb'
    ]
    
    self._bot_user: ClientUser | None = None
    self._commander_user: User | None = None
    
  @cmd.Cog.listener()
  async def on_ready(self) -> None:
    await self._bot.wait_until_ready()
    self._bot_user = self._bot.user
    self._commander_user = self._bot.get_user(int(self._ENV['COMMANDER']))
    
  @cmd.command(name='help')
  async def help(self, ctx, *commands: str):
    if not commands:
      return

    for command in commands:
      embed = discord.Embed(title=f'This one\'s report for ***{command}***')
      
      embed.set_author(name=self._commander_user.name, url=self._commander_user.avatar, icon_url=self._commander_user.avatar)
      embed.set_thumbnail(url=self._bot_user.avatar)
      
      best_match = process.extractOne(command.lower(), self._commands, scorer=fuzz.partial_ratio)
      method = getattr(self, best_match[0], None) if best_match[1] >= 60 else None
      if callable(method):
        await method(ctx, embed.copy(), command)
        
  async def alart(self, ctx, embed: discord.Embed, command: str) -> None:
    embed.add_field(name=f'Command: **>{command}**', value=f'This one will send one Azur Lane fanart.', inline=False)
    embed.add_field(name=f'Arguments: **<rating>** *(Optional)*', 
                    value='The user is allowed specify the rating of the fanarts. \
                          By adding a rating to the command, it may take a few seconds longer for this one to send\
                          in the fanart with the specified rating.',
                    inline=False)
    embed.add_field(name=f'Ratings: **general; questionable; sensitive; explicit**',
                    value='This one believes that these ratings need no explanation. The user may use only the first\
                          letter of the rating.',
                    inline=False)
    embed.add_field(name=f'Example: ', value=f'```>{command}```\nor```>{command} g```', inline=False)
    embed.set_image(url='https://konachan.com/image/7943261e4406920986a4fb2a6b684bd4/Konachan.com%20-%20317174%20animal_ears%20anthropomorphism%20azur_lane%20blue_eyes%20breasts%20cleavage%20foxgirl%20gray_hair%20long_hair%20multiple_tails%20shinano_%28azur_lane%29%20signed%20tail%20wsman.jpg')
    
    await ctx.channel.send(embed=embed)
      
  async def albomb(self, ctx, embed: discord.Embed, command: str) -> None:
    embed.add_field(name=f'Command: **>{command}**', value=f'This one will send a cluster(5) Azur Lane fanarts.', inline=False)
    embed.add_field(name=f'Arguments: **<rating>** *(Optional)*', 
                    value='The user is allowed specify the rating of the fanarts. \
                          By adding a rating to the command, it may take a few seconds longer for this one to send\
                          in the fanart with the specified rating.',
                    inline=False)
    embed.add_field(name=f'Ratings: **general; questionable; sensitive; explicit**',
                    value='This one believes that these ratings need no explanation. The user may use only the first\
                          letter of the rating.',
                    inline=False)
    embed.add_field(name=f'Example: ', value=f'```>{command}```\nor```>{command} g```', inline=False)
    embed.set_image(url='https://konachan.com/image/7943261e4406920986a4fb2a6b684bd4/Konachan.com%20-%20317174%20animal_ears%20anthropomorphism%20azur_lane%20blue_eyes%20breasts%20cleavage%20foxgirl%20gray_hair%20long_hair%20multiple_tails%20shinano_%28azur_lane%29%20signed%20tail%20wsman.jpg')
    
    await ctx.channel.send(embed=embed)
    
async def setup(bot: cmd.Bot) -> None:
  await bot.add_cog(Help(bot))