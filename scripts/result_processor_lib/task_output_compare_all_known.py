"""
@description
--------------------
Given the result.log, it compares the detected packages with all the manually checked packages (both true and false positives),
and outputs the left packages for further manual checking.
"""
import os
import csv
import re
import sys
from .constants import KNOWN_CLASS_POLLUTION_FOLDER_PATH, PROJECT_ROOT

def check_base_folder():
  if not os.path.exists(KNOWN_CLASS_POLLUTION_FOLDER_PATH):
    print(f"Error: Folder '{KNOWN_CLASS_POLLUTION_FOLDER_PATH}' not found.")
    sys.exit(1)

def parse_result_log(file_path):
  detected_packages = set()
  try:
    with open(file_path, "r") as file:
      for line in file:
        match = re.search(r"INFO - ([\w-]+) - .*/([^/]+?):", line)
        if match:
          detected_packages.add(match.group(1))
  except FileNotFoundError:
    print(f"Error: Result log file '{file_path}' not found.")
    sys.exit(1)
  return detected_packages

def parse_manually_checked_csv(folder_path):
  known_true_positives = set()
  known_false_positives = set()
  all_checked_apps = set()

  try:
    folder_path = os.path.join(PROJECT_ROOT, folder_path)
    if not os.path.exists(folder_path):
      raise FileNotFoundError(f"Folder '{folder_path}' not found.")
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    if not csv_files:
      raise FileNotFoundError("No CSV files found.")
    for csv_file in csv_files:
      csv_path = os.path.join(folder_path, csv_file)
      with open(csv_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
          app = row["Application"]
          all_checked_apps.add(app)
          confirmed = row["Confirmed"]
          if confirmed == "Y":
            known_true_positives.add(app)
          elif confirmed == "N" and app not in known_true_positives:
            known_false_positives.add(app)
  except FileNotFoundError as e:
    print(f"Error: {e}")
    sys.exit(1)
  return known_true_positives, known_false_positives, all_checked_apps

def compare_packages(detected, known_true, known_false):
  true_list = detected.intersection(known_true)
  false_list = detected.intersection(known_false)
  unknown = detected - known_true - known_false
  return sorted(true_list), sorted(false_list), sorted(unknown)

def compare_result(log_file):
  detected = parse_result_log(log_file)
  known_true, known_false, all_checked = parse_manually_checked_csv(KNOWN_CLASS_POLLUTION_FOLDER_PATH)
  
  true_positives, false_positives, unknowns = compare_packages(detected, known_true, known_false)
  newly_appeared = sorted(detected - all_checked)

  print("Known True Positives:")
  for pkg in true_positives:
    print(f"- {pkg}")

  print("\nKnown False Positives:")
  for pkg in false_positives:
    print(f"- {pkg}")

  print("\nNewly Appeared Applications (not in any CSV):")
  for pkg in newly_appeared:
    print(f"- {pkg}")

  print("\nUnknown Packages (for further manual checking):")
  for pkg in unknowns:
    print(f"- {pkg}")