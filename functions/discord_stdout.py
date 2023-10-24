import asyncio
from io import BytesIO
from typing import Any, List, Union
import discord
from discord import Colour, Embed, File
from discord.ext import commands as cmd
from discord.ext.commands import Context

class Discord_Stdout():
  def __init__(self, bot: cmd.Bot) -> None:
    self._bot: cmd.Bot = bot
    
  async def send_message(self, **kwargs) -> None:
    if 'ctx' not in kwargs and 'id' not in kwargs:
      raise ValueError('Either \'ctx\' or \'id\' must be provided.')
    
    channel = None
    if 'id' in kwargs and kwargs['id'].isdigit():
      channel = self._bot.get_channel(int(kwargs.pop('id')))
      kwargs.pop('ctx', None)
    else:
      channel = kwargs.pop('ctx')
    
    await channel.send(**kwargs)
  
  async def set_embed_properties(self, **kwargs) -> Embed:
    embed: Embed = kwargs.get('embed', Embed())
    
    if 'colour' in kwargs or 'color' in kwargs:
      embed.colour = kwargs.get('colour', kwargs.get('color'))
      
    embed.title = kwargs.get('title')
    embed.url = kwargs.get('url')
    embed.description = kwargs.get('description')
    
    return embed

  async def set_embed(self, **kwargs) -> Embed:
    '''
    The order of operation: Removal -> Insert
    1st: embed
    
    2nd: remove_author, remove_fields, remove_footer, clear_fields
    
    3rd: add_fields, insert_fields_at, set_author, set_fields_at, set_footer, set_image, set_thumbnail
    
    Parameter
    ---------------
    add_fields - A list of [name, value, inline].
    
    clear_fields - True/False. Remove all the fields.
    
    insert_fields_at - A list of [index, name, value, inline].
    
    remove_author - True/False. Clear the author property.
    
    remove_fields - A list of indices/field that should be removed.
    
    remove_footer - True/False. Remove the footer.
    
    set_author - [name, url, icon_url]. Set the author property.
    
    set_fields_at - A list of [index, name, value, inline]. Modify existing fields.
    
    set_footer - [text, icon_url]. Set the Footer property.
    
    set_image - URL. Set the image of the embed.
    
    set_thumbnail - URL. Set the thumbnail of the embed.
    
    Return
    ---------------
    Embed - `discord.Embed`
    '''
    
    embed: Embed = kwargs.get('embed', Embed())

    if kwargs.get('remove_author', False):
      embed.remove_author()
    
    remove_fields = kwargs.get('remove_fields', None)
    if remove_fields:
      for index in remove_fields:
        embed.remove_field(index)

    if kwargs.get('remove_footer', False):
      embed.remove_footer()

    if kwargs.get('clear_fields', False):
      embed.clear_fields()

    add_fields = kwargs.get('add_fields', None)
    if add_fields:
      for field in add_fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    insert_fields_at = kwargs.get('insert_fields_at', None)
    if insert_fields_at:
      for field in insert_fields_at:
        embed.insert_field_at(index=field[0], name=field[1], value=field[2], inline=field[3])

    set_author = kwargs.get('set_author', None)
    if set_author:
      embed.set_author(name=set_author[0], url=set_author[1], icon_url=set_author[2])

    set_fields_at = kwargs.get('set_fields_at', None)
    if set_fields_at:
      for field in set_fields_at:
        embed.set_field_at(index=field[0], name=field[1], value=field[2], inline=field[3])

    set_footer = kwargs.get('set_footer', None)
    if set_footer:
      embed.set_footer(text=set_footer[0], icon_url=set_footer[1])

    if kwargs.get('set_image'):
      embed.set_image(url=kwargs['set_image'])

    if kwargs.get('set_thumbnail'):
      embed.set_thumbnail(url=kwargs['set_thumbnail'])

    return embed
  
  async def send_file(self, ctx: Context, file: dict[str, BytesIO] | None = None, id: (int | str | None) = None) -> None:
    if not (ctx or id):
      raise ValueError('Either \'ctx\' or \'id\' must be provided.')
    
    bundles: list[dict[str, BytesIO]] = []
    bundle: dict[str, BytesIO] = {}
    tasks: list[asyncio.Task] = []
    
    channel = None
    try:
      channel = self._bot.get_channel(int(id)) if id and id.isdigit() else None
    except ValueError as e:
      raise ValueError(f'{e}')

    for i, (key, value) in enumerate(file):
      bundle[key] = value
      
      if (i + 1) % 10 == 0:
        bundles.append(bundle.copy())
        bundle.clear()
        
    if bundle:
      bundles.append(bundle.copy())

    for bundle in bundles:
      task = asyncio.create_task(self._bundle_files(ctx, bundle, channel))
      tasks.append(task)
      
    await asyncio.gather(*tasks)
      
  async def _bundle_files(self, ctx: Context, file: dict[str, BytesIO], channel = None):
    list_of_files: list[discord.File] = []

    for file_name, image in file.items():
      file = discord.File(image, filename=file_name)
      list_of_files.append(file)
      
    
    if len(list_of_files) > 1:
      await channel.send(files=list_of_files) if channel else await ctx.send(files=list_of_files)
    else:
      await channel.send(file=list_of_files[0]) if channel else await ctx.send(file=list_of_files[0])