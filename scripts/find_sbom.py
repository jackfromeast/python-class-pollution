import os
import json

# Define the base directory
BASE_DIR = "/home/redacted/Desktop/python-class-pollution/tasks/dependency-check-1K-r1/output"

# Counter for total dependencies analyzed
total_dependencies = 0

def process_sbom(file_path):
  """Reads an sbom.json file and counts the number of components."""
  global total_dependencies
  with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
    if "components" in data:
      total_dependencies += len(data["components"])

def find_sbom_files(base_dir):
  """Finds and processes all sbom.json files."""
  for root, _, files in os.walk(base_dir):
    for file in files:
      if file == "sbom.json":
        process_sbom(os.path.join(root, file))

# Start processing
find_sbom_files(BASE_DIR)

# Print the total count
print(f"Total dependencies analyzed: {total_dependencies}")
