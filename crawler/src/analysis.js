import fs from 'fs';
import path from 'path';
import { execSync, spawnSync } from 'child_process';
import { glob } from 'glob';
import log4js from 'log4js';

log4js.configure({
  appenders: {
    console: { type: 'console' },
    file: { type: 'fileSync', filename: '../logs/analysis.log' }
  },
  categories: {
    default: { appenders: ['console', 'file'], level: 'info' }
  }
});
var logger = log4js.getLogger();
logger.level = "info";

export class Analyzer {
  constructor(dataPath = './output/huntr-sponsored-repos.json', outputPath = './output/huntr-sponsored-repo-analysis-results.json', codeqlOutputPath = './output/codeql-results', workPath = '../tmp') {
    this.data = this.readData(dataPath);
    this.dataPath = dataPath;
    this.outputPath = outputPath;
    this.codeqlOutputPath = codeqlOutputPath;
    this.workPath = workPath;

    this.codeqlQueryPath = '/home/jackfromeast/Desktop/TheHulk/codeql-query/DOMClobbering/DOMClobbering.ql';
  }

  readData(dataPath) {
    return JSON.parse(fs.readFileSync(dataPath));
  }

  // Modify the save method to write to the file dynamically
  saveDynamicInit() {
    this.outputStream = fs.openSync(this.outputPath, 'w');
    fs.writeSync(this.outputStream, '[');
  }

  saveDynamicAppend(result, isLast = false) {
    try {
      if (this.outputStream) { // Ensure the stream is open
        const jsonData = JSON.stringify(result, null, 2);
        fs.writeSync(this.outputStream, jsonData);
        if (!isLast) {
          fs.writeSync(this.outputStream, ',\n');
        }
      } else {
        logger.error('Attempted to write to a closed or invalid file stream.');
      }
    } catch (error) {
      logger.error(`Error writing to the file: ${error.message}`);
    }
  }

  saveDynamicClose() {
    fs.writeSync(this.outputStream, ']');
    fs.closeSync(this.outputStream);
  }

  // sourcePatterns = {
  //   // SSRF Patterns
  //   "import urllib3": /\bimport\s+urllib3\b/g,
  //   "import requests": /\bimport\s+requests\b/g,
  //   "import http.client": /\bimport\s+http\.client\b/g,
  //   "import urllib.request": /\bimport\s+urllib\.request\b/g,
  //   "import selenium": /\bimport\s+selenium\b/g,
  //   "import playwright": /\bimport\s+playwright\b/g,
  //   "import puppeteer": /\bimport\s+puppeteer\b/g,
  //   "import BeautifulSoup": /\bimport\s+BeautifulSoup\b/g,
  //   "import bs4": /\bimport\s+bs4\b/g,
  //   "requests.get": /\brequests\.get\b/g,
  //   "requests.post": /\brequests\.post\b/g,
  //   "requests.put": /\brequests\.put\b/g,
  //   "requests.delete": /\brequests\.delete\b/g,
  //   ".request (generic request)": /\b\w+\.request\b/g,
  //   "driver.get": /\bdriver\.get\b/g,
  //   "page.goto": /\bpage\.goto\b/g,
  //   "urlopen": /\burlopen\b/g,
  //   "web search": /\bweb\s+search\b/g,
  //   "web retrieve": /\bweb\s+retrieve\b/g,

  //   // RCE Patterns
  //   "exec": /\bexec\b/g,
  //   "eval": /\beval\b/g,
  //   "os.system": /\bos\.system\b/g,
  //   "subprocess.call": /\bsubprocess\.call\b/g,
  //   "subprocess.run": /\bsubprocess\.run\b/g,
  //   "subprocess.Popen": /\bsubprocess\.Popen\b/g,
  //   ".Process": /\.Process\b/g,
  //   "import pickle": /\bimport\s+pickle\b/g,
  //   "import subprocess": /\bimport\s+subprocess\b/g,
  //   "import dill": /\bimport\s+dill\b/g,
  //   "pickle.load": /\bpickle\.load\b/g,
  //   "pickle.loads": /\bpickle\.loads\b/g,
  //   "torch.load": /\btorch\.load\b/g,
  //   "dill.load": /\bdill\.load\b/g,
  //   "dill.loads": /\bdill\.loads\b/g,
  //   "yaml.load": /\byaml\.load\b/g,
  //   "YAML": /\bYAML\b/g,
  //   ".load (generic load)": /\b\w+\.load\b/g,
  //   ".loads (generic loads)": /\b\w+\.loads\b/g,
  //   "Unpickler": /\bUnpickler\b/g,
  //   "pickle.Unpickler": /\bpickle\.Unpickler\b/g,
  //   "execfile": /\bexecfile\b/g,
  //   "evalfile": /\bevalfile\b/g,
  //   "runpy.run_path": /\brunpy\.run_path\b/g,
  //   "exec_module": /\bexec_module\b/g,

