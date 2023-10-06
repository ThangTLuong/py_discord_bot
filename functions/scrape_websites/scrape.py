from abc import ABC, abstractclassmethod
from typing import Dict, Tuple
from thefuzz import fuzz
from thefuzz import process
import random

from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs

class Scrape(ABC):
  def __init__(self) -> None:
    super().__init__()
  
  @abstractclassmethod
  async def start(self, tag: str | None = None) -> Tuple[str, bytes]:
    pass
  
  async def _get_website(self, session: ClientSession, url: str) -> bs:
    async with session.get(url) as response:
      return bs(await response.text(), 'html.parser')
    
  async def _random_post(self, number_of_elements: int) -> int:
    post = random.randint(0, (number_of_elements - 1))
    return post
  
  async def _random_rating_and_pages(self, ratings: Dict[str, int], tag: str | None = None) -> Tuple[str, int]:
    ratings: dict[str, int] = ratings.copy()
    list_of_ratings: list[str] = [key for key, value in ratings.items()]
    best_match: Tuple[str, int] | None = None
    
    # Possible ratings
    # {'safe': 155, 'questionable': 113, 'explicit': 58}
    # {'general': 273, 'questionable': 951, 'sensitive': 1000, 'explicit': 716}
    
    # Possible accepted tags
    # g: general, q: questionable, s: sensitive, e: explicit
    
    # If using konachan
    # g -> s, s -> q
    # general -> safe, sensitive -> questionable
    
    if tag and len(tag) > 1:
      best_match = process.extractOne(tag.lower(), list_of_ratings, scorer=fuzz.partial_ratio)
      if 'safe' in ratings:
        if best_match[1] >= 60 and best_match[0] == 'general':
          best_match = ['safe', 100]
          
        if best_match[1] >= 60 and best_match[0] == 'sensitive':
          best_match = ['questionable', 100]
    
    if tag and len(tag) == 1:
      if 'safe' in ratings:
        if tag == 'g':
          tag = 's'
          
        elif tag == 's':
          tag = 'q'
 
      first_letter_dictionary: dict[str, str] = {rating[0]: rating for rating in list_of_ratings}
      best_match = [first_letter_dictionary.get(tag), 100] if tag and tag in list(first_letter_dictionary.keys()) else None

    # Excludes the last element in the dictionary. Typically the 'Explicit' tag
    select_rating: str = best_match[0] if best_match and best_match[1] >= 60 else random.choice(list_of_ratings[:-1])
    rating: str = f'+rating%3A{select_rating}+'
    pages: int = random.randint(1, ratings.get(select_rating))

    return rating, pages
  
  async def _get_file_name(self, image_url: str) -> str:
    file_extension: str = image_url.split('.')[-1]
    file: str = image_url.split('/')[-1].replace(f'.{file_extension}', '')
    file_name: str = file + '.' + file_extension
    
    return file_name
  
  async def _get_image(self, session: ClientSession, image_url: str) -> bytes:
    async with session.get(image_url) as response:
      image = await response.read()
      
    return image