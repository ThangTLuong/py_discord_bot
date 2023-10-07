from datetime import datetime
import pytz

class Time_Log():
  def __init__(self) -> None:
    self._timezone = pytz.timezone('America/Los_Angeles')
    self._time_now: str | None = None
    
  async def now(self) -> None:
    self._time_now = datetime.now(self._timezone).strftime('%m/%d/%Y %H:%M:%S %Z%z')

  
  async def print_time(self, message: str = '') -> None:
    if self._time_now == None:
      return
    
    print(f'[{self._time_now}] : {message}')