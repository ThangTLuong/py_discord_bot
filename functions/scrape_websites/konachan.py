import asyncio
import sys
from typing import Dict, Tuple

from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs

from .scrape import Scrape

class Konachan(Scrape):
  def __init__(self) -> None:
    self._URL: str = 'https://konachan.com/post?page={}&tags=azur_lane{}'
    
    self._RATINGS: Dict[str, int] = {'safe': 155, 'questionable': 113, 'explicit': 58}
  
  async def start(self, tag: str | None = None) -> Tuple[str, bytes]:
    async with ClientSession() as session:
      image: bytes | None = None
      file_name: str | None = None
      image_url: str | None = None
      
      while True:
        try:
          rating, page = await self._random_rating_and_pages(self._RATINGS, tag)
          website: bs = await self._get_website(session, self._URL.format(page, rating))
          
          elements = website.find_all('a', class_ = 'directlink largeimg')
          post = await self._random_post(len(elements))
          image_url = elements[post].get('href')
          
          break

        except Exception as e:
          exec_type, exc_obj, exc_tb = sys.exc_info()
          line_number = exc_tb.tb_lineno
          
          print(f"Exception occurred on line {line_number}: {e} | {self._URL.format(page, rating)} | {len(elements)}")
          
          continue
          
      file_name = await self._get_file_name(image_url)
      image = await self._get_image(session, image_url)
      
      return file_name, image
    
async def main(args=None):
  kon = Konachan()
  await kon.start()
  
if __name__ == '__main__':
  asyncio.run(main())