import fs from 'fs';
import path from 'path';
import { execSync, spawnSync } from 'child_process';
import { glob } from 'glob';

const sourcePattern = {
  "pickle.Unpickler": /pickle\.Unpickler/,
  "*Unpickler": /\b.*Unpickler/
}

/** 
 * Filter repos with pickler unpicker
 * 
 * @param {Dict} The repo data (a page of repo) returned by the Github API
 * @param {Spider} The Spider object
 * @returns {Boolean} True/False if the repo is an LLM application
 */
export async function filterUnpicker(repo, spider) {
  const id = repo.id;
  const repository = repo;
  const repoPath = await download(id, repository, spider);
  const result = await search(repoPath, spider);
  await deleteRepo(repoPath);

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
  let files = glob.sync(`${repositoryPath}/**/*.py`);
  let result = false;

  files.forEach(file => {
    if (file.includes('test') || file.includes('example') || file.includes('demo')) { return; }

    // Ensure the path is a file before attempting to read it
    if (fs.statSync(file).isFile()) {
      try {
        const fileContent = fs.readFileSync(file, 'utf-8');
        const lines = fileContent.split('\n');

        for (const [patternName, pattern] of Object.entries(sourcePattern)) {
          lines.forEach((line, lineNumber) => {
            if (pattern.test(line)) {
              spider.logger.info(`Found pattern ${patternName} in file ${file} at line ${lineNumber + 1} at repo: ${repositoryPath}`);
              result = true;
            }
          });
        }

        if (result) { return true; }
      } catch (error) {
        spider.logger.error(`Error reading file ${file}: ${error.message}`);
      }
    } else {
      spider.logger.warn(`Skipping non-file path: ${file}`);
    }
  });

  return result;
}

async function deleteRepo(repositoryPath) {
  fs.rmSync(repositoryPath, { recursive: true, force: true });
  fs.rmSync(repositoryPath + '-codeql-db', { recursive: true, force: true });
}