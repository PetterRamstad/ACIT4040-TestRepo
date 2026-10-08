import json
from pathlib import Path

result={'experiment':'fixture-baseline','preference':{'stability':1.0},'retrieval':{'recall_at_5':1.0},'layout':{'collision_rate':0.0}}
Path('data/experiment-result.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result))
