import os
import shutil
import subprocess

def resolve_repo_name(repo_url):
  if repo_url.endswith(".git"):
    return repo_url.split("/")[-1].replace(".git", "")
  return repo_url.split("/")[-1]

def cleanup_folders(folder_path):
  if os.path.exists(folder_path):
    try:
      subprocess.run(['rm', '-rf', folder_path], check=True)
    except subprocess.CalledProcessError as e:
      print(f"Error deleting {folder_path}: {e}")
    except Exception as e:
      print(f"Unexpected error deleting {folder_path}: {e}")

def cleanup_folders(folder_path):
    """Removes a directory."""
    if os.path.exists(folder_path):
      shutil.rmtree(folder_path)