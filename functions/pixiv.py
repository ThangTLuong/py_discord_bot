from bs4 import BeautifulSoup as bs
import requests
import random
import asyncio

class Pixiv():
  def __init__(self) -> None:
    self._BASE_URL: str = 'https://danbooru.donmai.us'
    self._URL: str = 'https://danbooru.donmai.us/posts?page={}&tags=azur_lane'
    self._first_page, self._last_page = 1, 999
    
    self._image: bytes | None = None
    self._file_name: str | None = None
    
  async def start(self) -> None:
    page = await self._random_page()
    response = requests.get(self._URL.format(page))
    website = bs(response.text, 'html.parser')
    
    elements = website.find_all('a', class_ = 'post-preview-link')
    post = await self._random_post(len(elements))
    url: str = self._BASE_URL + elements[post].get('href')
    
    response = requests.get(url)
    website = bs(response.text, 'html.parser')
    image_url = website.find('img', id = 'image').get('src')
    
    file_extension: str = image_url.split('.')[-1]
    file: str = image_url.split('/')[-1].replace(f'.{file_extension}', '')
    self._file_name: str = file + '.' + file_extension
    
    self._image = requests.get(image_url).content
    
    # await self.save_image()
  
  async def _random_page(self) -> int:
    page = random.randint(self._first_page, self._last_page)
    
    return page

  async def _random_post(self, number_of_elements: int) -> int:
    post = random.randint(0, number_of_elements-1)
    
    return post
  
  async def get_image(self) -> bytes:
    return self._image

  async def get_name(self) -> str:
    return self._file_name
  
  async def save_image(self) -> None:
    with open(self._file_name, 'wb') as file:
      file.write(self._image)
  
async def main(args=None):
  pix = Pixiv()
  await pix.start()
  
if __name__ == '__main__':
  asyncio.run(main())