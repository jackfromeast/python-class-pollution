/**
 * This script searches for good JavaScript repositories (>1000 Stars) on GitHub.
 * 
 * Example:
 * Query: created:2024-01-01..2024-01-21 language:JavaScript stars:>1000
 * 
 * Reference:
 * https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories
 * https://github.com/rsain/GitHub-Crawler/blob/master/getDataFromGitHub.py
 */

import { Octokit } from "@octokit/core";
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import OpenAI from "openai";
import yaml from 'js-yaml';
import Logger from './logger.js';

const CONFIG = yaml.load(fs.readFileSync('/home/jiacheng/python-class-pollution/crawler/config-2020-2024.yml', 'utf8'));
// const CONFIG = yaml.load(fs.readFileSync('../config.yml', 'utf8'));
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class Spider {
  constructor () {
    this.outputPath = CONFIG.TASK.OUTPUT_PATH;
    this.tmpPath = CONFIG.TASK.TEMP_PATH;

    if (!fs.existsSync(path.dirname(this.outputPath))){
      fs.mkdirSync(path.dirname(this.outputPath), { recursive: true });
    }

    this.logger = new Logger('debug', 'CRAWLER', CONFIG.TASK.LOG_PATH);
  }

  async initialize() {
    this.filter_functions = await this.install_filters();
    // this.openAIClient = new OpenAI({
    //   organization: CONFIG.OPENAI.ORGANIZATION,
    //   project: CONFIG.OPENAI.PROJECT,
    //   apiKey: CONFIG.OPENAI.API_KEY
    // });
    this.octokit = new Octokit({
      auth: CONFIG.GITHUB.TOKEN
    });
  }

  async install_filters() {
    const filters = CONFIG.TASK.FILTERS;
    const filterFunctions = [];

    for (const filter of filters) {
      const { FILE, FILTER_NAME } = filter;
      try {
        const filterModule = await import(FILE);
        if (filterModule[FILTER_NAME]) {
          filterFunctions.push(filterModule[FILTER_NAME]);
        } else {
          this.logger.warn(`Filter function ${FILTER_NAME} not found in ${FILE}`);
        }
      } catch (error) {
        this.logger.error(`Failed to load filter from ${FILE}: ${error}`);
      }
    }
    return filterFunctions;
  }

  async retrieve(query, page=1, retry=3) {
    try {
      var res = await this.octokit.request('GET /search/repositories', {
        headers: { accept: 'application/vnd.github+json' },
        q: query,
        per_page: 100,
        page: page
      });
    } catch (error) {
      this.logger.error(`[-] Error during octokit.request: ${error.message}`);

      if (retry > 0)
        return this.retrieve(query, page, retry - 1);
      
      return [[], 0, 0];
    }

    await sleep(10000); 

    // let result = await this.filter(res.data.items);
    // Filter the result using the filter functions
    let total_count = res.data.total_count;
    let result = res.data.items;
    for (const filterFunction of this.filter_functions) {
      const filteredResult = [];
      for (const repo of result) {
        try {
          if (CONFIG.TASK.GITHUB_FILTER.MAX_SIZE && repo.size > CONFIG.TASK.GITHUB_FILTER.MAX_SIZE) { 
            this.logger.info(`[-] Skip ${repo.name} due to size ${repo.size}`);
            continue;
          }
          if (await filterFunction(repo, this)) { filteredResult.push(repo);}
        } catch (error) {
          this.logger.error(`Error while filtering: ${error}`);
        }
      }
      this.logger.info(`[+] Filtered ${filteredResult.length}/${result.length} results using ${filterFunction.name}`);
      result = filteredResult;
    }

    let rateLimit = res.headers['x-ratelimit-remaining'];
    this.logger.info(`[+] Found ${result.length}/${res.data.items.length} results for "${query}" on page ${page}.`);
    return [result, total_count, rateLimit];
  }

  /**
   * Github will return 1000 results for each query which at most 10 pages
   * @param {*} query 
   */
  async searchAllPages(query) {
    let results = [];
    
    let [firstPage, total_count, _] = await this.retrieve(query, 1);
    results = results.concat(firstPage);

    const totalPages = Math.min(10, Math.ceil(total_count / 100));
    for (let i = 2; i <= totalPages; i++) {
      let [pageResult, total_count, rateLimit] = await this.retrieve(query, i);
      results = results.concat(pageResult);

      if (parseInt(rateLimit) === 1) {
        this.logger.log(`[-] Rate limit reached. Sleeping for 1 minute...`);
        await sleep(60000);
      }
    }

    return results;
  }

  /**
   * Since Github only returns 1000 results for each query, we need to create subqueries based on time windows
   * Query: created:2024-01-01..2024-01-21 language:JavaScript stars:>1000
   */
  async searchAll() {
    let results = [];

    const startDate = new Date(CONFIG.TASK.GITHUB_FILTER.START_DATE);
    const endDate = new Date(CONFIG.TASK.GITHUB_FILTER.END_DATE);

    const timeRange = CONFIG.TASK.GITHUB_FILTER.TIME_RANGE;
    function addOnePeriod(date) {
      const newDate = new Date(date);
      if (timeRange === 'Week') {
        newDate.setDate(newDate.getDate() + 7);
      } else if (timeRange === 'Month') {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    }

    // Split the date range into chunks based on the configured time range
    let currentStartDate = startDate;

    while (currentStartDate < endDate) {
      let currentEndDate = addOnePeriod(currentStartDate);
      if (currentEndDate > endDate) {
        currentEndDate = endDate;
      }

      // Format dates to YYYY-MM-DD
      let formattedStartDate = currentStartDate.toISOString().split('T')[0];
      let formattedEndDate = currentEndDate.toISOString().split('T')[0];

      // Construct the query string
      let query = `created:${formattedStartDate}..${formattedEndDate} language:${CONFIG.TASK.GITHUB_FILTER.LANGUAGE} stars:>${CONFIG.TASK.GITHUB_FILTER.STARS}`;
      this.logger.info(`[+] Searching for repositories created between ${formattedStartDate} and ${formattedEndDate}`);

      // Search all pages for the current query
      await this.searchAllPages(query)
        .then(result => {
          results = results.concat(result);

          this.save(results);
          this.logger.info(`[+] Saved ${results.length} repositories so far.`);

          currentStartDate = currentEndDate;
        })
        .catch(error => {
          this.logger.error(`[-] Error during search: ${error.message}`);
        });
    }

    results = results.sort((a, b) => b.stargazers_count - a.stargazers_count);
    this.save(results);
  }

  save(result) {
    fs.writeFileSync(this.outputPath, JSON.stringify(result, null, 2)); // Format JSON for readability
  }
}


(async () => {
  const spider = new Spider();
  await spider.initialize()
  await spider.searchAll();
})()