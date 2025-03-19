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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_output_classify_repo import classify

# Metadata files
metadata_files = [
  "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20100101-20141001-star-1K.json",
  "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20141001-20241001-star-100-1K.json",
  "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20191001-20241001-star-1K.json"
]

# Path to the manually checked CSV file
KNOWN_CLASS_POLLUTION_FOLDER_PATH = "/home/jackfromeast/Desktop/python-class-pollution/dataset/manually-checked"

# Function to load metadata from JSON files
def load_metadata(metadata_files):
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

# Function to parse the result.log file
def parse_result_log(log_file):
  flagged_repos = []
  output_path = os.path.join(os.path.dirname(log_file), '..', "output")

  with open(log_file, 'r', encoding='utf-8') as f:
    for line in f:
      # Updated regex to allow hyphens in repository names and capture the query name
      match = re.search(r"INFO - ([\w-]+) - (.+?)\.ql\.sarif:", line)
      if match:
        repo_name = match.group(1)
        query_name = match.group(2)

        # Determine GetType and SetType based on the query name
        if "SetAttrGetBoth" in query_name:
          get_type = "Attr/Field"
          set_type = "Attr"
        elif "SetAttrGetAttr" in query_name:
          get_type = "Attr"
          set_type = "Attr"
        elif "SetItemGetBoth" in query_name:
          get_type = "Attr/Field"
          set_type = "Field"
        elif "SetItemGetAttr" in query_name:
          get_type = "Attr"
          set_type = "Field"
        elif "SetBothGetAttr" in query_name:
          get_type = "Attr"
          set_type = "Attr/Field"
        elif "SetBothGetBoth" in query_name:
          get_type = "Attr/Field"
          set_type = "Attr/Field"
        else:
          get_type = ""
          set_type = ""
        
        # Classify the repository
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

# Function to parse manually checked CSV files
def parse_manually_checked_csv(folder_path):
  known_true_positives = set()
  known_false_positives = set()

  try:
    # Check if the folder exists
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

# Function to generate the CSV output
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

def main():
  parser = argparse.ArgumentParser(description="Summarize flagged repositories from result.log.")
  parser.add_argument("log_file", help="Path to the result.log file")
  parser.add_argument("--output", help="Output CSV file name (default: same folder as result.log)")
  parser.add_argument("--filter", action="store_true", help="Filter out manually checked repositories")
  args = parser.parse_args()

  # Determine the output file path
  if args.output:
    output_file = args.output
  else:
    # Default to the same folder as result.log
    log_dir = os.path.dirname(args.log_file)
    output_file = os.path.join(log_dir, "flagged_repos.csv")

  repo_metadata = load_metadata(metadata_files)

  flagged_repos = parse_result_log(args.log_file)

  filter_repos = None
  if args.filter:
    known_true_positives, known_false_positives = parse_manually_checked_csv(KNOWN_CLASS_POLLUTION_FOLDER_PATH)
    filter_repos = known_true_positives.union(known_false_positives)

  generate_csv_output(flagged_repos, repo_metadata, output_file, filter_repos)

  logging.info(f"CSV file '{output_file}' generated successfully.")

if __name__ == "__main__":
  main()