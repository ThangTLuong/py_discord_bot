import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs
import random
import asyncio
from typing import Any
from thefuzz import fuzz
from thefuzz import process

import traceback
import sys

class Danbooru():
  def __init__(self) -> None:
    self._BASE_URL: str = 'https://danbooru.donmai.us'
    self._URL: str = 'https://danbooru.donmai.us/posts?page={}&tags=azur_lane{}'

  async def start(self, tag: str | None = None) -> tuple[str, bytes]:
    async with ClientSession() as session:
      image: bytes | None = None
      file_name: str | None = None
      post: int | None = None
      rating: str | None = None
      page: int | None = None
      url: str | None = None
      
      while True:
        try:
          rating, page = await self._random_rating_and_pages(tag)
          website: bs = await self._get_website(session, self._URL.format(page, rating))

          elements = website.find_all('a', class_='post-preview-link')
          post = await self._random_post(len(elements))
          url: str = self._BASE_URL + elements[post].get('href')

          website: bs = await self._get_website(session, url)
          image_url = website.find('img', id='image').get('src')

          break
        except Exception as e:
          exec_type, exc_obj, exc_tb = sys.exc_info()
          line_number = exc_tb.tb_lineno
          
          print(f"Exception occurred on line {line_number}: {e} | {url}")
          
          continue

      file_extension: str = image_url.split('.')[-1]
      file: str = image_url.split('/')[-1].replace(f'.{file_extension}', '')
      file_name: str = file + '.' + file_extension

      async with session.get(image_url) as response:
        image = await response.read()
      return file_name, image
    

  async def _get_website(self, session: ClientSession, url: str) -> bs:
    async with session.get(url) as response:
      return bs(await response.text(), 'html.parser')

  async def _random_post(self, number_of_elements: int) -> int:
    post = random.randint(0, (number_of_elements - 1))
    return post

  async def _random_rating_and_pages(self, tag: str | None = None) -> tuple[str, int]:
    ratings: dict[str, int] = {'general': 273, 'questionable': 951, 'sensitive': 1000, 'explicit': 716}
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
  
async def main(args=None):
  dan = Danbooru()
  await dan.start()

if __name__ == '__main__':
  asyncio.run(main())