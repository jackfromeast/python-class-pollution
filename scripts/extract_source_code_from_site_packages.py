"""
@description
--------------------
Move the source code of packages from python virtual environment's site-packages to a new directory.
"""

import os
import shutil
import argparse

def extract_and_move_source_folders(source_path, destination_path):
  if not os.path.exists(destination_path):
    os.makedirs(destination_path)

  for item in os.listdir(source_path):
    item_path = os.path.join(source_path, item)

    if os.path.isdir(item_path) and not item.endswith(('.dist-info', '.pth')):
      print(f"Moving folder: {item}")
      try:
        shutil.move(item_path, os.path.join(destination_path, item))
      except Exception as e:
        print(f"Error moving folder {item}: {e}")
    else:
      print(f"Skipping non-source folder or file: {item}")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Move source code folders from site-packages to a specified directory.")
  parser.add_argument("--source", required=True, help="Path to the source site-packages folder.")
  parser.add_argument("--dest", required=True, help="Path to the destination folder.")

  args = parser.parse_args()

  extract_and_move_source_folders(args.source, args.dest)