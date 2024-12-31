import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

/**
 * Filter repositories with Python code using the GitHub API.
 * 
 * @param {Object} repo - The repository data returned by the GitHub API.
 * @param {Object} spider - The Spider object, which contains the Octokit instance for making API requests.
 * @returns {Boolean} - True if the repository contains Python code, False otherwise.
 */
export async function filterHasJavaScriptCode(repo, spider) {
  const owner = repo.owner.login;
  const repoName = repo.name;

  try {
    const { data: languages } = await spider.octokit.request('GET /repos/{owner}/{repo}/languages', {
      owner,
      repo: repoName
    });

    return languages.hasOwnProperty('JavaScript') || languages.hasOwnProperty('TypeScript');
  } catch (error) {
    spider.logger.error(`Failed to retrieve languages for repository ${repo.full_name}: ${error.message}`);
    return false;
  }
}