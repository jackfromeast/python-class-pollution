import os
import json
import re
import csv
import sys
import argparse
import logging
from .constants import KNOWN_CLASS_POLLUTION_FOLDER_PATH, CSV_COLUMNS, HEADER_ROWS, METADATA_PATH, PROJECT_ROOT
from .task_output_classify_repo import classify

def load_all_known_repos(folder_path):
  # If folder_path is relative, make it absolute
  if not os.path.isabs(folder_path):
    folder_path = os.path.join(PROJECT_ROOT, folder_path)

  known_repos = set()
  if not os.path.isdir(folder_path):
    logging.warning(f"Known class pollution folder not found: {folder_path}")
    return known_repos

  for filename in os.listdir(folder_path):
    if not filename.endswith('.csv'):
      continue
    csv_path = os.path.join(folder_path, filename)
    try:
      with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) 
        next(reader)  # Skip second header row
        for row in reader:
          if row:  # Check for non-empty rows
            app_name = row[0].strip()  # Application is first column
            known_repos.add(app_name)
    except Exception as e:
      logging.error(f"Error reading {csv_path}: {e}")
  return known_repos
  
def load_metadata(metadata_files):
  repo_metadata = {}

  for file in metadata_files:
    try:
      file = os.path.join(PROJECT_ROOT, file)
      with open(file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        for repo in metadata:
          repo_metadata[repo["name"]] = {
            "name": repo["name"],
            "stargazers_count": repo.get("stargazers_count", 0),
            "html_url": repo.get("html_url", "")
          }
    except (json.JSONDecodeError, FileNotFoundError) as e:
      print(f"Warning: Could not process {file}: {e}")

  return repo_metadata

def load_pip_metadata(metadata_files):
  repo_metadata = {}

  for file in metadata_files:
    try:
      file = os.path.join(PROJECT_ROOT, file)
      with open(file, 'r', encoding='utf-8') as f:
        metadata = csv.DictReader(f)
        for row in metadata:
          repo_metadata[row["package_name"]] = {
            "name": row["package_name"],
            "downloads": int(row.get("total_downloads_last_month", -1)),
            "html_url": "https://pypi.org/project/" + row["package_name"]
          }
    except (csv.Error, FileNotFoundError) as e:
      print(f"Warning: Could not process {file}: {e}")

  return repo_metadata

def parse_result_log(log_file):
  flagged_repos = []
  output_path = os.path.join(os.path.dirname(log_file), '..', "output")

  with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
      match = re.search(r"INFO - ([\w-]+) - .*/([^/]+?):", line)
      if match:
        repo_name = match.group(1)
        query_name = match.group(2).lower()

        # Define mappings for set and get types
        set_type_map = {
            'attr': 'Attr',
            'item': 'Field',
            'both': 'Attr/Field'
        }
        get_type_map = {
            'attr': 'Attr',
            'both': 'Attr/Field'
        }

        parts = query_name.split('-')
        set_type = ''
        get_type = ''
        if len(parts) >= 4 and parts[0] == 'set' and parts[2] == 'get':
          set_part = parts[1]
          get_part = parts[3]
          set_type = set_type_map.get(set_part, '')
          get_type = get_type_map.get(get_part, '')
        
        repo_src_path = os.path.join(output_path, repo_name, "codebase")
        web_patterns, local_patterns = classify(repo_src_path)

        # Append the repository with its GetType and SetType as a new entry
        flagged_repos.append({
          "repo_name": repo_name,
          "get_type": get_type,
          "set_type": set_type,
          "remote_patterns": web_patterns,
          "local_patterns": local_patterns
        })
      else:
        logging.warning(f"Warning: Could not parse line: {line.strip()}")  # Use strip() to remove extra newlines

  return flagged_repos