  //   // SSTI
  //   "jinja2.Environment": /\bjinja2\.Environment\b/g,
  //   "jinja2": /\bjinja2\b/g,

  //   // XSS
  //   "make_response": /\bmake_response\b/g,
  //   "render_template": /\brender_template\b/g,

  //   // SQLi
  //   "SQLAlchemy": /\bSQLAlchemy\b/g,
  //   "sqlite3": /\bsqlite3\b/g,
  //   "mysql": /\bmysql\b/g,
  // }

  sourcePatterns = {
    "import pickle": /\bimport\s+pickle\b/g,
    "pickle.load": /\bpickle\.load\b/g,
    "pickle.Unpickler": /\bpickle\.Unpickler\b/g,
    "import dill": /\bimport\s+dill\b/g,
    "dill.load": /\bdill\.load\b/g,
    "dill.load_session": /\bdill\.load_session\b/g,
    "import joblib": /\bimport\s+joblib\b/g,
    "joblib.load": /\bjoblib\.load\b/g,
    "numpy.load": /\bnumpy\.load\b/g,
    "torch.load": /\btorch\.load\b/g,
    "import h5py": /\bimport\s+h5py\b/g,
    "onnx.load": /\bonnx\.load\b/g,
    "import onnx": /\bimport\s+onnx\b/g,
    ".from_pretrained": /\b\w+\.from_pretrained\b/g,
    ".load_weights": /\b\w+\.load_weights\b/g,
    ".restore": /\b\w+\.restore\b/g,
    ".load_model": /\b\w+\.load_model\b/g,
    ".pipeline": /\b\w+\.pipeline\b/g,
    ".restore_checkpoint": /\b\w+\.restore_checkpoint\b/g,
    "h5py.File": /\bh5py\.File\b/g,
    "cloudpickle.load": /\bcloudpickle\.load\b/g,
  }

  sourcePatternBacklist = [
    "json.loads", "json.load"
  ];

  async analyzeAll(from = 0, to = -1) {
    if (to === -1) { to = this.data.length; }

    let id = from;
    this.saveDynamicInit();

    for (let index = from; index < to; index++) {
      const repo = this.data[index];
      try {

        logger.info(`Processing ${id++}/${to} repository: ${repo.full_name}.`);
        
        // Await the asynchronous operation
        let repoPath = await this.download(repo.id, repo);
        let repoResult = await this.analyzeBasedOnSourcePattern(repo, repoPath);
        // let repoResult = await this.analyzeBasedOnCodeql(repo, repoPath);
        this.delete(repoPath);
        
        if (repoResult) {
          const isLast = (index === to - 1);
          this.saveDynamicAppend(repoResult, isLast);
        }
      } catch (error) {
        logger.info(`Error analyzing ${repo.full_name}: ${error.message}`);
      }
    }

    this.saveDynamicClose();
  }

  async analyzeBasedOnSourcePattern(repository, repoPath) {
    let repositoryResult = null;

    // 1. Use the sourcePatterns to search all the .js/.ts files in the repo
    let matchedResults = await this.search(repoPath);

    // 2. If results are not empty, save the results to repository.filterResult and return
    if (Object.keys(matchedResults).length > 0) {
      repositoryResult = {
        id: repository.id,
        full_name: repository.full_name,
        stargazers_count: repository.stargazers_count,
        html_url: repository.html_url,
        description: repository.description,
        matchedResult: matchedResults,
        // codeqlResultPath: codeqlResults
      };

      let summary = Object.entries(matchedResults)
                    .map(([pattern, matches]) => `${pattern}: ${matches.length}`)
                    .join(', ');

      logger.info(`Found patterns - ${summary}`);
    }

    return repositoryResult;
  }

  async download(id, repository) {
    const repoPath = path.join(this.workPath, `repo-${id}`);
    if (!fs.existsSync(repoPath)) {
      fs.mkdirSync(repoPath, { recursive: true });
    }

    logger.info(`Downloading repository: ${repository.clone_url}`);
    execSync(`git clone ${repository.clone_url} ${repoPath}`, { stdio: 'inherit' });
    return repoPath;
  }

