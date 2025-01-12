import os
import json
import sys

def summarize_results(base_folder):
  """
  Given a base folder, this function:
    - Iterates through each subfolder,
    - Reads the `summary.json` in `results/` if it exists,
    - Checks if `MultiLevelClassPollutionQuery.ql.sarif` > 0,
    - Collects the names of the subfolders that meet the criteria.
  Returns a list of subfolder names.
  """
  flagged_folders = []

  # Iterate over all entries in the base folder
  for entry in os.scandir(base_folder):
    if entry.is_dir():
      # Construct the path to the results/summary.json
      results_folder = os.path.join(entry.path, 'results')
      summary_file = os.path.join(results_folder, 'summary.json')

      # Check if summary.json exists
      if os.path.exists(summary_file):
        with open(summary_file, 'r', encoding='utf-8') as f:
          try:
            data = json.load(f)
          except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {summary_file}")
            continue

        # Check the value of "MultiLevelClassPollutionQuery.ql.sarif"
        if data.get("MultiLevelClassPollutionQuery.ql.sarif", 0) > 0:
          # Record just the folder name (not the full path)
          flagged_folders.append(os.path.basename(entry.path))

  return flagged_folders


if __name__ == "__main__":
  # If you want to pass the base folder as a command-line argument
  # usage: python summarize_results.py /path/to/base_folder
  if len(sys.argv) < 2:
    base_folder = "/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K-r2/output"
  else:
    base_folder = sys.argv[1]

  # Collect subfolder names that have a positive result for MultiLevelClassPollutionQuery.ql.sarif
  result = summarize_results(base_folder)

  # Print or process the result as needed
  if result:
    print(f"Found {len(result)} subfolders with MultiLevelClassPollutionQuery.ql.sarif > 0:")
    for folder_name in result:
      print(f"  - {folder_name}")
  else:
    print("No subfolders found with MultiLevelClassPollutionQuery.ql.sarif > 0.")
