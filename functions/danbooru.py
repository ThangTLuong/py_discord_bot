from typing import Any
from bs4 import BeautifulSoup as bs
import requests
from requests import Response
import random
import asyncio

from thefuzz import fuzz
from thefuzz import process

class Danbooru():
  def __init__(self) -> None:
    self._BASE_URL: str = 'https://danbooru.donmai.us'
    self._URL: str = 'https://danbooru.donmai.us/posts?page={}&tags=azur_lane{}'
    self._first_page, self._last_page = 1, 999
    
    self._image: bytes | None = None
    self._file_name: str | None = None
    
  async def start(self, tag: str | None = None) -> tuple[str, bytes]:
    while True:
      try:
        page = await self._random_page()
        website: bs = await self._get_website(self._URL.format(page, await self._random_rating(tag)))
        
        elements = website.find_all('a', class_ = 'post-preview-link')
        post = await self._random_post(len(elements))
        url: str = self._BASE_URL + elements[post].get('href')
        
        website: bs = await self._get_website(url)
        image_url = website.find('img', id = 'image').get('src')
        
        break
      except:
        continue
    
    file_extension: str = image_url.split('.')[-1]
    file: str = image_url.split('/')[-1].replace(f'.{file_extension}', '')
    self._file_name: str = file + '.' + file_extension
    
    self._image = requests.get(image_url).content
    return self._file_name, self._image
    
    # await self.save_image()
    
  async def _get_website(self, url: str) -> bs:
    response: Response = requests.get(url)
    return bs(response.text, 'html.parser')
  
  async def _random_page(self) -> int:
    page = random.randint(self._first_page, self._last_page)
    
    return page

  async def _random_post(self, number_of_elements: int) -> int:
    post = random.randint(0, number_of_elements-1)
    
    return post
  
  async def _random_rating(self, tag: str | None = None) -> str:
    ratings: list[str] = ['general', 'questionable', 'sensitive', 'explicit']
    best_match: Any = None

    if tag and len(tag) == 1:
      first_letter_dictionary: dict[str, str] = {each_rating[0]: each_rating for each_rating in ratings}
      best_match = [first_letter_dictionary.get(tag), 100] if tag and tag in list(first_letter_dictionary.keys()) else None
    else:
      best_match = process.extractOne(tag.lower(), ratings, scorer=fuzz.partial_ratio) if tag else None
    
    # Excludes 'explicit' if tag is not given
    rating: str = f'+rating%3A{best_match[0] if best_match and best_match[1] >= 60 else ratings[random.randint(0, len(ratings)-2)]}+'

    return rating
  
  async def get_image(self) -> bytes:
    return self._image

  async def get_name(self) -> str:
    return self._file_name
  
  async def save_image(self) -> None:
    with open(self._file_name, 'wb') as file:
      file.write(self._image)
  
async def main(args=None):
  dan = Danbooru()
  await dan.start()
  
if __name__ == '__main__':
  asyncio.run(main())