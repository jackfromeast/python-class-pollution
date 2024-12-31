import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

/**
 * Filter repositories with Python code containing `glom.assign(` using the GitHub API.
 *
 * @param {Object} repo - The repository data returned by the GitHub API.
 * @param {Object} spider - The Spider object, which contains the Octokit instance for making API requests.
 * @returns {Boolean} - True if the repository contains Python code using `glom.assign(`, False otherwise.
 */
export async function filterHasGlomAssign(repo, spider) {
  const owner = repo.owner.login;
  const repoName = repo.name;

  try {
    // Step 1: Check if the repository contains Python code
    const { data: languages } = await spider.octokit.request('GET /repos/{owner}/{repo}/languages', {
      owner,
      repo: repoName,
    });

    if (!languages.hasOwnProperty('Python')) {
      spider.logger.info(`Repository ${repo.full_name} does not contain Python code.`);
      return false;
    }

    // Step 2: Search for `glom.assign(` in the codebase
    const searchQuery = `glom.assign( repo:${owner}/${repoName}`;
    const { data: searchResults } = await spider.octokit.request('GET /search/code', {
      q: searchQuery,
    });

    // If search results contain any matches, return true
    if (searchResults.total_count > 0) {
      for (const item of searchResults.items) {
        if (item.path.endsWith('.ipynb') || item.path.endsWith('.py')) {
          spider.logger.info(`Repository ${repo.full_name} contains 'glom.assign('.`);
          return true;
        }
      }
    }

    // If no matches are found, return false
    spider.logger.info(`Repository ${repo.full_name} does not contain 'glom.assign('.`);
    return false;

  } catch (error) {
    if (error.status === 403 && error.message.includes('API rate limit exceeded')) {
      const rateLimitReset = error.response?.headers['x-ratelimit-reset'];
      const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
      const waitTime = rateLimitReset ? rateLimitReset - currentTime : 60; // Default to 1 minute if no reset time

      spider.logger.error(
        `API rate limit exceeded for 'Search code': ${error.message}. Sleeping for ${waitTime} seconds...`
      );

      await new Promise(resolve => setTimeout(resolve, waitTime * 1000));

      // Retry the same repository
      return filterHasGlomAssign(repo, spider);
    }

    spider.logger.error(
      `Failed to search for 'glom.assign(' in repository ${repo.full_name}: ${error.message}`
    );
    return false;
  }
}