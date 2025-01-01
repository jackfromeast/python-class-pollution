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
  "glom.assign": /\bglom\.assign\(/i,
  "glom.assign.direct_import": /\bglom\s+import\s+.*\bassign\b/i,
  "glom.assign.as": [
    /import\s+.*glom\s+as/,
    /\.assign\(/i
  ],
  "glom.assign.wildcard_import": [
    /from\s+glom\s+import\s+\*/,
    /\bassign\(/i
  ],
  "pydash.set_": /\bpydash.set\_\(/,
  "pydash.set_.direct_import": /\bpydash\s+import\s+.*\bset_\b/,
  "pydash.set_.as": [
    /import\s+.*pydash\s+as/,
    /\.set_\(/
  ],
  "pydash.set_.wildcard_import": [
    /from\s+pydash\s+import\s+\*/,
    /\bset_\(/
  ],
  "deepdiff.Delta": /\bdeepdiff.Delta\(/,
  "deepdiff.Delta.direct_import": /\bdeepdiff\s+import\s+.*\bDelta\b/,
  "deepdiff.Delta.as": [
    /import\s+.*deepdiff\s+as/,
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


async function search(repositoryPath) {
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
    // if (file.includes('test') || file.includes('example') || file.includes('demo')) { return; }

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
                    console.log(
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
                console.log(`Found pattern ${patternName} in file ${file} at line ${lineNumber + 1}`);
              }
            }
          }
        });
      } catch (error) {
        console.log(`Error reading file ${file}: ${error.message}`);
        // console.log(`Error reading file ${file}: ${error.message}`);
      }
    } else {
      console.log(`Skipping non-file path: ${file}`);
      // console.log(`Skipping non-file path: ${file}`);
    }
  });
  // Evaluate multi-condition patterns
  let match_num = 0;
  for (const [patternName, resultSet] of Object.entries(patternResults)) {
    if (Array.isArray(sourcePattern[patternName])) {
      // Check if all conditions are satisfied
      if (resultSet.size === sourcePattern[patternName].length) {
        console.log(`All conditions for pattern ${patternName} matched in repository: ${repositoryPath}`);
        match_num += 1;
        result = true;
      }
    } else if (resultSet) {
      // Simple patterns that matched
      match_num += 1;
      result = true;
    }
  }
  console.log(`Found ${match_num}/${Object.keys(sourcePattern).length} patterns in repository: ${repositoryPath}`);
  return result;
}

async function deleteRepo(repositoryPath) {
  fs.rmSync(repositoryPath, { recursive: true, force: true });
  fs.rmSync(repositoryPath + '-codeql-db', { recursive: true, force: true });
}


async function test(testPath) {
  const files = glob.sync(`${testPath}/**/*.py`);

  let total_repos = files.length;
  let vulnerable_repos = 0;
  for (const file of files) {
    const tmpPath = path.join(testPath+'-tmp', path.basename(file));
    fs.mkdirSync(tmpPath, { recursive: true });
    fs.copyFileSync(file, path.join(tmpPath, path.basename(file)));
    const result = await search(tmpPath);
    if (result) {
      vulnerable_repos += 1;
    } else {
      console.log(`[-] No class pollution found in: ${file}`);
    }
    fs.rmSync(tmpPath, { recursive: true, force: true });
  }
  console.log(`Total repos: ${total_repos}, vulnerable repos: ${vulnerable_repos}`);
}

test("/Users/jiachengzhong/project/jhu-research/python-class-pollution/python-class-pollution/crawler/src/filters/test")
