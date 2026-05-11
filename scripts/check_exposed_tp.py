import csv
import json
import os

INPUT_CSV = "/home/jackfromeast/Desktop/python-class-pollution/dataset/temp/The Python World-Class Pollution - Github-Top-1K-0523.csv" 
EXPOSED_APIS_ROOT = "/home/jackfromeast/Desktop/python-class-pollution/tasks/github-dataset/class-pollution-1K-r4/output"

def load_exposed_apis(repo):
    path = os.path.join(EXPOSED_APIS_ROOT, repo, "exposed_apis.json")
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        apis = json.load(f)
    return set(api.split('.')[-1] for api in apis)

with open(INPUT_CSV, newline='') as infile:
  reader = csv.DictReader(infile)
  for row in reader:
    last_col = list(row.values())[-1]
    if not last_col:
      continue
    repo = row['Application']
    func_names = [entry.split(':')[0] for entry in last_col.split(',')]
    exposed_funcs = load_exposed_apis(repo)
    is_exposed = all(fn in exposed_funcs for fn in func_names)
    if is_exposed:
      print(f"Repo: {repo}, Functions: {func_names}")