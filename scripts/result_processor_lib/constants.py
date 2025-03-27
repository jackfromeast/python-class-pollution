"""
@description
--------------------
This file contains the constants used in the result processor.
"""
import os

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", ".." )

# Metadata files for the repositories
METADATA_PATH = [
  "dataset/github/python-20100101-20141001-star-1K.json",
  "dataset/github/python-20141001-20241001-star-100-1K.json",
  "dataset/github/python-20191001-20241001-star-1K.json"
]

# Path to all the manually checked CSV files
KNOWN_CLASS_POLLUTION_FOLDER_PATH = "dataset/manually-checked"

# Path the all_true_positives 
TRUE_POSITIVES_FILE_PATH = "dataset/manually-checked/The Python World-Class Pollution - All-in-one-0326.csv"

# Result CSV columns
CSV_COLUMNS = ["Application", "Stars", "URL", "Confirmed", "CodeQL", "FP Reason", "GetType", "SetType", "Input", "Remote", "Local", "Status", "Comment", "NewlyAdded"]
HEADER_ROWS = """Application,Stars,URL,Confirmed,Codeql,FP Reason,Types,,Input,,,Status,Comment
,,,,,,Get,Set,,Remote,Local,,
"""