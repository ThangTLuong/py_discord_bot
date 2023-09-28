import asyncio
from bs4 import BeautifulSoup as bs
import requests
from requests import Response
from requests_html import AsyncHTMLSession
import random

class Pixiv():
  def __init__(self) -> None:
    self._URL: str = 'https://www.pixiv.net/en/tags/アズールレーン1000users入り/illustrations?p='
    self._first_page, self._last_page = 1, 416
    self._first_img, self._last_img = 0, 62
    
    self._session: AsyncHTMLSession = AsyncHTMLSession()
    self._response: Response | None = None
  
  async def start(self) -> None:
    await self._get_response(f'{self._URL}{random.randint(self._first_page, self._last_page)}')
    
    soup = bs(self._response.html.html, 'html.parser')
    elements = soup.find_all('a', class_ = 'sc-d98f2c-0 sc-rp5asc-16 iUsZyY sc-cKRKFl ejjglN')
    
    
    url: str = ''
    while True:
      try:
        url = f'https://www.pixiv.net/en{elements[random.randint(self._first_img, self._last_img)].get("href")}'
        await self._get_response(url)
    
        soup = bs(self._response.html.html, 'html.parser')
        image = soup.find(class_ = 'sc-1qpw8k9-3 eFhoug gtm-expand-full-size-illust').find('img').get('src')
        break
      except Exception as e:
        print(e)
        continue
      
    image = image.replace('_master1200', '').replace('-master', '-original')
    file_extension: str = image.split('.')[-1]
    headers = {"Referer": f"{url}"}

    response = requests.get(image, headers=headers)
    with open('image.' + file_extension, 'wb') as file:
      file.write(response.content)
    
    await self.quit()
    
  async def _get_response(self, url: str) -> None:
    self._response = await self._session.get(url, timeout=30)
    await self._response.html.arender()
    
  async def quit(self):
    await self._session.close()
    
async def main():
  pix = Pixiv()
  await pix.start()
  
if __name__ == '__main__':
  asyncio.run(main())