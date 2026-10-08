import sys
from pathlib import Path


class DatasetManager:
 def ensure(self,name):
  path=Path('data/fixtures/furniture.json'); return {'name':name,'status':'reused' if path.exists() else 'missing','path':str(path)}
if __name__=='__main__': print(DatasetManager().ensure(sys.argv[-1]))
