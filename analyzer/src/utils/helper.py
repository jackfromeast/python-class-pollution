import os
import shutil
import psutil
import subprocess

def resolve_repo_name(repo_url):
  """
  Extracts the repository or package name from a URL.

  @param repo_url: The URL of the repository or package.
  e.g.,
  - https://pypi.org/project/laboneq/2.44.0/
  - https://pypi.org/project/laboneq
  - https://github.com/xxx/laboneq.git
  - https://github.com/xxx/laboneq
  @return: The repository or package name.
  """
  repo_url = repo_url.rstrip("/")

  # Handle GitHub URLs
  if "github.com" in repo_url:
    if repo_url.endswith(".git"):
      return repo_url.split("/")[-1].replace(".git", "")
    return repo_url.split("/")[-1]

  # Handle PyPI URLs
  elif "pypi.org" in repo_url:
    # Split the URL by "/" and get the second-to-last part (project name)
    parts = repo_url.split("/")
    if len(parts) >= 5 and parts[-2] == "project":
      return parts[-1]
    elif len(parts) >= 5 and parts[-3] == "project":
      return parts[-2]
    else:
      raise ValueError(f"Invalid PyPI URL: {repo_url}")

  # Handle other URLs
  else:
    raise ValueError(f"Unsupported URL: {repo_url}")

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

  
def terminate_process(pid):
  """
  Kill all processes spawned from the given process ID.
  """
  try:
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.terminate()
    psutil.wait_procs(children, timeout=5)
    parent.terminate()
  except psutil.NoSuchProcess:
    pass
  except Exception as e:
    pass