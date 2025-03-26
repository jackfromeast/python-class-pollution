"""
@description
--------------------
Given the input.txt and result.log, it compares them and prints the missing packages.
"""
import re
import sys
import os

# Default file paths
PROJECT_ROOT = os.path.join(__file__, "..")
DEFAULT_RESULT_LOG_FILE = "tasks/codeql-class-pollution-all-known/logs/result.log"
DEFAULT_INPUT_FILE = "tasks/codeql-class-pollution-all-known/input/all-known-class-pollution.txt"

def check_cwd():
    """Check if the current working directory is named 'python-class-pollution'."""
    cwd = os.getcwd()
    if not cwd.endswith("python-class-pollution"):
        raise ValueError("The current working directory must be named 'python-class-pollution'.")

def extract_package_name(url):
    """Extract package name from PyPI and GitHub URLs."""
    # Match PyPI package URLs
    pypi_match = re.search(r"https://pypi\.org/project/([^/]+)", url)
    if pypi_match:
        return pypi_match.group(1)

    # Match GitHub repository names
    github_match = re.search(r"https://github\.com/[^/]+/([^/]+)", url)
    if github_match:
        return github_match.group(1)

    return None

def parse_result_log(file_path):
    """Extract package names and their detected counts from result.log."""
    detected_packages = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                match = re.search(r"INFO - ([\w\-\d]+) - MultiLevelClassPollutionQueryNew\.ql\.sarif: (\d+) flows detected", line)
                if match:
                    package_name = match.group(1)
                    flow_count = int(match.group(2))
                    detected_packages[package_name] = flow_count
    except FileNotFoundError:
        print(f"Error: Result log file '{file_path}' not found.")
        sys.exit(1)
    return detected_packages

def parse_input_file(file_path):
    """Extract package names from input.txt."""
    input_packages = set()
    try:
        with open(file_path, "r") as file:
            for line in file:
                package_name = extract_package_name(line.strip())
                if package_name:
                    input_packages.add(package_name)
    except FileNotFoundError:
        print(f"Error: Input file '{file_path}' not found.")
        sys.exit(1)
    return input_packages

if __name__ == "__main__":
    # Check if the current working directory is correct
    check_cwd()

    # Get the absolute paths for the input and result log files
    result_log_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT_ROOT, DEFAULT_RESULT_LOG_FILE)
    input_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJECT_ROOT, DEFAULT_INPUT_FILE)

    # Parse the result log and input file
    detected_packages = parse_result_log(result_log_file)
    input_packages = parse_input_file(input_file)

    # Find missing packages
    missing_packages = input_packages - detected_packages.keys()

    # Print the missing packages
    print(f"Missing packages ({len(missing_packages)} total):")
    for package in sorted(missing_packages):
        print(f"- {package}")