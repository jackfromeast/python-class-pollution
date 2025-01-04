import fs from 'fs';
import path from 'path';
import { Octokit } from "@octokit/core";

const extractGithubLinks = (text) => {
  const pattern = /\/repos\/([\w\-]+)\/([\w\-]+)/g;
  const matches = text.matchAll(pattern);

  const githubLinks = Array.from(matches, match => `https://github.com/${match[1]}/${match[2]}`);
  
  return [...new Set(githubLinks)];
};

const inputText = fs.readFileSync('input/huntr.html', 'utf8');
const githubLinks = extractGithubLinks(inputText);

fs.writeFileSync('output/huntr-sponsored-repo-links.json', JSON.stringify(githubLinks, null, 2));

const octokit = new Octokit({
  auth: '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' // Ensure to replace this with your actual token
});

// Function to fetch GitHub repository information
const fetchRepoDetails = async (repoUrl) => {
  const [owner, repo] = repoUrl.replace('https://github.com/', '').split('/');
  try {
    const response = await octokit.request('GET /repos/{owner}/{repo}', {
      owner,
      repo
    });
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch details for ${repoUrl}:`, error);
    return null;
  }
};

// Main function to fetch repository details and save them
const fetchAndSaveRepoDetails = async (links) => {
  const repoDetails = [];
  
  for (const link of links) {
    const details = await fetchRepoDetails(link);
    if (details) repoDetails.push(details); // Add valid repository details
  }

  fs.writeFileSync('output/huntr-sponsored-repos.json', JSON.stringify(repoDetails, null, 2));
};


fetchAndSaveRepoDetails(githubLinks);
