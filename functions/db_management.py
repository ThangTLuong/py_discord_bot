from typing import Any
from dotenv import dotenv_values as dv
from tinydb import TinyDB, Query
from pprint import pprint

import asyncio

class DB():
  def __init__(self) -> None:
    self._ENV = dv('../.env')
    self._db = TinyDB(self._ENV['DB'])
    self._query = Query()
    
    self._category: str | None = None
    self._function: str | None = None
    
  async def __aenter__(self):
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback) -> None:
    await self.close()
    
  async def insert(self, data: str | None = None) -> None:
    """
    Use to create or replace the existing data. \n
    If a data needs to be added/removed from a queue, 
    use queue/dequeue.
    """
    if self._category == None or self._function == None or data == None:
      return
    
    result = self._db.search(self._query[self._category].exists())
    if not bool(result):
      self._db.insert({self._category: {self._function: data}})
    else:
      await self._update(data)
      
  async def _update(self, data: Any | None = None) -> None:
    result = self._db.get(self._query[self._category].exists())
    if result.get(self._category)[self._function] == data:
      return
    
    result.get(self._category)[self._function] = data
    self._db.update(result, self._query[self._category].exists())
    
  async def queue(self) -> None:
    pass
  
  async def dequeue(self) -> None:
    pass
    
  async def set_category(self, category: str | None = None):
    self._category = category.upper()
    
  async def set_function(self, function: str | None = None):
    self._function = function.upper()
    
  async def print_db(self) -> None:
    pprint(self._db.all())
  
  async def close(self) -> None:
    self._db.close()
    
async def main(args=None):
  async with DB() as db:
    await db.print_db()
    
if __name__ == '__main__':
  asyncio.run(main())