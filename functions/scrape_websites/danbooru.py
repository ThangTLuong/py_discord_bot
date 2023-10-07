from typing import Dict, Tuple
from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs
import asyncio

import sys

from .scrape import Scrape

class Danbooru(Scrape):
  def __init__(self) -> None:
    self._BASE_URL: str = 'https://danbooru.donmai.us'
    self._URL: str = 'https://danbooru.donmai.us/posts?page={}&tags=azur_lane{}'

    self._RATINGS: Dict[str, int] = {'general': 273, 'questionable': 951, 'sensitive': 1000, 'explicit': 716}

  async def start(self, tag: str | None = None) -> Tuple[str, bytes]:
    async with ClientSession() as session:
      image: bytes | None = None
      file_name: str | None = None
      url: str | None = None
      image_url: str | None = None
      
      while True:
        try:
          rating, page = await self._random_rating_and_pages(self._RATINGS, tag)
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
      
      file_name = await self._get_file_name(image_url)
      image = await self._get_image(session, image_url)
      
      return file_name, image
  
async def main(args=None):
  dan = Danbooru()
  await dan.start()

if __name__ == '__main__':
  asyncio.run(main())