import re
import os

RESULTS = [
  ("Github Top 100", "/home/jackfromeast/Desktop/python-class-pollution/tasks/github-dataset/class-pollution-100-1K-r3-all/logs/result.log", "Github"),
  ("Github Top 1K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/github-dataset/class-pollution-1K-r4/logs/result.log", "Github"),
  ("PIP TOP 10K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-0-60K/logs/result-top10K.log", "Pip"),
  ("PIP 0-60K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-0-60K/logs/result.log", "Pip"),
  ("PIP 60K-90K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-60K-90K/logs/result.log", "Pip"),
  ("PIP 90K-120K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-90K-120K/logs/result.log", "Pip"),
  ("PIP 120K-170K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-120K-170K/logs/result.log", "Pip"),
  ("PIP 170K-220K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-170K-220K/logs/result.log", "Pip"),
  ("PIP 220K-270K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-220K-270K/logs/result.log", "Pip"),
  ("PIP 270K-320K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-270K-320K/logs/result.log", "Pip"),
  ("PIP 320K-370K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-320K-370K/logs/result.log", "Pip"),
  ("PIP 370K-420K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-370K-420K/logs/result.log", "Pip"),
  ("PIP 420K-470K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-420K-470K/logs/result.log", "Pip"),
  ("PIP 470K-520K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-470K-520K/logs/result.log", "Pip"),
  ("PIP 520K-570K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-520K-570K/logs/result.log", "Pip"),
  ("PIP 570K-600K", "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-570K-600K/logs/result.log", "Pip"),
]

CATEGORIES = [
  "set-both-get-both",
  "set-both-get-attr",
  "set-attr-get-both",
  "set-attr-get-attr",
  "set-item-get-both",
  "set-item-get-attr"
]


def load_github_url_map(filepath):
    # Assumes each line is: <github_url>
    url_map = {}
    with open(filepath) as f:
        for line in f:
            url = line.strip()
            if url:
                # Extract repo name (e.g., "owner/repo") from URL
                repo_name = url.split('github.com/')[-1].replace('.git', '').strip('/')
                pkg_name = repo_name.split('/')[-1]
                url_map[pkg_name] = url
    return url_map

def load_pip_pkg_list(filepath):
    # Assumes each line is a package name
    pkgs = set()
    with open(filepath) as f:
        for line in f:
            pkg = line.strip()
            if pkg:
                pkgs.add(pkg)
    return pkgs

def parse_log(filepath):
  pattern = re.compile(
    r" - (?P<package>[\w\-]+) - py/class-polliution/(?P<type>[\w\-]+): (?P<count>\d+) flows detected"
  )
  set_types_order = [
    "set-both-get-both",
    "set-both-get-attr",
    "set-attr-get-both",
    "set-attr-get-attr",
    "set-item-get-both",
    "set-item-get-attr"
  ]
  # For package-level unique counting
  package_set = set()
  flow_alerts = 0
  type_counts = {cat: 0 for cat in CATEGORIES}
  package_to_types = {}
  if not os.path.exists(filepath):
    return None
  with open(filepath, "r") as f:
    for line in f:
      m = pattern.search(line)
      if m:
        pkg = m.group("package")
        pollution_type = m.group("type")
        count = int(m.group("count"))
        package_set.add(pkg)
        flow_alerts += count
        if pollution_type in type_counts:
          # Record all types per package
          if pkg not in package_to_types:
            package_to_types[pkg] = set()
          package_to_types[pkg].add(pollution_type)
  # Now, for each package, select the most expressive type and count
  for pkg, types in package_to_types.items():
    for t in set_types_order:
      if t in types:
        type_counts[t] += 1
        break  # Only count the most expressive type for this package
  result = {
    "Package Alerts": len(package_set),
    "Flow Alerts": flow_alerts,
  }
  result.update(type_counts)

  # Build mapping: primitive -> set(packages)
  primitive_to_packages = {cat: set() for cat in CATEGORIES}
  for pkg, types in package_to_types.items():
    for t in set_types_order:
      if t in types:
        primitive_to_packages[t].add(pkg)
        break
  result['primitive_to_packages'] = primitive_to_packages

  return result

def collect_tp_packages(result):
  if not result or 'primitive_to_packages' not in result:
      return set()
  tp_pkgs = set()
  for pkgs in result['primitive_to_packages'].values():
      tp_pkgs.update(pkgs)
  return tp_pkgs

def load_list(path):
  s = set()
  if os.path.exists(path):
      with open(path) as f:
          for line in f:
              val = line.strip()
              if val:
                  s.add(val)
  return s

# --- File paths ---
github_top1k_log = "/home/jackfromeast/Desktop/python-class-pollution/tasks/github-dataset/class-pollution-1K-r4/logs/result.log"
github_all_log = "/home/jackfromeast/Desktop/python-class-pollution/tasks/github-dataset/class-pollution-100-1K-r3-all/logs/result.log"
pip_top10k_log = "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-0-60K/logs/result-top10K.log"
pip_all_logs = [
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-0-60K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-60K-90K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-90K-120K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-120K-170K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-170K-220K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-220K-270K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-270K-320K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-320K-370K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-370K-420K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-420K-470K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-470K-520K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-520K-570K/logs/result.log",
    "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-570K-600K/logs/result.log",
]

github_top1k_input = "/home/jackfromeast/Desktop/python-class-pollution/tasks/github-dataset/class-pollution-1K-external/input/github-20101001-20241001-stars-1000.txt"
github_all_input = "/home/jackfromeast/Desktop/python-class-pollution/tasks/github-dataset/class-pollution-100-1K-r3-all/input/codeql-class-pollution-100-1K.txt"
pip_all_input = "/home/jackfromeast/Desktop/python-class-pollution/tasks/pip-dataset/class-pollution-pip-r2-0-60K/input/pip_all_packages_download_last_month_03_2025.txt"

github_top1k_url_map = load_github_url_map(github_top1k_input)
github_all_url_map = load_github_url_map(github_all_input)
pip_all_pkgs = load_pip_pkg_list(pip_all_input)

# --- Collect tp packages ---
tp_github_top1k = collect_tp_packages(parse_log(github_top1k_log)) 
tp_github_all = collect_tp_packages(parse_log(github_all_log))
tp_pip_top10k = collect_tp_packages(parse_log(pip_top10k_log))
tp_pip_all = set()
for log_path in pip_all_logs:
    tp_pip_all.update(collect_tp_packages(parse_log(log_path)))

# --- Write input.txt files ---
def write_urls(pkg_set, url_map, out_path):
    with open(out_path, 'w') as f:
        for pkg in sorted(pkg_set):
            url = url_map.get(pkg)
            if not url:
                print(f"Warning: No URL found for package: {pkg}")
                continue
            f.write(url + '\n')

def write_pypi_urls(pkg_set, out_path):
    with open(out_path, 'w') as f:
        for pkg in sorted(pkg_set):
            f.write(f'https://pypi.org/project/{pkg}/\n')

# Github top-1K
write_urls(tp_github_top1k, github_top1k_url_map, 'Github-Top-1K-TP.txt')
# Github all
write_urls(tp_github_all, github_all_url_map, 'Github-All-TP.txt')
# Pip top-10K
write_pypi_urls(tp_pip_top10k, 'Pip-Top-10K-TP.txt')
# Pip all
write_pypi_urls(tp_pip_all, 'Pip-All-TP.txt')