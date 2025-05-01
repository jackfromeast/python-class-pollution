import os
import json
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
task_dir = os.path.join(script_dir, "../", "tasks", "class-pollution-1K-with-remote-pattern")
repo_list_path = os.path.join(task_dir, "input", "repo-with-remote-patterns.txt")
output_base = os.path.join(task_dir, "output")
result_path = os.path.join(task_dir, "logs", "class-pollution-function-only.json")

output = []

for line in open(repo_list_path):
  repo_url = line.strip()
  if not repo_url: continue
  repo_name = repo_url.rstrip('/').split('/')[-1]
  sarif_path = os.path.join(output_base, repo_name, "results", "class-pollution-function-only.qls.sarif")
  if not os.path.exists(sarif_path):
    print(f"Missing SARIF for {repo_name}: {sarif_path}")
    continue

  with open(sarif_path, 'r') as f:
    sarif_json = json.load(f)

  func_locs = []
  func_names = set()
  for run in sarif_json.get("runs", [])[0].get("results", []):
    for loc in run.get("relatedLocations", []):
      loc_id = str(loc.get("id"))
      physical = loc.get("physicalLocation", {})
      uri = physical.get("artifactLocation", {}).get("uri")
      region = physical.get("region", {})
      func_name = loc.get("message", {}).get("text", "").strip("Function ")

      if func_name in func_names:
        continue

      func_locs.append({
        "function": func_name,
        "location": {
          "file": uri,
          "start_line": region.get("startLine"),
          "start_column": region.get("startColumn"),
          "end_column": region.get("endColumn"),
        }
      })
      func_names.add(func_name)

  summary = {
    "repo": repo_url,
    "class_pollution_func": func_locs
  }
  output.append(summary)

with open(result_path, 'w') as f:
  json.dump(output, f, indent=2)

print(f"Wrote summary to {result_path}")