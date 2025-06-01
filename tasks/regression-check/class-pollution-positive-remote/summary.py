# summary.py

import re

input_links_file = "tasks/class-pollution-positive-remote/input/all-positives-class-pollution.txt"
result_log_file = "tasks/class-pollution-positive-remote/logs/result.log"
output_file = "tasks/class-pollution-positive-remote/input/tp-links.txt"

def extract_repo_names(filepath):
  repo_names = set()
  with open(filepath, "r") as f:
    for line in f:
      match = re.search(r"INFO - ([^ ]+) -", line)
      if match:
        repo_names.add(match.group(1))
  return repo_names

def read_links(filepath):
  with open(filepath, "r") as f:
    return [line.strip() for line in f if line.strip()]

def remove_duplicates(links):
  seen = set()
  unique_links = []
  for link in links:
    if link not in seen:
      unique_links.append(link)
      seen.add(link)
  return unique_links

def main():
  repo_names = extract_repo_names(result_log_file)
  links = read_links(input_links_file)
  filtered_links = [
    link for link in links
    if any(repo in link for repo in repo_names)
  ]
  unique_filtered_links = remove_duplicates(filtered_links)
  with open(output_file, "w") as f:
    for link in unique_filtered_links:
      f.write(link + "\n")
  print(f"Filtered links written to {output_file}")

if __name__ == "__main__":
  main()