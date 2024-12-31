import fs from 'fs';
import path from 'path';
import { execSync, spawnSync } from 'child_process';
import { glob } from 'glob';
/**
 * Filter repositories with Python code invoke python libraries that are vulnerable to class pollution
 * by downloading the repository and conduct local search.
 *
 * @param {Object} repo - The repository data returned by the GitHub API.
 * @param {Object} spider - The Spider object, which contains the Octokit instance for making API requests.
 * @returns {Boolean} - True if the repository contains Python code using vulnerabile libraries, False otherwise.
 */

// @Library.Func.direct_import
// Match direct import with alias or not 
// 1: from glom import assign as a
//       a(obj, ...)
// 2: from glom import assign
//       assign(obj, ...)
const sourcePattern = {
  "glom.assign": /\bglom\.assign\(/,
  "glom.assign.direct_import": /glom\s+import\s+assign/,
  "glom.assign.as": [
    /import\s+glom\s+as/,
    /\.assign\(/
  ],
  "glom.assign.wildcard_import": [
    /from\s+glom\s+import\s+\*/,
    /\bassign\(/
  ],
  "pydash.set_": /\bpydash.set\_\(/,
  "pydash.set_.direct_import": /pydash\s+import\s+set_/,
  "pydash.set_.as": [
    /import\s+pydash\s+as/,
    /\.set_\(/
  ],
  "pydash.set_.wildcard_import": [
    /from\s+pydash\s+import\s+\*/,
    /\bset_\(/
  ],
  "deepdiff.Delta": /\bdeepdiff.Delta\(/,
  "deepdiff.Delta.direct_import": /deepdiff\s+import\s+Delta/,
  "deepdiff.Delta.as": [
    /import\s+deepdiff\s+as/,
    /\.Delta\(/,
  ],
  "deepdiff.Delta.wildcard_import": [
    /from\s+deepdiff\s+import\s+\*/,
    /\bDelta\(/,
  ]
}


/** 
 * Filter repos with potential class pollution vulnerability
 * 
 * @param {Dict} The repo data (a page of repo) returned by the Github API
 * @param {Spider} The Spider object
 * @returns {Boolean} True/False if the repo uses the vulnerable library
 */
export async function filterUseClassPollutionLibraryLocalCheck(repo, spider) {
  const id = repo.id;
  const repository = repo;
  const repoPath = await download(id, repository, spider);
  const result = await search(repoPath, spider);
  if (result == false) { await deleteRepo(repoPath); }
  return result;
}

async function download(id, repository, spider) {
  const repoPath = path.join(spider.tmpPath, `repo-${id}`);
  if (!fs.existsSync(repoPath)) {
    fs.mkdirSync(repoPath, { recursive: true });
  }

  spider.logger.info(`Downloading repository: ${repository.clone_url}`);
  execSync(`git clone ${repository.clone_url} ${repoPath}`, { stdio: 'inherit' });
  return repoPath;
}


async function search(repositoryPath, spider) {
  const files = glob.sync(`${repositoryPath}/**/*.py`);
  const patternResults = {}; // To track patterns and their matches
  let result = false;

  // Initialize pattern results for multi-condition checks
  for (const [patternName, pattern] of Object.entries(sourcePattern)) {
    if (Array.isArray(pattern)) {
      patternResults[patternName] = new Set(); // Use Set to track matches for multi-condition patterns
    } else {
      patternResults[patternName] = false;
    }
  }

  files.forEach(file => {
    if (file.includes('test') || file.includes('example') || file.includes('demo')) { return; }

    // Ensure the path is a file before attempting to read it
    if (fs.statSync(file).isFile()) {
      try {
        const fileContent = fs.readFileSync(file, 'utf-8');
        const lines = fileContent.split('\n');

        lines.forEach((line, lineNumber) => {
          for (const [patternName, pattern] of Object.entries(sourcePattern)) {
            if (Array.isArray(pattern)) {
              // Multi-condition pattern
              pattern.forEach((subPattern, index) => {
                if (subPattern.test(line)) {
                  if (!patternResults[patternName].has(index)) {
                    spider.logger.info(
                      `Found sub-pattern ${index + 1} of ${patternName} in file ${file} at line ${lineNumber + 1}`
                    );
                  }
                  patternResults[patternName].add(index); // Mark the sub-pattern as matched
                }
              });
            } else {
              // Simple pattern
              if (pattern.test(line)) {
                patternResults[patternName] = true;
                spider.logger.info(`Found pattern ${patternName} in file ${file} at line ${lineNumber + 1}`);
              }
            }
          }
        });
      } catch (error) {
        spider.logger.error(`Error reading file ${file}: ${error.message}`);
        // console.log(`Error reading file ${file}: ${error.message}`);
      }
    } else {
      spider.logger.warn(`Skipping non-file path: ${file}`);
      // console.log(`Skipping non-file path: ${file}`);
    }
  });
  // Evaluate multi-condition patterns
  let match_num = 0;
  for (const [patternName, resultSet] of Object.entries(patternResults)) {
    if (Array.isArray(sourcePattern[patternName])) {
      // Check if all conditions are satisfied
      if (resultSet.size === sourcePattern[patternName].length) {
        spider.logger.info(`All conditions for pattern ${patternName} matched in repository: ${repositoryPath}`);
        match_num += 1;
        result = true;
      }
    } else if (resultSet) {
      // Simple patterns that matched
      match_num += 1;
      result = true;
    }
  }
  spider.logger.info(`Found ${match_num}/${Object.keys(sourcePattern).length} patterns in repository: ${repositoryPath}`);
  return result;
}

async function deleteRepo(repositoryPath) {
  fs.rmSync(repositoryPath, { recursive: true, force: true });
  fs.rmSync(repositoryPath + '-codeql-db', { recursive: true, force: true });
}
