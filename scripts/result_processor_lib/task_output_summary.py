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
from .helpers import load_metadata, parse_result_log
from .constants import KNOWN_CLASS_POLLUTION_FOLDER_PATH, CSV_COLUMNS, HEADER_ROWS, METADATA_PATH
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

def generate_csv_output(flagged_repos, repo_metadata, output_file, filter_repos=None):
  # Sort flagged_repos by stars (descending order)
  flagged_repos_sorted = sorted(
    flagged_repos,
    key=lambda x: repo_metadata.get(x["repo_name"], {}).get("stargazers_count", -1),
    reverse=True
  )

  with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["repo_name", "stars", "url", "Confirmed", "CodeQL", "FP Reason", "GetType", "SetType", "Input", "Remote", "Local"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for repo in flagged_repos_sorted:
      if filter_repos and repo["repo_name"] in filter_repos:
        continue  # Skip this repo if it's in the filter list

      repo_info = repo_metadata.get(repo["repo_name"], {
        "name": repo["repo_name"],
        "stargazers_count": -1,
        "html_url": f"https://github.com/{repo['repo_name']}"
      })
      writer.writerow({
        "repo_name": repo_info["name"],
        "stars": repo_info["stargazers_count"],
        "url": repo_info["html_url"],
        "Confirmed": "N/A",  # Empty by default
        "CodeQL": "Y",    # Always set to "Yes"
        "FP Reason": "",  # Empty by default
        "GetType": repo["get_type"],
        "SetType": repo["set_type"],
        "Input": "",
        "Remote": "|".join(repo["remote_patterns"]),
        "Local": "|".join(repo["local_patterns"])
      })

def summary_csv(log_file, output_file, filter=False):
  repo_metadata = load_metadata(METADATA_PATH)

  flagged_repos = parse_result_log(log_file)

  filter_repos = None
  if filter:
    known_true_positives, known_false_positives = parse_manually_checked_csv(KNOWN_CLASS_POLLUTION_FOLDER_PATH)
    filter_repos = known_true_positives.union(known_false_positives)

  generate_csv_output(flagged_repos, repo_metadata, output_file, filter_repos)

  logging.info(f"CSV file '{output_file}' generated successfully.")