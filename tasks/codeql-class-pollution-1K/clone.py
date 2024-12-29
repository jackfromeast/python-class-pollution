""" This script clones the codeql-class-pollution-1K repository

    Date: 12/7/2024
"""
from math import e
import subprocess
import yaml
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
import logging
import os

class cloner:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config(config_path)
        self.work_space = self.config["SCHEDULER"]["WORKSPACE"]
        self.max_workers = self.config["SCHEDULER"]["MAX_WORKER"]
        self.repo_urls = self.get_repo_urls()

    def load_config(self, config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    """ 
        This function checks if the repo has potential true positives.
        If the repo name has already existed in the work space, which
        means it has true positive class polution traces, it will be cloned.
    """
    def repo_url_filter(self, repo_url):
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        if repo_name in os.listdir(self.work_space):
            return True
        else:
            return False
        
    def get_repo_urls(self):
        repo_urls = []
        with open(self.config["SCHEDULER"]["REPO_URL_LIST"], "r") as f:
            for line in f:
                if self.repo_url_filter(line.strip()):
                    repo_urls.append(line.strip())
        return repo_urls

    def worker(self, repo_url):
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_save_path = os.path.join(self.work_space, repo_name, "repo")
        try:
            os.makedirs(repo_save_path, exist_ok=True)
            subprocess.run(["git", "clone", repo_url, repo_save_path], timeout=300)
            logging.info(f"Cloned {repo_url} to {repo_save_path}")
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout: {repo_url}")
        except Exception as e:
            logging.error(f"Unknown Error: {repo_url}")
        
    def run_work(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for repo_url in self.repo_urls:
                executor.submit(self.worker, repo_url)

def test():
    clone_test = cloner("/Users/jiachengzhong/project/jhu-research/python-class-pollution/python-class-pollution/tasks/codeql-class-pollution-1K/config.yaml")
    clone_test.run_work()
test()
# def __main__():
#     parser = ArgumentParser()
#     parser.add_argument("--config_file", type=str, default="config.yaml")
#     args = parser.parse_args()

#     cloner = cloner(args.config_file)
#     cloner.run_work()
    