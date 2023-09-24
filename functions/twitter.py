from time import sleep
from dotenv import dotenv_values as dv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class Twitter():
  def __init__(self) -> None:
    self._ENV: dict[str, str | None] = dv('../.env')
    self._LOGIN_PAGE: str = 'https://twitter.com/login'
    self._tweet_url: str | None = None
    
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    
    self._driver = webdriver.Chrome(options=op)
    
  def __del__(self) -> None:
    self.quit()
    
  def start(self) -> str:
    self._driver.get(self._LOGIN_PAGE)
    self._slp()
    
    self._input_username('EMAIL')
    self._slp()
    
    try:
      self._input_password()
    except Exception:
      self._input_username('USERNAME')
      self._slp()
      self._input_password()
    self._slp()
    
    try:
      self._input_search_item()
    except Exception:
      self._explore()
      self._slp()
      self._input_search_item()
    self._slp()
    
    self._get_profile()
    self._slp()
    self._get_media()
    self._slp()
    self._get_lastest_post()
    
    return self._tweet_url
  
  def _slp(self) -> None:
    sleep(3)
    
  def _input_username(self, env: str) -> None:
    username = self._driver.find_element(By.XPATH, '//input[@name=\'text\']')
    username.send_keys(self._ENV[env])
    next_button = self._driver.find_element(By.XPATH, '//span[contains(text(), \'Next\')]')
    next_button.click()

    
  def _input_password(self) -> None:
    password = self._driver.find_element(By.XPATH, '//input[@name=\'password\']')
    password.send_keys(self._ENV['PASSWORD'])
    log_in = self._driver.find_element(By.XPATH, '//span[contains(text(), \'Log in\')]')
    log_in.click()
  
  def _input_search_item(self) -> None:
    search_box = self._driver.find_element(By.XPATH, '//input[@data-testid=\'SearchBox_Search_Input\']')
    search_box.send_keys(self._ENV['USER'])
    search_box.send_keys(Keys.ENTER)

    people = self._driver.find_element(By.XPATH, '//span[contains(text(), \'People\')]')
    people.click()
    
  def _explore(self) -> None:
    explore = self._driver.find_element(By.XPATH, '//a[@aria-label=\'Search and explore\']')
    explore.click()
    
  def _get_profile(self) -> None:
    profile = self._driver.find_element(By.XPATH, '//*[@id=\'react-root\']/div/div/div[2]/main/div/div/div/div/div/div[3]/section/div/div/div[1]/div/div/div/div/div[2]/div[1]/div[1]/div/div[1]/a/div/div[1]/span/span[1]')
    profile.click()
    
  def _get_media(self) -> None:
    media = self._driver.find_element(By.XPATH, '//*[@id=\'react-root\']/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/nav/div/div[2]/div/div[3]/a/div/div/span')
    media.click()
    
  def _get_lastest_post(self) -> None:
    self._tweet_url = self._driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/section/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div[1]/div/div[1]/div/div/div[2]/div/div[3]/a').get_attribute('href')
    
  def get_url(self) -> str:
    return self._tweet_url
  
  def quit(self) -> None:
    self._driver.quit()
    
def main(args=None):
  twt = Twitter()
  print(twt.start())
  
if __name__ == '__main__':
  main()