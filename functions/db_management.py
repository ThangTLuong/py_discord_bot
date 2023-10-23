from dotenv import dotenv_values as dv
from tinydb import TinyDB, Query
from typing import (Any, Dict, List)

import sys
import asyncio

sys.path.append('..')
from template import TEMPLATES

class DB_Management():
  lock = asyncio.Lock()
  
  def __init__(self, database: str) -> None:
    self._ENV = dv('../.env')
    
    if database.split('.')[-1] != 'json':
      database = f'{database}.json'
    
    self._db: TinyDB = TinyDB(f'{self._ENV["DB"]}/{database}', indent=2)
    self._query: Query = Query()
    
  async def __aenter__(self):
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback) -> None:
    await self.close()
    
  async def insert(self, type: str, **kwargs) -> None:
    """
    Use to create or modify the existing data. 
    
    If a data needs to be added/removed from a queue, 
    use queue/dequeue.
    """
    if self._db is None: return
    if not await self._matches_template(type, list(kwargs.keys())): raise ValueError(f'Invalid \'type\': {type}. Supported types are {list(TEMPLATES.keys())}')
    
    template: List[str] = TEMPLATES[type]
    entity: Dict[str, Any] = await self._new(**kwargs)
    entity[template[0]] = entity[template[0]].upper()
    
    async with self.__class__.lock:
      if self._db.contains(self._query[template[0]] == entity[template[0]]):
        self._db.update(entity, self._query[template[0]] == entity[template[0]])
      else:
        self._db.insert(entity)
        
  async def retrieve(self, type: str, **kwargs) -> Dict[str, Any]:
    if self._db is None: return

    entity: str
    for key, value in kwargs.items():
      entity = self._db.get(self._query[key] == value)
    
    return entity
    
  async def _matches_template(self, type: str, keys: List[str]) -> bool:
    if type not in TEMPLATES: return False
    return keys == TEMPLATES[type]
    
  async def _new(self, **kwargs) -> Dict[str, Any]:
    new_entity: Dict[str, Any] = {}
    
    for key, value in kwargs.items():
      new_entity[key] = value
      
    return new_entity

  async def close(self) -> None:
    self._db.close()
    
async def main():
  async with DB_Management('db.json') as db:
    entity = await db.retrieve('news', game = 'AZUR LANE')
    print(entity['last_tweet'])

if __name__ == '__main__':
  asyncio.run(main())