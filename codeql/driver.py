"""
@description
---------------------
This module helps to run the codeql queries on the codebase.

@usage
---------------------
1/ Build the codeql database given the codebase path.
   It will generate the codeql database named `codeql-db` in the same codebase path.

```python driver.py --build-db --codebase-path <path-to-codebase>```

"""
import os
import subprocess
import argparse

def build_codeql_database(codebase_path):
  """
  Builds the CodeQL database for the given codebase path.

  Args:
    codebase_path (str): Path to the codebase.
  """
  if not os.path.exists(codebase_path):
    raise FileNotFoundError(f"The specified codebase path does not exist: {codebase_path}")

  codeql_db_path = os.path.join(codebase_path, "../codeql-db")
  
  try:
    print(f"Building CodeQL database at: {codeql_db_path}")
    subprocess.run(
      [
        "codeql", "database", "create", codeql_db_path, 
        "--source-root", codebase_path,
        "--language", "python"
      ],
      check=True
    )
    print(f"CodeQL database created successfully at {codeql_db_path}")
  except subprocess.CalledProcessError as e:
    raise Exception(f"Failed to create CodeQL database: {e}")

def main():
  """
  Main function to parse arguments and trigger CodeQL database build.
  """
  parser = argparse.ArgumentParser(description="Run CodeQL queries on a codebase.")
  parser.add_argument(
    "--build-db", 
    action="store_true", 
    help="Build the CodeQL database for the given codebase."
  )
  parser.add_argument(
    "--codebase-path", 
    type=str, 
    required=True, 
    help="Path to the codebase."
  )
  
  args = parser.parse_args()

  if args.build_db:
    build_codeql_database(args.codebase_path)

if __name__ == "__main__":
  main()
