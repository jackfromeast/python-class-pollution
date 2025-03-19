import os
import yaml
from collections import defaultdict

BASE_DIR = "/home/jackfromeast/Desktop/python-class-pollution/codeql-query/library-models"

model_counts = defaultdict(int)

def process_yaml(file_path):
  """Reads a YAML file and updates the model counts."""
  with open(file_path, "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)
    
    if "extensions" in data:
      for extension in data["extensions"]:
        if "addsTo" in extension and "extensible" in extension["addsTo"]:
          model_type = extension["addsTo"]["extensible"]
          model_counts[model_type] += 1

def find_yaml_files(base_dir):
  """Recursively finds all data_extension.yml files."""
  for root, _, files in os.walk(base_dir):
    if "latest" in root:
      for file in files:
        if file == "data_extension.yaml":
          process_yaml(os.path.join(root, file))


find_yaml_files(BASE_DIR)

print("Model Counts:")
for model, count in model_counts.items():
  print(f"{model}: {count}")
