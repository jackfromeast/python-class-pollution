import os
import json
import sys
import argparse

metadata_files = [
    "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20100101-20141001-star-1K.json",
    "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20141001-20241001-star-100-1K.json",
    "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20191001-20241001-star-1K.json"
]

def summarize_results(base_folder, load_meta=False, metadata_files=None):
    """
    Given a base folder and optional metadata files:
    - Iterates through each subfolder,
    - Reads the `summary.json` in `results/` if it exists,
    - Checks if `MultiLevelClassPollutionQuery.ql.sarif` > 0,
    - Collects the names of the subfolders that meet the criteria,
    - Optionally maps these names to metadata from the given JSON files.
    Returns formatted rows for flagged repositories.
    """
    flagged_folders = []

    # Iterate over all entries in the base folder
    for entry in os.scandir(base_folder):
        if entry.is_dir():
            # Construct the path to the results/summary.json
            results_folder = os.path.join(entry.path, 'results')
            summary_file = os.path.join(results_folder, 'summary.json')

            # Check if summary.json exists
            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from {summary_file}")
                        continue

                if data.get("MultiLevelClassPollutionQuery.ql.sarif", 0) > 0:
                    flagged_folders.append(os.path.basename(entry.path))

    # If metadata loading is disabled, only return repo names and count
    if not load_meta:
        return [f"- {name}" for i, name in enumerate(flagged_folders)]

    # Load metadata and map to flagged folders
    repo_metadata = load_metadata(metadata_files) if metadata_files else {}
    results = []

    for folder_name in flagged_folders:
        if folder_name in repo_metadata:
            repo_info = repo_metadata[folder_name]
            results.append(f"{repo_info['name']}, {repo_info['stargazers_count']}, {repo_info['html_url']}")
        else:
            results.append(f"{folder_name} (Metadata not found)")

    return results

def load_metadata(metadata_files):
    """
    Loads repository metadata from the given JSON files.
    Returns a dictionary mapping folder names to repository information.
    """
    repo_metadata = {}

    for file in metadata_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                for repo in metadata:
                    repo_metadata[repo["name"]] = {
                        "name": repo["name"],
                        "stargazers_count": repo.get("stargazers_count", 0),
                        "html_url": repo.get("html_url", "")
                    }
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not process {file}: {e}")
    
    return repo_metadata

if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Summarize flagged repositories.")
    parser.add_argument("base_folder", help="Base folder to analyze")
    parser.add_argument("--meta", action="store_true", help="Include metadata in the output")

    args = parser.parse_args()

    # Run the summarization
    result = summarize_results(args.base_folder, load_meta=args.meta, metadata_files=metadata_files if args.meta else None)

    # Print results
    if result:
        print(f"Flagged {len(result)} repositories in total:")
        for row in result:
            print(row)
    else:
        print("No repositories flagged.")
