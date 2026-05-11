import os
import re

# New config: single result log and four filter files
RESULT_LOG = "/home/jackfromeast/Desktop/python-class-pollution/tasks/research-questions/all-tp-external/logs/result.log"
GROUPS = [
    ("Github All", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Github-All-TP.txt"),
    ("Github Top 1K", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Github-Top-1K-TP.txt"),
    ("Pip All", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Pip-All-TP.txt"),
    ("Pip Top 10K", "/home/jackfromeast/Desktop/python-class-pollution/dataset/all-alerts/Pip-Top-10K-TP.txt"),
]

CATEGORIES = [
  "set-both-get-both",
  "set-both-get-attr",
  "set-attr-get-both",
  "set-attr-get-attr",
  "set-item-get-both",
  "set-item-get-attr"
]

def parse_log_per_package(filepath):
    # Parse the log, return dict: package -> {type: set of types, flows: {type: count}}
    pattern = re.compile(
        r" - (?P<package>[\w\-]+) - py/class-polliution-external/(?P<type>[\w\-]+): (?P<count>\d+) flows detected"
    )
    set_types_order = [
        "set-both-get-both",
        "set-both-get-attr",
        "set-attr-get-both",
        "set-attr-get-attr",
        "set-item-get-both",
        "set-item-get-attr"
    ]
    package_to_types = {}
    package_to_flows = {}
    if not os.path.exists(filepath):
        return {}, {}
    with open(filepath, "r") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                pkg = m.group("package")
                pollution_type = m.group("type")
                count = int(m.group("count"))
                if pkg not in package_to_types:
                    package_to_types[pkg] = set()
                package_to_types[pkg].add(pollution_type)
                if pkg not in package_to_flows:
                    package_to_flows[pkg] = {}
                package_to_flows[pkg][pollution_type] = package_to_flows[pkg].get(pollution_type, 0) + count
    return package_to_types, package_to_flows

def collect_tp_packages(result):
  if not result or 'primitive_to_packages' not in result:
      return set()
  tp_pkgs = set()
  for pkgs in result['primitive_to_packages'].values():
      tp_pkgs.update(pkgs)
  return tp_pkgs

def load_list(path):
    # Accepts either package names or URLs, returns set of base names
    s = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                val = line.strip()
                if val:
                    # If it's a URL, extract the last part
                    if val.startswith("https://github.com/"):
                        name = val.split('/')[-1].replace('.git','')
                        s.add(name)
                    elif val.startswith("https://pypi.org/project/"):
                        name = val.split('/')[-2] if val.endswith('/') else val.split('/')[-1]
                        s.add(name)
                    else:
                        s.add(val)
    return s

def compute_stats(filtered_types, filtered_flows):
    set_types_order = [
        "set-both-get-both",
        "set-both-get-attr",
        "set-attr-get-both",
        "set-attr-get-attr",
        "set-item-get-both",
        "set-item-get-attr"
    ]
    # Package Alerts: number of unique packages
    package_alerts = len(filtered_types)
    # Flow Alerts: sum of all flow counts for all types
    flow_alerts = sum(
        sum(type_counts.values()) for type_counts in filtered_flows.values()
    )
    # For each package, select the most expressive type
    type_counts = {cat: 0 for cat in CATEGORIES}
    for pkg, types in filtered_types.items():
        for t in set_types_order:
            if t in types:
                type_counts[t] += 1
                break
    result = {
        "Package Alerts": package_alerts,
        "Flow Alerts": flow_alerts,
    }
    result.update(type_counts)
    return result


def main():
    headers = ["Dataset", "Package Alerts", "Flow Alerts"] + CATEGORIES
    col_widths = [max(len(h), 16) for h in headers]

    # Parse the result log once for all packages
    package_to_types, package_to_flows = parse_log_per_package(RESULT_LOG)

    # For each group, load the filter file and compute stats
    all_rows = []
    group_stats = []
    for label, filter_path in GROUPS:
        pkg_set = load_list(filter_path)
        # Only consider packages that are in pkg_set
        filtered_types = {pkg: types for pkg, types in package_to_types.items() if pkg in pkg_set}
        filtered_flows = {pkg: flows for pkg, flows in package_to_flows.items() if pkg in pkg_set}
        # Compute stats
        row_stats = compute_stats(filtered_types, filtered_flows)
        row = [label] + [str(row_stats.get(col, "-")) for col in headers[1:]]
        all_rows.append(row)
        group_stats.append(row_stats)
        for j, cell in enumerate(row):
            col_widths[j] = max(col_widths[j], len(str(cell)))

    header_str = ""
    for i, h in enumerate(headers):
        header_str += h.ljust(col_widths[i]) + ("  " if i < len(headers) - 1 else "")
    print(header_str)
    print("=" * len(header_str))
    for row in all_rows:
        row_str = ""
        for i, cell in enumerate(row):
            row_str += str(cell).ljust(col_widths[i]) + ("  " if i < len(row) - 1 else "")
        print(row_str)

    print_latex_table(all_rows, headers)
    print_latex_table_columnar(group_stats, [row[0] for row in all_rows], headers[1:])


def print_latex_table(summary_rows, headers):
    # summary_rows: list of lists, as already printed
    # headers: list of column names

    # Find relevant rows for new groupings
    github_all = None
    github_top1k = None
    pip_all = None
    pip_top10k = None
    for r in summary_rows:
        if r[0] == "Github All":
            github_all = r
        elif r[0] == "Github Top 1K":
            github_top1k = r
        elif r[0] == "Pip All":
            pip_all = r
        elif r[0] == "Pip Top 10K":
            pip_top10k = r

    # Indices for each primitive
    idx_set_both_get_both = headers.index("set-both-get-both")
    idx_set_both_get_attr = headers.index("set-both-get-attr")
    idx_set_attr_get_both = headers.index("set-attr-get-both")
    idx_set_attr_get_attr = headers.index("set-attr-get-attr")
    idx_set_item_get_both = headers.index("set-item-get-both")
    idx_set_item_get_attr = headers.index("set-item-get-attr")

    def sum_int(a, b):
        try:
            return int(a) + int(b)
        except:
            return "-"

    def sum_checked(a, b):
        try:
            return str(int(a) + int(b))
        except:
            return "-"

    print(r"\begin{table}[!t]")
    print(r"\centering")
    print(r"\scriptsize")
    print(r"\caption{[RQ2] A breakdown of zero-day vulnerabilities found by \sys.}")
    print(r"\label{table:zero-day-breakdown}")
    print(r"\begin{tabular}{lrrrrr}")
    print(r"\toprule")
    print(r"& \#Reported & \#Checked & TP & FP \\")
    print(r"\midrule")
    # Total
    total_reported = sum_int(github_all[1], pip_all[1])
    total_checked = sum_checked(github_top1k[1], pip_top10k[1])
    print("\\textbf{Total}" + r" & {} & {} &  &  \\".format(total_reported, total_checked))
    print(r"\midrule")
    print(r"\emph{Input type breakdown} & & & & \\")
    print(r"\midrule")
    print(r"Remote Input &  &  &  &  \\")
    print(r"Local Input &  &  &  &  \\")
    print(r"Package-level Input &  &  &  &  \\")
    print(r"\midrule")
    print(r"\emph{Pollution Primitive breakdown} & & & & \\")
    print(r"\midrule")
    # Primitives
    primitives = [
        ("Agnostic-Get$\\times$Dual-Set", idx_set_both_get_both),
        ("Constrained-Get$\\times$Dual-Set", idx_set_both_get_attr),
        ("Agnostic-Get$\\times$Attr-Set", idx_set_attr_get_both),
        ("Constrained-Get$\\times$Attr-Set", idx_set_attr_get_attr),
        ("Agnostic-Get$\\times$Item-Set", idx_set_item_get_both),
        ("Constrained-Get$\\times$Item-Set", idx_set_item_get_attr),
    ]
    for name, idx in primitives:
        reported = sum_int(github_all[idx], pip_all[idx])
        checked = sum_checked(github_top1k[idx], pip_top10k[idx])
        print(f"{name} & {reported} & {checked} &  &  \\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")


def print_latex_table_columnar(stats_per_group, group_labels, metrics):
    # Print LaTeX table with metrics as rows and group_labels as columns
    print(r"\begin{table}[!t]")
    print(r"\centering")
    print(r"\scriptsize")
    print(r"\caption{[RQ2] A breakdown of zero-day vulnerabilities found by \sys.}")
    print(r"\label{table:zero-day-breakdown}")
    col_spec = 'l' + 'r'*len(group_labels)
    print(rf"\\begin{{tabular}}{{{col_spec}}}")
    print(r"\toprule")
    print("Metric", end='')
    for label in group_labels:
        print(f" & {label}", end='')
    print(r" \\")

    print(r"\midrule")
    for metric in metrics:
        print(metric, end='')
        for i in range(len(group_labels)):
            val = stats_per_group[i].get(metric, '-')
            print(f" & {val}", end='')
        print(r" \\")

    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(r"\end{table}")


if __name__ == "__main__":
  main()