import os
import json
import sys
import argparse
import csv

metadata_files = [
    "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20100101-20141001-star-1K.json",
    "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20141001-20241001-star-100-1K.json",
    "/home/jackfromeast/Desktop/Blurt/crawler/output/python-20191001-20241001-star-1K.json"
]

downloads_file = "/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-pip-1M/input/pip_10K_downloads_past_year.csv"

def load_metadata(metadata_files):
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

def load_downloads(downloads_file):
    downloads_data = {}
    try:
        with open(downloads_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                project_name = row["project_name"].strip()
                num_downloads = int(row["num_downloads"].strip())
                downloads_data[project_name] = num_downloads
    except (FileNotFoundError, ValueError) as e:
        print(f"Warning: Could not process downloads file {downloads_file}: {e}")

    return downloads_data

def summarize_results(base_folder, load_meta=False, metadata_files=None, downloads_file=None):
    flagged_folders = []

    for entry in os.scandir(base_folder):
        if entry.is_dir():
            results_folder = os.path.join(entry.path, 'results')
            summary_file = os.path.join(results_folder, 'summary.json')

            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from {summary_file}")
                        continue

                if data.get("MultiLevelClassPollutionQuery.ql.sarif", 0) > 0:
                    flagged_folders.append(os.path.basename(entry.path))

    if not load_meta:
        return [f"{name}" for name in flagged_folders]

    repo_metadata = load_metadata(metadata_files) if metadata_files else {}
    downloads_data = load_downloads(downloads_file) if downloads_file else {}
    results = []

    for folder_name in flagged_folders:
        repo_info = repo_metadata.get(folder_name, {
            "name": folder_name,
            "stargazers_count": -1,
            "html_url": f"https://pypi.org/project/{folder_name}"
        })
        repo_info["num_downloads"] = downloads_data.get(folder_name, -1)
        results.append(repo_info)

    sorted_results = sorted(results, key=lambda x: (x["stargazers_count"], x["num_downloads"]), reverse=True)

    formatted_results = [
        f"{repo['name']}, {repo['stargazers_count']}, {repo['num_downloads']}, {repo['html_url']}" for repo in sorted_results
    ]

    return formatted_results

def guess_input_test_path(base_folder):
    input_folder = os.path.join(base_folder, "..", "input")
    if os.path.exists(input_folder):
        txt_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".txt")]
        if txt_files:
            return txt_files[0]  # Return the first found .txt file
    print(f"Warning: No input test file found in {input_folder}")
    return None

def get_repo_name(url):
    return url.split("/")[-1].replace(".git", "")

def compare_with_input_test(flagged_folders, input_test_path):
    if not os.path.exists(input_test_path):
        print(f"Error: Input test file '{input_test_path}' does not exist.")
        return []

    with open(input_test_path, 'r', encoding='utf-8') as f:
        input_lines = [line.strip() for line in f if line.strip()]

    all_test_repos = [get_repo_name(line) for line in input_lines]

    test_set = set(all_test_repos)
    flagged_set = set(flagged_folders)
    failed_cases = test_set - flagged_set

    if failed_cases:
        print(f"Failed {len(failed_cases)} cases:")
        for case in failed_cases:
            print(f"- {case}")
    else:
        print("All flagged cases match the input test.")

    return failed_cases

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize flagged repositories.")
    parser.add_argument("base_folder", help="Base folder to analyze")
    parser.add_argument("--meta", action="store_true", help="Include metadata in the output")
    parser.add_argument("--test", action="store_true", help="Show the failed cases by comparing with an input test file")
    parser.add_argument("--input-file", help="Input test file for comparison")

    args = parser.parse_args()

    result = summarize_results(
        args.base_folder,
        load_meta=args.meta,
        metadata_files=metadata_files if args.meta else None,
        downloads_file=downloads_file if args.meta else None
    )

    if result:
        print(f"Flagged {len(result)} repositories in total:")
        for case in result:
            print(f"{case}")

    if args.test:
        input_test_path = args.input_file if args.input_file else guess_input_test_path(args.base_folder)
        flagged_folders = [line.split(',')[0].strip() for line in result]
        compare_with_input_test(flagged_folders, input_test_path)
