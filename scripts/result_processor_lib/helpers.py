import os
import json
import re
import csv
import sys
import argparse
import logging
from .constants import KNOWN_CLASS_POLLUTION_FOLDER_PATH, CSV_COLUMNS, HEADER_ROWS, METADATA_PATH, PROJECT_ROOT

def load_metadata(metadata_files):
  file = os.path.join(PROJECT_ROOT, file)
  repo_metadata = {}

  for file in metadata_files:
    try:
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