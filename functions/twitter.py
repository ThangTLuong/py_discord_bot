import asyncio
from aiohttp import ClientSession
from dotenv import dotenv_values as dv
from datetime import datetime
import pytz

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class Twitter:
  def __init__(self, account: str) -> None:
    self._ENV = dv('.env')
    self._LOGIN_PAGE = 'https://twitter.com/login'
    self._account: dict[str, str | None] = self._ENV[account]
    self._list_of_tweets: list[str] = []
    self._tweet_urls: list[str] = []
    self._sent_tweet: str = None
    
    self._timezone = pytz.timezone('America/Los_Angeles')

    self._op = webdriver.ChromeOptions()
    self._op.add_argument('--headless')
    self._op.add_argument('--window-size=1920x1080')

  async def __aenter__(self):
    return self

  async def __aexit__(self, exc_type, exc_value, traceback) -> None:
    print('Shutting down driver')
    await self.quit()
    
  async def start(self) -> bool:
    """
    Starts scraiping Twitter. It will take a few seconds to run.\n
    The links of the tweets are accessible with the function get.urls().
    
    
    Parameters
    ---------------
    None
    
    Returns
    ---------------
    boolean
      True if the twitter page has been updated. \n
      False if the twitter page has NOT been updated.
    """
    self._driver = webdriver.Chrome(options=self._op)
    self._driver.get(self._LOGIN_PAGE)
    await self._slp()

    await self._input_username('EMAIL')
    await self._slp()

    try:
      await self._input_password()
    except Exception:
      await self._input_username('USERNAME')
      await self._slp()
      await self._input_password()
    await self._slp()

    try:
      await self._input_search_item(self._account)
    except Exception:
      await self._explore()
      await self._slp()
      await self._input_search_item(self._account)
    await self._slp()

    await self._get_profile()
    await self._slp()
    await self._get_media()
    await self._slp()

    return await self._get_tweet()

  async def _slp(self, seconds=3.0) -> None:
    await asyncio.sleep(seconds)

  async def _input_username(self, env) -> None:
    username = self._driver.find_element(By.XPATH, '//input[@name=\'text\']')
    username.send_keys(self._ENV[env])
    next_button = self._driver.find_element(By.XPATH, '//span[contains(text(), \'Next\')]')
    next_button.click()

  async def _input_password(self) -> None:
    password = self._driver.find_element(By.XPATH, '//input[@name=\'password\']')
    password.send_keys(self._ENV['PASSWORD'])
    log_in = self._driver.find_element(By.XPATH, '//span[contains(text(), \'Log in\')]')
    log_in.click()

  async def _input_search_item(self, account: str) -> None:
    search_box = self._driver.find_element(By.XPATH, '//input[@data-testid=\'SearchBox_Search_Input\']')
    search_box.send_keys(account)
    search_box.send_keys(Keys.ENTER)

    await self._slp(1)

    people = self._driver.find_element(By.XPATH, '//span[contains(text(), \'People\')]')
    people.click()

  async def _explore(self) -> None:
    explore = self._driver.find_element(By.XPATH, '//a[@aria-label=\'Search and explore\']')
    explore.click()

  async def _get_profile(self) -> None:
    max_retries: int = 3
    retry_delay: int = 3
    retry_additional_delay: int = 2
    retry_count: int = 0
    
    while retry_count < max_retries:
      try:
        profile = self._driver.find_element(By.XPATH, '//*[@id=\'react-root\']/div/div/div[2]/main/div/div/div/div/div/div[3]/section/div/div/div[1]/div/div/div/div/div[2]/div[1]/div[1]/div/div[1]/a/div/div[1]/span/span[1]')
        await self._slp(1)
        profile.click()
        break
      except NoSuchElementException:
        retry_count += 1
        
        if retry_count > max_retries:
          timenow = datetime.now(self._timezone).strftime("%m/%d/%Y %H:%M:%S %Z%z")
          print(f'[{timenow}] [Error]: Profile was not found. Unable to get profile. Aborting...')
          break
        
        timenow = datetime.now(self._timezone).strftime("%m/%d/%Y %H:%M:%S %Z%z")
        print(f'[{timenow}] [Error]: Profile was not found. Retrying...')
        retry_delay += retry_additional_delay
        await self._slp(retry_delay)

  async def _get_media(self) -> None:
    media = self._driver.find_element(By.XPATH, '//*[@id=\'react-root\']/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/nav/div/div[2]/div/div[3]/a/div/div/span')
    media.click()

  async def _load_posts(self) -> None:
    self._driver.execute_script('window.scrollTo(0,300)')

  async def _get_posts(self) -> None:
    self._list_of_tweets.clear()
    for i in range(1, 10):
      try:
        await self._load_posts()
        await self._slp(0.2)
        self._list_of_tweets.append(
          self._driver.find_element(By.XPATH,f'/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/section/div/div/div[{i}]/div/div/article/div/div/div[2]/div[2]/div[1]/div/div[1]/div/div/div[2]/div/div[3]/a').get_attribute('href'))
      except:
        continue

  async def _get_tweet(self) -> bool:
    await self._get_posts()

    await self._load_tweets()
    index = await self._find_last_sent_tweet()

    if index != 0 and index != -1:
      self._tweet_urls = self._list_of_tweets[:index]
    elif index == -1:
      self._tweet_urls = self._list_of_tweets
    else:
      await self.quit()
      return False

    await self._save_tweets()
    await self.quit()
    return True

  async def _load_tweets(self) -> None:
    with open(f'{self._ENV["BOT_DB"]}/tweets.txt', 'r') as file:
      self._sent_tweet = file.read()

  async def _save_tweets(self) -> None:
    with open(f'{self._ENV["BOT_DB"]}/tweets.txt', 'w') as file:
      file.write(str(self._list_of_tweets[0]))

  async def _find_last_sent_tweet(self) -> int:
    try:
      return self._list_of_tweets.index(self._sent_tweet)
    except ValueError:
      return -1

  def get_urls(self) -> list[str]:
    list_of_tweets = self._tweet_urls.copy()
    list_of_tweets.reverse()

    return list_of_tweets

  async def quit(self) -> None:
    self._driver.quit()

async def main():
  async with Twitter() as twitter:
    await twitter.start()

if __name__ == "__main__":
  asyncio.run(main())
