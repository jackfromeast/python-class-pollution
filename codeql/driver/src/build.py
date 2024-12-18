"""
@description
---------------------
This module helps to build the codeql database on the codebase.

@usage
---------------------
1/ Build the codeql database given the codebase path.
   It will generate the codeql database named `codeql-db` in the same codebase path.

```python build.py --codebase-path <path-to-codebase>```

"""
import os
import subprocess
import argparse
import logging

logging.basicConfig(level=logging.INFO)

def build_codeql_database(codebase_path, codeql_db_path="codeql-db"):
  """
  Builds the CodeQL database for the given codebase path.

  Args:
    codebase_path (str): Path to the codebase.
  """
  if not os.path.exists(codebase_path):
    raise FileNotFoundError(f"The specified codebase path does not exist: {codebase_path}")
  
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
  parser = argparse.ArgumentParser(description="Build CodeQL database on a codebase.")
  parser.add_argument(
    "--codebase-path", 
    type=str, 
    required=True, 
    help="Path to the codebase."
  )
  parser.add_argument(
    "--database-path", 
    type=str, 
    required=False, 
    help="Path to the codebase."
  )
  
  args = parser.parse_args()
  
  if not args.database_path:
    args.database_path = os.path.join(args.codebase_path, "../codeql-db")

  build_codeql_database(args.codebase_path, args.database_path)

if __name__ == "__main__":
  main()
