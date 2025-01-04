/** 
 * Filter out non-LLM applications
 * 
 * @param {Dict} The repo data (a page of repo) returned by the Github API
 * @param {Spider} The Spider object
 * @returns {Boolean} True/False if the repo is an LLM application
 */
export async function isLLMAppFilter(repo, spider) {
  const readmeFileNames = ['README.md', 'ReadMe.md', 'readme.md', 'Readme.md', 'README.MD', 'ReadMe.MD', 'readme.MD', 'Readme.MD', 'README.rst'];

  let readmeText = null;
  for (const filename of readmeFileNames) {
    const repoREADMEUrl = `https://raw.githubusercontent.com/${repo.owner.login}/${repo.name}/${repo.default_branch}/${filename}`;

    try {
      const response = await fetch(repoREADMEUrl);
      if (response.ok) {
        readmeText = await response.text();
        break;
      }
    } catch (error) {
      spider.logger.error(`[-] Error fetching README for ${repo.name}: ${error.message}`);
    }
  }

  if (readmeText) {
    if (await isLLMProject(readmeText, spider.openAIClient, spider)) {
      spider.logger.info(`[+] Found an LLM project: ${repo.html_url}`);
      return true;
    }
  } else {
    spider.logger.warn(`[-] Could not fetch any README for ${repo.name}.`);
  }
  
  return false;
}

async function isLLMProject(readme_text, client, spider) {
  const cleanedText = readme_text
      .split('\n')
      .filter(line => line.trim() !== '')
      .map(line => line.trim().replace(/\s+/g, ' '))
      .join('\n');
  
  const slicedText = cleanedText.slice(0, 10000);
  const response = await client.chat.completions.create({
    messages: [ { role: 'system', content: SystemLLMQuery },
                { role: 'user', content: `[Input]\nREADME.md:\n ${slicedText}`}],
    model: 'gpt-4o-mini'
  });
  
  if (response.choices[0].message.content.includes("[Yes]")){
    return true;
  } else{
    return false;
  }
}

