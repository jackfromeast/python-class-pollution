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

# Path to the manually checked CSV file
KNOWN_CLASS_POLLUTION_FOLDER_PATH = "dataset/manually-checked"

def check_base_folder():
  """Check if the base folder exists and contains the required files/folders."""
  if not os.path.exists(KNOWN_CLASS_POLLUTION_FOLDER_PATH):
    print(f"Error: Folder '{KNOWN_CLASS_POLLUTION_FOLDER_PATH}' not found in the base directory.")
    sys.exit(1)

def parse_result_log(file_path):
  """Extract package names from result.log."""
  detected_packages = set()
  try:
    with open(file_path, "r") as file:
      for line in file:
        match = re.search(r"INFO - ([\w\-\d]+) - .*\.ql\.sarif:", line)
        if match:
          package_name = match.group(1)
          detected_packages.add(package_name)
  except FileNotFoundError:
    print(f"Error: Result log file '{file_path}' not found.")
    sys.exit(1)
  return detected_packages

def parse_manually_checked_csv(folder_path):
  """Extract known true positives and false positives from all CSV files in the folder."""
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
    print(f"Error: {e}")
    sys.exit(1)

  return known_true_positives, known_false_positives

def compare_packages(detected_packages, known_true_positives, known_false_positives):
  """Compare detected packages with known true/false positives and find unknowns."""
  known_true_positive_list = detected_packages.intersection(known_true_positives)
  known_false_positive_list = detected_packages.intersection(known_false_positives)
  unknown_list = detected_packages - known_true_positives - known_false_positives

  return sorted(known_true_positive_list), sorted(known_false_positive_list), sorted(unknown_list)

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python script.py <result_log_file>")
    sys.exit(1)

  check_base_folder()

  result_log_file = sys.argv[1]
  if not os.path.isabs(result_log_file):
    result_log_file = os.path.join(os.getcwd(), result_log_file)

  detected_packages = parse_result_log(result_log_file)

  known_true_positives, known_false_positives = parse_manually_checked_csv(KNOWN_CLASS_POLLUTION_FOLDER_PATH)

  known_true_positive_list, known_false_positive_list, unknown_list = compare_packages(
    detected_packages, known_true_positives, known_false_positives
  )

  print("Known True Positives:")
  for package in known_true_positive_list:
    print(f"- {package}")

  print("\nKnown False Positives:")
  for package in known_false_positive_list:
    print(f"- {package}")

  print("\nUnknown Packages (for further manual checking):")
  for package in unknown_list:
    print(f"- {package}")