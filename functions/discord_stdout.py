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
    self._condition: asyncio.Condition = asyncio.Condition()
  
  async def send_message(self, ctx: Context, message: str, id: (int | str | None) = None) -> None:
    if not (ctx or id):
      raise ValueError('Either \'ctx\' or \'id\' must be provided.')
    
    channel = None
    try:
      channel = self._bot.get_channel(int(id)) if id and id.isdigit() else None
    except ValueError as e:
      raise ValueError(f'{e}')
    
    await channel.send(content=message) if channel else await ctx.send(content=message)
  
  async def set_embed_properties(self,
                      colour: int | Colour | None = None,
                      color: int | Colour | None = None,
                      title: Any | None = None,
                      url: Any | None = None,
                      description: Any | None = None,
                      embed: Embed | None = None 
                      ) -> Embed:
    embed = embed if embed else Embed()
    embed.colour = colour if colour else color
    embed.title = title
    embed.url = url
    embed.description = description
    
    return embed
  
  async def set_embed(self,
                      add_fields: List[List[Union[Any, bool]]] | None = None,
                      clear_fields: bool = False,
                      insert_fields_at: List[List[Union[int, Any, bool]]] | None = None,
                      remove_author: bool = False,
                      remove_fields: List[int] | None = None,
                      remove_footer: bool = False,
                      set_author: List[Any] | None = None,
                      set_fields_at: List[List[Union[int, Any, bool]]] | None = None,
                      set_footer: List[Any] | None = None,
                      set_image: Any | None = None,
                      set_thumbnail: Any | None = None,
                      embed: Embed | None = None
                      ) -> Embed:
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
    
    # Add safe guard
    
    embed = embed if embed else Embed()
    if remove_author: embed.remove_author()
    
    if remove_fields:
      for index in remove_fields:
        embed.remove_field(index)
      
    if remove_footer: embed.remove_footer()
      
    if clear_fields: embed.clear_fields()
    
    if add_fields:
      for list_of_fields in add_fields:
        embed.add_field(name=list_of_fields[0], 
                        value=list_of_fields[1], 
                        inline=list_of_fields[2])
    
    if insert_fields_at:
      for list_of_insert in insert_fields_at:
        embed.insert_field_at(index=list_of_insert[0], 
                              name=list_of_insert[1], 
                              value=list_of_insert[2], 
                              inline=list_of_insert[3])
    
    if set_author: embed.set_author(name=set_author[0], url=set_author[1], icon_url=set_author[2])
    
    if set_fields_at:
      for list_of_set in set_fields_at:
        embed.set_field_at(index=list_of_set[0], name=list_of_set[1], value=list_of_set[2], inline=list_of_set[3])

    if set_footer: embed.set_footer(text=set_footer[0], icon_url=set_footer[1])
      
    if set_image: embed.set_image(url=set_image)
      
    if set_thumbnail: embed.set_thumbnail(url=set_thumbnail)

    return embed
  
  async def send_embed(self, ctx: Context, embed: Embed, id: (int | str | None) = None) -> None:
    if not (ctx or id):
      raise ValueError('Either \'ctx\' or \'id\' must be provided.')
    
    channel = None
    try:
      channel = self._bot.get_channel(int(id)) if id and id.isdigit() else None
    except ValueError as e:
      raise ValueError(f'{e}')
    
    await channel.send(embed=embed) if channel else await ctx.send(embed=embed)
  
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