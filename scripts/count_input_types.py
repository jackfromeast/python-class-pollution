import os
import json
from collections import defaultdict

# Config
OUTPUT_DIR = "/home/jackfromeast/Desktop/python-class-pollution/tasks/research-questions/all-tp-external/output"
GROUPS = [
    ("Github All", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Github-All-TP.txt"),
    ("Github Top 1K", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Github-Top-1K-TP.txt"),
    ("Pip All", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Pip-All-TP.txt"),
    ("Pip Top 10K", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Pip-Top-10K-TP.txt"),
]
INPUT_TYPES = ["Library", "Remote", "Local"]


def load_list(path):
    s = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                val = line.strip()
                if val:
                    if val.startswith("https://github.com/"):
                        name = val.split("/")[-1].replace(".git", "")
                        s.add(name)
                    elif val.startswith("https://pypi.org/project/"):
                        name = val.split("/")[-2] if val.endswith("/") else val.split("/")[-1]
                        s.add(name)
                    else:
                        s.add(val)
    return s


def count_input_types(details):
    counts = {k: 0 for k in INPUT_TYPES}
    for entry in details:
        # Split by newline to handle multiple inputs in one string
        for line in entry.split('\n'):
            line = line.strip()
            for t in INPUT_TYPES:
                if line.startswith(f"External Input:{t}"):
                    counts[t] += 1
                    break
    return counts


def main():
    # Load group filter sets
    group_sets = [load_list(fpath) for _, fpath in GROUPS]
    # For each group, count number of repos by input type with priority: Remote > Local > Library
    group_type_repo_counts = [defaultdict(int) for _ in GROUPS]  # type -> repo count
    group_repo_counts = [0 for _ in GROUPS]  # total repos in group

    PRIORITY = ["Remote", "Local", "Library"]

    for repo in os.listdir(OUTPUT_DIR):
        repo_dir = os.path.join(OUTPUT_DIR, repo)
        summary_path = os.path.join(repo_dir, "results/summary.json")
        if not os.path.isfile(summary_path):
            continue
        try:
            with open(summary_path) as f:
                data = json.load(f)
            details = data.get("details", [])
        except Exception as e:
            print(f"Warning: Could not parse {summary_path}: {e}")
            continue
        input_counts = count_input_types(details)
        # Determine highest-priority input type for this repo
        repo_type = None
        for t in PRIORITY:
            if input_counts[t] > 0:
                repo_type = t
                break
        # Map repo to groups
        if repo_type:
            for i, group_set in enumerate(group_sets):
                if repo in group_set:
                    group_repo_counts[i] += 1
                    group_type_repo_counts[i][repo_type] += 1

    # Output summary table
    headers = ["Group", "#Repos"] + [f"#ReposWith:{t}" for t in INPUT_TYPES]
    print("\t".join(headers))
    for i, (gname, _) in enumerate(GROUPS):
        row = [gname, str(group_repo_counts[i])] + [str(group_type_repo_counts[i][t]) for t in INPUT_TYPES]
        print("\t".join(row))

    # Output LaTeX table (metrics as rows, groups as columns)
    print("\nLaTeX Table:")
    group_labels = [g[0] for g in GROUPS]
    metrics = ["#Repos"] + [f"#ReposWith:{t}" for t in INPUT_TYPES]
    print(r"\\begin{table}[!t]")
    print(r"\\centering")
    print(r"\\scriptsize")
    print(r"\\caption{[RQ1] Number of repos with at least one input type, by group.}")
    print(r"\\label{table:input-type-counts}")
    col_spec = 'l' + 'r'*len(group_labels)
    print(rf"\\begin{{tabular}}{{{col_spec}}}")
    print(r"\\toprule")
    print("Metric", end='')
    for label in group_labels:
        print(f" & {label}", end='')
    print(r" \\")
    print(r"\\midrule")
    for j, metric in enumerate(metrics):
        print(metric, end='')
        for i in range(len(group_labels)):
            val = group_repo_counts[i] if j == 0 else group_type_repo_counts[i][INPUT_TYPES[j-1]]
            print(f" & {val}", end='')
        print(r" \\")
    print(r"\\bottomrule")
    print(r"\\end{tabular}")
    print(r"\\end{table}")

if __name__ == "__main__":
    main()
