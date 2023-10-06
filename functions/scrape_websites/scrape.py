from abc import ABC, abstractclassmethod
from typing import Dict
from thefuzz import fuzz
from thefuzz import process
import random

from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs

class Scrape(ABC):
  def __init__(self) -> None:
    super().__init__()
  
  @abstractclassmethod
  async def start(self, tag: str | None = None) -> tuple[str, bytes]:
    pass
  
  async def _get_website(self, session: ClientSession, url: str) -> bs:
    async with session.get(url) as response:
      return bs(await response.text(), 'html.parser')
    
  async def _random_post(self, number_of_elements: int) -> int:
    post = random.randint(0, (number_of_elements - 1))
    return post
  
  async def _random_rating_and_pages(self, ratings: Dict[str, int], tag: str | None = None) -> tuple[str, int]:
    ratings: dict[str, int] = ratings.copy()
    list_of_ratings: list[str] = [key for key, value in ratings.items()]
    best_match: tuple[str, int] | None = None

    if tag and len(tag) == 1:
      first_letter_dictionary: dict[str, str] = {rating[0]: rating for rating in list_of_ratings}
      best_match = [first_letter_dictionary.get(tag), 100] if tag and tag in list(first_letter_dictionary.keys()) else None
    else:
      best_match = process.extractOne(tag.lower(), list_of_ratings, scorer=fuzz.partial_ratio) if tag else None

    # Excludes 'explicit' if tag is not given
    select_rating: str = best_match[0] if best_match and best_match[1] >= 60 else list_of_ratings[random.randint(0, len(ratings)-2)]
    rating: str = f'+rating%3A{select_rating}+'
    pages: int = random.randint(1, ratings.get(select_rating))
    
    return rating, pages