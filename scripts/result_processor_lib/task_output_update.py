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
from .helpers import load_metadata, parse_result_log, load_all_known_repos, load_pip_metadata
from .constants import KNOWN_CLASS_POLLUTION_FOLDER_PATH, CSV_COLUMNS, HEADER_ROWS, METADATA_PATH, PROJECT_ROOT, PIP_METADATA_PATH, CSV_COLUMNS_PIP
from .task_output_classify_repo import classify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_existing_csv(csv_file, use_pip_metadata=False):
  existing_repos = []
  try:
    with open(csv_file, 'r', encoding='utf-8') as f:
      reader = csv.reader(f)
      next(reader)
      next(reader)
      
      columns_to_use = CSV_COLUMNS_PIP if use_pip_metadata else CSV_COLUMNS

      for row in reader:
        repo_dict = {}

        for i, column in enumerate(columns_to_use):
          value = row[i] if i < len(row) else ''

          if isinstance(value, str):
            value = value.strip()
          repo_dict[column] = value
        existing_repos.append(repo_dict)
        
  except FileNotFoundError:
    logging.error(f"Error: CSV file '{csv_file}' not found.")
    sys.exit(1)
    
  return existing_repos

def generate_csv_output(flagged_repos, existing_repos, repo_metadata, output_file, all_known_repos, use_pip_metadata):
  # Merge existing and new repos, marking new entries
  all_repos = []
  
  # Process new flagged repos
  for repo in flagged_repos:
    if any(repo["repo_name"] == existing_repo["Application"] for existing_repo in existing_repos):
      # Support updating the patterns of existing repos
      # Find the existing repo in the list
      existing_repo = next(existing_repo for existing_repo in existing_repos if repo["repo_name"] == existing_repo["Application"])
      existing_repo["Remote"] = "|".join(repo["remote_patterns"])
      existing_repo["Local"] = "|".join(repo["local_patterns"])
      existing_repo["Func Name (Path)"] = repo["class_pollution_func"]
      continue

    NewlyAdded = "Yes"
    if repo["repo_name"] in all_known_repos:
      NewlyAdded = "No"
      
    if not use_pip_metadata:
      repo_info = repo_metadata.get(repo["repo_name"], {
        "name": repo["repo_name"],
        "stargazers_count": -1,
        "html_url": f"https://github.com/{repo['repo_name']}"
      })
    else:
      repo_info = repo_metadata.get(repo["repo_name"], {
        "name": repo["repo_name"],
        "downloads": -1,
        "html_url": f"https://pypi.org/project/{repo['repo_name']}"
      })
    
    repo_data = {
      "Application": repo_info["name"],
      # "Stars": repo_info["stargazers_count"],
      "URL": repo_info["html_url"],
      "CodeQL": "Y",
      "Confirmed (Function-level)": "N/A",
      "Func Name (Path)": repo["class_pollution_func"],
      "FP Reason": "",
      "GetType": repo["get_type"],
      "SetType": repo["set_type"],
      "Triggering": "",
      "Remote": "|".join(repo["remote_patterns"]),
      "Local": "|".join(repo["local_patterns"]),
      "Status": "",
      "Comment": "",
      "NewlyAdded": NewlyAdded
    }

    if use_pip_metadata:
      repo_data["Downloads"] = repo_info["downloads"]
    else:
      repo_data["Stars"] = repo_info["stargazers_count"]
  
    all_repos.append(repo_data)

  # Add existing repos (preserve their data)
  all_repos.extend(existing_repos)

  # Sort all repos by stars (descending) 
  if use_pip_metadata:
    all_repos_sorted = sorted(
      all_repos,
      key=lambda x: int(x.get("Downloads", 0)) if str(x.get("Downloads", 0)).isdigit() else 0,
      reverse=True
    )
  else:
    all_repos_sorted = sorted(
      all_repos,
      key=lambda x: int(x.get("Stars", 0)) if str(x.get("Stars", 0)).isdigit() else 0,
      reverse=True
    )

  with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    # Write custom header rows
    csvfile.write(HEADER_ROWS)
    
    # Create writer and write data rows
    if use_pip_metadata:
      writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS_PIP)
    else:
      writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)

    for repo in all_repos_sorted:
      # Ensure all columns are present
      if use_pip_metadata:
        clean_repo = {col: repo.get(col, "") for col in CSV_COLUMNS_PIP}
      else:
        clean_repo = {col: repo.get(col, "") for col in CSV_COLUMNS}
      writer.writerow(clean_repo)


def update_csv(result_files, csv_files, output_file, use_pip_metadata=False):
  if use_pip_metadata:
    repo_metadata = load_pip_metadata(PIP_METADATA_PATH)
  else:
    repo_metadata = load_metadata(METADATA_PATH)

  flagged_repos = []
  for rf in result_files:
    flagged_repos += parse_result_log(rf)

  existing_repos = []
  for csv_file in csv_files:
    existing_repos += parse_existing_csv(csv_file, use_pip_metadata)

  print(existing_repos[:1])

  all_known_repos = load_all_known_repos(KNOWN_CLASS_POLLUTION_FOLDER_PATH)
  generate_csv_output(flagged_repos, existing_repos, repo_metadata, output_file, all_known_repos, use_pip_metadata)

  logging.info(f"CSV file '{output_file}' generated successfully.")