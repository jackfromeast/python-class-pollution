/**
 * Filter repositories with electron apps using the GitHub API.
 * 
 * @param {Object} repo - The repository data returned by the GitHub API.
 * @param {Object} spider - The Spider object, which contains the Octokit instance for making API requests.
 * @returns {Boolean} - True if the repository contains Python code, False otherwise.
 */
export async function filterHasElectronTopic(repo, spider) {
  const owner = repo.owner.login;
  const repoName = repo.name;

  try {
    const { data: topics } = await spider.octokit.request('GET /repos/{owner}/{repo}/topics', {
      owner,
      repo: repoName
    });

    return topics['names'].indexOf("electron")!=-1;
  } catch (error) {
    if (error.status === 403 && error.message.includes('API rate limit exceeded')) {
      spider.logger.error(`API rate limit exceeded: ${error.message}. Sleeping for 1 hour...`);

      // Countdown for 1 hour with 10-minute intervals
      const sleepDuration = 61 * 60 * 1000; // 1 hour in milliseconds
      const interval = 10 * 60 * 1000; // 10 minutes in milliseconds
      for (let remaining = sleepDuration; remaining > 0; remaining -= interval) {
        spider.logger.info(`Sleeping... ${Math.ceil(remaining / (60 * 1000))} minutes remaining.`);
        await new Promise(resolve => setTimeout(resolve, Math.min(interval, remaining)));
      }

      // Retry the same repository
      return filterHasElectronTopic(repo, spider);
    }

    spider.logger.error(`Failed to retrieve languages for repository ${repo.full_name}: ${error.message}`);
    return false;
  }
}

// case1: https://github.com/advanced-rest-client/arc-electron
// case2: https://github.com/RocketChat/Rocket.Chat