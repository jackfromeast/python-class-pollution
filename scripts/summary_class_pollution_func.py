import os
import json
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
task_dir = os.path.join(script_dir, "../", "tasks", "class-pollution-1K-with-remote-pattern")
repo_list_path = os.path.join(task_dir, "input", "repo-with-remote-patterns.txt")
output_base = os.path.join(task_dir, "output")
result_path = os.path.join(task_dir, "logs", "class-pollution-function-only.json")

with open(repo_list_path, 'r') as f:
  repo_lines = [line.strip() for line in f if line.strip()]

output = []

for line in repo_lines:
  repo_url = line
  repo_name = repo_url.rstrip('/').split('/')[-1]

  # Path to the SARIF file
  sarif_path = os.path.join(output_base, repo_name, "results", "class-pollution-function-only.qls.sarif")
  if not os.path.exists(sarif_path):
    print(f"Missing SARIF for {repo_name}: {sarif_path}")
    continue

  # Extract function names from the SARIF file
  with open(sarif_path, 'r') as f:
    sarif_data = f.read()

  # This regex assumes function names appear as "functionName": "set_attr" or similar in the SARIF
  # Adjust if your SARIF format differs!
  func_names = re.findall(r'\[Function\s(\w+)\]', sarif_data)
  func_names = list(sorted(set(func_names)))  # Unique and sorted

  # Prepare the summary JSON
  summary = {
    "repo": repo_url,
    "class_pollution_func": func_names
  }

  output.append(summary)

with open(result_path, 'w') as f:
  json.dump(output, f, indent=2)

print(f"Wrote summary to {result_path}")
