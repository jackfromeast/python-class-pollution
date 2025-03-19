import os
import shutil
import json

def clean_folders(input_path):
  """
  Cleans the given input folder by removing subfolders
  that do not contain a 'results' folder or if all values
  in 'results/summary.json' are 0.

  Parameters:
    input_path (str): The path to the input folder.
  """
  if not os.path.exists(input_path):
    print(f"Error: The path '{input_path}' does not exist.")
    return

  if not os.path.isdir(input_path):
    print(f"Error: The path '{input_path}' is not a folder.")
    return

  for subfolder in os.listdir(input_path):
    subfolder_path = os.path.join(input_path, subfolder)
    # Check if it's a directory
    if os.path.isdir(subfolder_path):
      # Check for 'results' folder
      results_path = os.path.join(subfolder_path, 'results')
      if not os.path.exists(results_path):
        # Delete the folder if 'results' folder is missing
        print(f"Deleting folder: {subfolder_path}")
        shutil.rmtree(subfolder_path)
      else:
        # Check the contents of 'results/summary.json'
        summary_json_path = os.path.join(results_path, 'summary.json')
        if os.path.exists(summary_json_path):
          with open(summary_json_path, 'r') as f:
            summary_data = json.load(f)
            # Check if all values in the summary are 0
            if all(value == 0 for value in summary_data.values()):
              print(f"All values in 'summary.json' are 0. Deleting folder: {subfolder_path}")
              shutil.rmtree(subfolder_path)
            else:
              print(f"'results' folder and valid 'summary.json' found in: {subfolder_path}, skipping deletion.")
        else:
          try:
            shutil.rmtree(subfolder_path)
            print(f"'results' folder found but 'summary.json' is missing in: {subfolder_path}. Deleting folder.")
          except OSError:
            print(f"Error: Could not delete folder '{subfolder_path}'.")
    else:
      print(f"Skipping non-directory item: {subfolder_path}")

if __name__ == "__main__":
  input_path = input("Enter the path to the folder: ").strip()
  clean_folders(input_path)