"""
@description
--------------------
Given the input.txt and result.log, it compares them and prints the missing packages.
"""
import re
import sys
import os
from .constants import TRUE_POSITIVES_FILE_PATH, PROJECT_ROOT

import os
import re
import csv
import sys
from .constants import TRUE_POSITIVES_FILE_PATH, PROJECT_ROOT

def check_cwd():
  """Verify correct working directory"""
  cwd = os.getcwd()
  if not cwd.endswith("python-class-pollution"):
    raise ValueError("Current working directory must be 'python-class-pollution'")

def parse_result_log(log_file):
  """Extract repo to set of (get_type, set_type) mappings from log"""
  entries = {}
  try:
    with open(log_file, 'r', encoding='utf-8') as f:
      for line in f:
        match = re.search(r"INFO - ([\w-]+) - .*/([^/]+?):", line)
        if match:
          repo = match.group(1)
          query = match.group(2).lower()
          parts = query.split('-')
          get_type, set_type = '', ''
          if len(parts) >= 4 and parts[0] == 'set' and parts[2] == 'get':
            set_map = {'attr': 'Attr', 'item': 'Field', 'both': 'Attr/Field'}
            get_map = {'attr': 'Attr', 'both': 'Attr/Field'}
            set_type = set_map.get(parts[1], '')
            get_type = get_map.get(parts[3], '')
          if repo not in entries:
            entries[repo] = set()
          entries[repo].add((get_type, set_type))
  except FileNotFoundError:
    print(f"Error: Log file {log_file} not found")
    sys.exit(1)
  return entries

def parse_true_positives_csv(csv_file):
  """Extract {app: (get_type, set_type)} from CSV"""
  entries = {}
  try:
    csv_path = os.path.join(PROJECT_ROOT, csv_file)
    with open(csv_path, 'r', encoding='utf-8') as f:
      reader = csv.reader(f)
      next(reader)  # Skip headers
      next(reader)
      for row in reader:
        if len(row) < 8:
          continue
        app = row[0].strip()
        get_type = row[6].strip()
        set_type = row[7].strip()
        entries[app] = (get_type, set_type)
  except FileNotFoundError:
    print(f"Error: CSV file {csv_path} not found")
    sys.exit(1)
  return entries

def compare_true_positives(log_file):
  """Compare log entries with CSV entries and report discrepancies"""
  log_entries = parse_result_log(log_file)
  csv_entries = parse_true_positives_csv(TRUE_POSITIVES_FILE_PATH)

  missing_repos = []
  type_mismatches = []
  new_entries = []

  for app in csv_entries:
    csv_get, csv_set = csv_entries[app]
    if app not in log_entries:
      missing_repos.append((app, csv_get, csv_set))
    else:
      found = False
      for (log_get, log_set) in log_entries[app]:
        if log_get == csv_get and log_set == csv_set:
          found = True
          break
      if not found:
        log_pairs = list(log_entries[app])
        type_mismatches.append((app, csv_get, csv_set, log_pairs))

  for repo in log_entries:
    if repo not in csv_entries:
      for (get_t, set_t) in log_entries[repo]:
        new_entries.append((repo, get_t, set_t))

  print(f"Missing true positives (not found in log): {len(missing_repos)}")
  for app, get_t, set_t in sorted(missing_repos):
    print(f"- {app}")
    print(f"  Expected getType: {get_t}, setType: {set_t}\n")

  print(f"\nType mismatches (different get/set types): {len(type_mismatches)}")
  for app, exp_get, exp_set, log_pairs in sorted(type_mismatches, key=lambda x: x[0]):
    log_str = ", ".join([f"get: {g}, set: {s}" for g, s in log_pairs])
    print(f"- {app}")
    print(f"  Expected: getType: {exp_get}, setType: {exp_set}")
    print(f"  Found in log: {log_str}\n")

  print(f"\nNew entries in log not present in CSV: {len(new_entries)}")
  for repo, get_t, set_t in sorted(new_entries):
    print(f"- {repo}")
    print(f"  getType: {get_t}, setType: {set_t}\n")