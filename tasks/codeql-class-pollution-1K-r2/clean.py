import os
import shutil

def clean_folders(input_path):
  """
  Cleans the given input folder by removing subfolders
  that do not contain a 'results' folder.

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
        print(f"'results' folder found in: {subfolder_path}, skipping deletion.")
    else:
      print(f"Skipping non-directory item: {subfolder_path}")

if __name__ == "__main__":
  input_path = input("Enter the path to the folder: ").strip()
  clean_folders(input_path)
