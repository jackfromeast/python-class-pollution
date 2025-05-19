"""
@description
--------------------
Given the task output result.log, it summarizes the flagged repositories and optionally includes metadata such as stargazers count and download count.

@usage
--------------------
python task-output-summary.py result.log --output flagged_repos.csv [--filter]
"""
import os
import json
import re
import csv
import sys
import argparse
import logging
from .helpers import load_metadata, load_pip_metadata, parse_result_log, load_all_known_repos
from .constants import KNOWN_CLASS_POLLUTION_FOLDER_PATH, CSV_COLUMNS, HEADER_ROWS, METADATA_PATH, PIP_METADATA_PATH, PROJECT_ROOT, CSV_COLUMNS_PIP
from .task_output_classify_repo import classify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_manually_checked_csv(folder_path):
  known_true_positives = set()
  known_false_positives = set()

  try:
    # Check if the folder exists
    folder_path = os.path.join(PROJECT_ROOT, folder_path)
    if not os.path.exists(folder_path):
      raise FileNotFoundError(f"Folder '{folder_path}' not found.")

    # Get all CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    if not csv_files:
      raise FileNotFoundError("No CSV files found in the folder.")

    # Process each CSV file
    for csv_file in csv_files:
      csv_file_path = os.path.join(folder_path, csv_file)
      with open(csv_file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
          application = row["Application"]
          confirmed = row["Confirmed"]

          if confirmed == "Y":
            known_true_positives.add(application)
          elif confirmed == "N":
            known_false_positives.add(application)

  except FileNotFoundError as e:
    logging.error(f"Error: {e}")
    sys.exit(1)

  return known_true_positives, known_false_positives

def generate_csv_output(flagged_repos, repo_metadata, output_file, all_known_repos, use_pip_metadata=False):
  all_repos = []
  
  # Process new flagged repos
  for repo in flagged_repos:
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
      "Confirmed": "N/A",
      "Func Name (Path)": "",
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

def summary_csv(result_files, output_file, filter=False, use_pip_metadata=False):
  if use_pip_metadata:
    repo_metadata = load_pip_metadata(PIP_METADATA_PATH)
  else:
    repo_metadata = load_metadata(METADATA_PATH)

  flagged_repos = []
  for rf in result_files:
      flagged_repos += parse_result_log(rf)

  filter_repos = None
  if filter:
    known_true_positives, known_false_positives = parse_manually_checked_csv(KNOWN_CLASS_POLLUTION_FOLDER_PATH)
    filter_repos = known_true_positives.union(known_false_positives)

  all_known_repos = load_all_known_repos(KNOWN_CLASS_POLLUTION_FOLDER_PATH)
  generate_csv_output(flagged_repos, repo_metadata, output_file, all_known_repos, use_pip_metadata)

  logging.info(f"CSV file '{output_file}' generated successfully.")