const SystemLLMQuery = `
[Description]:\
You are a code reviewer. You have been assigned to review a project that is a LLM or AI-integrated workflow project with a web interface, specially these application/framework designed for user to use or train LLM or Machine Learning Model with Web UI.\
  - My ultimate goal is to find the security issues in these LLM/AI-integrated web applications.\
  - You need to make the decision based on the following criteria:\
    - Is the applicaition LLM or AI or ML integrated?
    - Is the application will start a web server for hosting the web interface so that user can interact with the application?
      (Any thing like frontend, server, self-hosting, cloud-hosting, localhost:9999, etc. menthon in the README.md?)
  - You should not return projects that are only contains the LLM or AI training codebase, like a model related to a paper. \ 

[Case Study]:
CASE 1 - mlflow/mlfolow - [Yes] - The project is a LLM or AI-integrated workflow project with a web interface based it says the application support the interactive UI.
README.md:
  MLflow is a platform to streamline machine learning development, including tracking experiments, packaging code into reproducible runs, and sharing and deploying models. MLflow offers a set of lightweight APIs that can be used with any existing machine learning application or library (TensorFlow, PyTorch, XGBoost, etc), wherever you currently run ML code (e.g. in notebooks, standalone applications or the cloud). MLflow's current components are:
  MLflow Tracking: An API to log parameters, code, and results in machine learning experiments and compare them using an interactive UI.
  MLflow Projects: A code packaging format for reproducible runs using Conda and Docker, so you can share your ML code with others.
  MLflow Models: A model packaging format and tools that let you easily deploy the same model (from any ML library) to batch and real-time scoring on platforms such as Docker, Apache Spark, Azure ML and AWS SageMaker.
  MLflow Model Registry: A centralized model store, set of APIs, and UI, to collaboratively manage the full lifecycle of MLflow Models.
  ...
  The MLflow Tracking UI will show runs logged in ./mlruns at http://localhost:5000. Start it with:
  mlflow ui
  Note: Running mlflow ui from within a clone of MLflow is not recommended - doing so will run the dev UI from source. We recommend running the UI from a different working directory, specifying a backend store via the --backend-store-uri option. Alternatively, see instructions for running the dev UI in the contributor guide.

CASE 2 - AutoGPT - [Yes] - The project is a LLM or AI-integrated workflow project with a web interface because it has frontend and server components.
README.md:
  # AutoGPT: Build, Deploy, and Run AI Agents
  [![Discord Follow](https://dcbadge.vercel.app/api/server/autogpt?style=flat)](https://discord.gg/autogpt) &ensp;
  [![Twitter Follow](https://img.shields.io/twitter/follow/Auto_GPT?style=social)](https://twitter.com/Auto_GPT) &ensp;
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  **AutoGPT** is a powerful platform that allows you to create, deploy, and manage continuous AI agents that automate complex workflows. 
  ## Hosting Options 
    - Download to self-host
    - [Join the Waitlist](https://bit.ly/3ZDijAI) for the cloud-hosted beta  
  ## How to Setup for Self-Hosting
  > [!NOTE]
  > Setting up and hosting the AutoGPT Platform yourself is a technical process. 
  > If you'd rather something that just works, we recommend [joining the waitlist](https://bit.ly/3ZDijAI) for the cloud-hosted beta.
  https://github.com/user-attachments/assets/d04273a5-b36a-4a37-818e-f631ce72d603
  This tutorial assumes you have Docker, VSCode, git and npm installed.
  ### AutoGPT Frontend
  The AutoGPT frontend is where users interact with our powerful AI automation platform. It offers multiple ways to engage with and leverage our AI agents. This is the interface where you'll bring your AI automation ideas to life:
    **Agent Builder:** For those who want to customize, our intuitive, low-code interface allows you to design and configure your own AI agents. 
    **Workflow Management:** Build, modify, and optimize your automation workflows with ease. You build your agent by connecting blocks, where each block     performs a single action.
    **Deployment Controls:** Manage the lifecycle of your agents, from testing to production.
    **Ready-to-Use Agents:** Don't want to build? Simply select from our library of pre-configured agents and put them to work immediately.
    **Agent Interaction:** Whether you've built your own or are using pre-configured agents, easily run and interact with them through our user-friendly      interface.
    **Monitoring and Analytics:** Keep track of your agents' performance and gain insights to continually improve your automation processes.
  [Read this guide](https://docs.agpt.co/server/new_blocks/) to learn how to build your own custom blocks.
  ### 💽 AutoGPT Server
  The AutoGPT Server is the powerhouse of our platform This is where your agents run. Once deployed, agents can be triggered by external sources and can operate continuously. It contains all the essential components that make AutoGPT run smoothly.
    **Source Code:** The core logic that drives our agents and automation processes.
    **Infrastructure:** Robust systems that ensure reliable and scalable performance.
    **Marketplace:** A comprehensive marketplace where you can find and deploy a wide range of pre-built agents.

CASE 3 - open-interpreter - [No] - The project is not a LLM or AI-integrated workflow project with a web interface because it runs locally through command line but not through web interface.
README.md:
  shell
  pip install open-interpreter
  Not working? Read our [setup guide](https://docs.openinterpreter.com/getting-started/setup).
  shell
  interpreter
  **Open Interpreter** lets LLMs run code (Python, Javascript, Shell, and more) locally. You can chat with Open Interpreter through a ChatGPT-like interface in your terminal by running $ interpreter after installing.
  This provides a natural-language interface to your computer's general-purpose capabilities:
  - Create and edit photos, videos, PDFs, etc.
  - Control a Chrome browser to perform research
  - Plot, clean, and analyze large datasets
  - ...etc.
  **Note: You'll be asked to approve code before it's run.**

CASE 4 - APITable/APITable - [No] - The project is not a LLM or AI-integrated workflow project with a web interface because it is not related to LLM or AI.
README.md:
  APITable provides a range of amazing features, from the personal to the enterprise.
- Advanced technology stack and open-source
  - Realtime collaboration allows multiple users to edit together in real time, or simultaneously with the Operational Transformation (OT) Algorithm.
  - Extremely smooth, user-friendly, super-fast database-spreadsheet interface in <canvas> Rendering Engine.
  - Database native architecture: Changeset / Operation / Action / Snapshot and so on.
  - **100k+** data rows with real-time collaboration.
  - Full-stack API access, from Data to Metadata.
  - One-direction / Bi-direction Table Link and Infinite Cross Links
  - Community-friendly programming languages and framework, TypeScript ([NextJS](https://nextjs.org/) + [NestJS](https://nestjs.com/)) and Java ([Spring Boot](https://spring.io/projects/spring-boot)).
- Beautiful and Rich Database-Spreadsheet UI
  - CRU: Create, Read, Update, Delete the Tables, Columns, and Rows
  - Fields Operations: sort, filter, grouping, hide/unhide, height setting.
  - Space base: Use separated workspaces in place of App/Base-based structure, make unlimited tables link together possible.
  - Dark mode and theme customization available.
  - 7 View Types: Grid View (Datasheet) / Gallery View / Mindmap View / Kanban View / Full-Feature Gantt View / Calendar View
  - One-click API Panel
- Batteries included
  - Built-in 10+ official templates.
  - Robot Automation and customization available.
  - BI dashboard
  - One-click auto-generated form
  - Shareable and embeddable page.
  - Multi-language support.
  - Integration with n8n.io / Zapier / Appsmith... and more.
- Excellent extensibility
  - Extensible Widget System with over 20 officials open-source widgets.
  - Customizable Graph & Chart & Dashboard
  - Customizable Data Column Types
  - Customizable Formulas
  - Customizable Automation Robot Actions.
- Enterprise-grade permissions
  - Mirror, turn a View into a mirror to implement Row Permission.
  - Activate Column Permission through a very simple operation.
  - Folders / Sub-Folders / Files Permission.
  - Tree structure folders and customizable node (file);
  - Team Management & Organization Structure.
- Enterprise features:
  - SAML
  - Single-Sign-On (SSO)
  - Audit
  - Database Auto Backup
  - Data Exporter
  - Watermark

[TASK]:
Please read the provided README.md (removed the new lines with \n) and determine it is the project is a LLM or AI-inregarated web application \
  - If Yes, return: [Yes], the repo is a llm-/ml- based web application becuase [YOUR_REASON] \
  - If not, return: [No], the repo is not a llm-/ml- based web application becuase [YOUR_REASON] \
`