  async search(repositoryPath) {
    let results = {};
    let files = glob.sync(`${repositoryPath}/**/*.py`);

    files.forEach(file => {
      // Ensure the path is a file before attempting to read it
      if (fs.statSync(file).isFile()) {
        try {
          const fileContent = fs.readFileSync(file, 'utf-8');
          const lines = fileContent.split('\n');
  
          for (const [patternName, pattern] of Object.entries(this.sourcePatterns)) {
            lines.forEach((line, lineNumber) => {
              if (pattern.test(line)) {
                if (!this.sourcePatternBacklist.some(blacklistPattern => line.includes(blacklistPattern))) {
                  if (!results[patternName]) {
                    results[patternName] = [];
                  }
                  
                  // The filepath shouldn't contain test or example
                  if (file.includes('test') || file.includes('example')) {
                    return;
                  }

                  results[patternName].push({
                    filePath: file,
                    lineNumber: lineNumber + 1,
                    matchedContent: line.trim().substring(0, 100)
                  });
                }
              }
            });
          }
        } catch (error) {
          logger.error(`Error reading file ${file}: ${error.message}`);
        }
      } else {
        logger.warn(`Skipping non-file path: ${file}`);
      }
    });
  
    return results;
  }

  async analyzeBasedOnCodeql(repository, repositoryPath) {
    const dbPath = path.join(this.workPath, `${path.basename(repositoryPath)}-codeql-db`);
    const resultPath = path.join(this.codeqlOutputPath, `${path.basename(repositoryPath)}-codeql-results.sarif`);
  
    try {
      logger.info(`Creating CodeQL database for repository at ${repositoryPath}`);
      const createArgs = ['database', 'create', '--overwrite', '--language=javascript', '--source-root', repositoryPath, dbPath];
      
      // Run the database creation process synchronously
      const createProcess = spawnSync('codeql', createArgs);
  
      // Check if the process was successful
      if (createProcess.error) {
        logger.error(`Failed to start CodeQL database creation process: ${createProcess.error.message}`);
        return null;
      }
  
      if (createProcess.status !== 0) {
        logger.error(`CodeQL database creation failed with code ${createProcess.status}`);
        logger.error(`stderr: ${createProcess.stderr.toString()}`);
        return null;
      }
  
      logger.info(`CodeQL database created at ${dbPath}`);
  
      logger.info(`Running CodeQL analysis on ${repositoryPath}`);
      const runArgs = ['database', 'analyze', dbPath, this.codeqlQueryPath, '--format=sarif-latest', '-o', resultPath];
      
      // Run the analysis process synchronously
      const runProcess = spawnSync('codeql', runArgs, { timeout: 1800000 }); // 30 mins timeout
  
      // Check if the process was successful
      if (runProcess.error) {
        logger.error(`Failed to start CodeQL analysis process: ${runProcess.error.message}`);
        return null;
      }
  
      if (runProcess.status !== 0) {
        logger.error(`CodeQL analysis failed with code ${runProcess.status}`);
        logger.error(`stderr: ${runProcess.stderr.toString()}`);
        return null;
      }
  
      logger.info(`CodeQL analysis result saved at ${resultPath}`);
      return this.summaryCodeQLResult(repository, resultPath);
    } catch (error) {
      logger.error(`Error during CodeQL analysis: ${error.message}`);
      return null;
    }
  }

  summaryCodeQLResult(repository, resultPath) {
    try {
      // 1/ Read the output SARIF from the resultPath
      const sarifData = JSON.parse(fs.readFileSync(resultPath, 'utf-8'));
  
      // 2/ Check for taint flows in the SARIF file
      let taintFlowMessages = [];
  
      if (sarifData.runs) {
        sarifData.runs.forEach(run => {
          if (run.results) {
            run.results.forEach(result => {
              // Example: Extract relevant messages and locations associated with taint flows
              if (result.ruleId && result.message && result.message.text) {
                taintFlowMessages.push(result.message.text);
              }
            });
          }
        });
      }
  
      // 3/ If there are taint flows, return the summarized repository result
      if (taintFlowMessages.length > 0) {
        logger.info(`Found ${taintFlowMessages.length} taint flows for ${repository.full_name}`);
        return {
          id: repository.id,
          full_name: repository.full_name,
          stargazers_count: repository.stargazers_count,
          html_url: repository.html_url,
          description: repository.description,
          codeqlResultPath: taintFlowMessages
        };
      } else {
        logger.info(`No taint flows found for ${repository.full_name}`);
        return null; // No taint flows found
      }
    } catch (error) {
      logger.error(`Error processing SARIF file at ${resultPath}: ${error.message}`);
      return null;
    }
  }
  
  delete(repositoryPath) {
    logger.info(`Deleting repository: ${repositoryPath} and ${repositoryPath + '-codeql-db'}.`);
    fs.rmSync(repositoryPath, { recursive: true, force: true });
    fs.rmSync(repositoryPath + '-codeql-db', { recursive: true, force: true });
  }
}

(async function main() {
  let input_repo = '../output/huntr-sponsored-repos.json';
  let output_repo = '../output/huntr-sponsored-repo-analysis-results-deserialization.json';
  let codeql_results = '../output/codeql-results';
  let tmp = '../tmp';

  const analyzer = new Analyzer(input_repo, output_repo, codeql_results, tmp);
  await analyzer.analyzeAll();
}())