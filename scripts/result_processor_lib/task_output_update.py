"""
@description
--------------------
Given the task output result.log and an existing result csv, it updates the csv with new flagged repositories.

@usage
--------------------
python task-output-update.py result.log csv_to_be_updated.csv --output updated.csv [--filter]
"""
import os
import json
import re
import csv
import sys
import argparse
import logging
from .helpers import load_metadata, parse_result_log
from .constants import KNOWN_CLASS_POLLUTION_FOLDER_PATH, CSV_COLUMNS, HEADER_ROWS, METADATA_PATH, PROJECT_ROOT
from .task_output_classify_repo import classify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_all_known_repos(folder_path):
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

def parse_existing_csv(csv_file):
  existing_repos = []
  try:
    with open(csv_file, 'r', encoding='utf-8') as f:
      reader = csv.reader(f)
      next(reader)
      next(reader)
      
      for row in reader:
        repo_dict = {}
        for i, column in enumerate(CSV_COLUMNS):
          value = row[i] if i < len(row) else ''

          if isinstance(value, str):
            value = value.strip()
          repo_dict[column] = value
        existing_repos.append(repo_dict)
        
  except FileNotFoundError:
    logging.error(f"Error: CSV file '{csv_file}' not found.")
    sys.exit(1)
    
  return existing_repos

def generate_csv_output(flagged_repos, existing_repos, repo_metadata, output_file, all_known_repos):
  # Merge existing and new repos, marking new entries
  all_repos = []
  
  # Process new flagged repos
  for repo in flagged_repos:
    if any(repo["repo_name"] == existing_repo["Application"] for existing_repo in existing_repos):
      continue
    
    NewlyAdded = "Yes"
    if repo["repo_name"] in all_known_repos:
      NewlyAdded = "No"
      
    repo_info = repo_metadata.get(repo["repo_name"], {
      "name": repo["repo_name"],
      "stargazers_count": -1,
      "html_url": f"https://github.com/{repo['repo_name']}"
    })
    
    all_repos.append({
      "Application": repo_info["name"],
      "Stars": repo_info["stargazers_count"],
      "URL": repo_info["html_url"],
      "Confirmed": "N/A",
      "CodeQL": "Y",
      "FP Reason": "",
      "GetType": repo["get_type"],
      "SetType": repo["set_type"],
      "Input": "",
      "Remote": "|".join(repo["remote_patterns"]),
      "Local": "|".join(repo["local_patterns"]),
      "Status": "",
      "Comment": "",
      "NewlyAdded": NewlyAdded
    })

  # Add existing repos (preserve their data)
  all_repos.extend(existing_repos)

  # Sort all repos by stars (descending) 
  all_repos_sorted = sorted(
    all_repos,
    key=lambda x: int(x.get("Stars", 0)) if str(x.get("Stars", 0)).isdigit() else 0,
    reverse=True
  )

  with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    # Write custom header rows
    csvfile.write(HEADER_ROWS)
    
    # Create writer and write data rows
    writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
    
    for repo in all_repos_sorted:
      # Ensure all columns are present
      clean_repo = {col: repo.get(col, "") for col in CSV_COLUMNS}
      writer.writerow(clean_repo)

def update_csv(result_file, csv_file, output_file):
  repo_metadata = load_metadata(METADATA_PATH)
  flagged_repos = parse_result_log(result_file)

  existing_repos = parse_existing_csv(csv_file)
  all_known_repos = load_all_known_repos(KNOWN_CLASS_POLLUTION_FOLDER_PATH)
  generate_csv_output(flagged_repos, existing_repos, repo_metadata, output_file, all_known_repos)

  logging.info(f"CSV file '{output_file}' generated successfully.")