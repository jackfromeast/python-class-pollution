## **1 Results**

We are using the google sheet for summerizing all the results, which link is as follows.

https://docs.google.com/spreadsheets/d/1Ncr7LVNmu4p7ZUOc5h3eo50_GV35g3yuyKwsP5U-Suk/edit?gid=1085660249#gid=1085660249

### 1.1 Tables

- **All-in-one**
    - Read-only Result which contains all the verified true positives
    - The table is dynamically generated from scripts based on table **Github-Top-1k-0329** and **Github-Top-100-0331**
    - Note: Please don’t update any data there!
- **Github-Top-1k-0329**
    - Repositories with alerted function-level class pollution vulnerability found from Github repositories with more than 1K stars
    - The listed repo only means that there is a function which contains class pollution behavior. It does not guarantee that the vulnerability can be triggered remotely, locally, or through library APIs.
    - The associated raw CodeQL SARIF file will be available at: **TODO**
- **Github-Top-100-0331**
    - Repositories with alerted function-level class pollution vulnerability found from Github repositories with 100-1K stars
    - The listed repo only means that there is a function which contains class pollution behavior. It does not guarantee that the vulnerability can be triggered remotely, locally, or through library APIs.
    - The associated raw CodeQL SARIF file will be available at: **TODO**
- Agent-Remote-1000 and Agent-Remote-100
    - Raw results from an LLM based agent that verified can be triggered remotely based on the function-level from the above two lists.
    - Read-only Result which contains all the verified true positives

### 1.2 Headers

The first three tables share the same header. Tables Agent-Remote-1000 and Agent-Remote-100 are only for reference, please update the result to the **Github-Top-1k-0329 and Github-Top-100-0331 table for persistent tracking.**

<img width="1694" alt="tmp-2025-05-16_18-58-57" src="https://github.com/user-attachments/assets/18fbb742-1028-4b5f-92fb-a3e9ac7f44c6" />

- **General Meta Data**
    - **Application**: Name of the repository or project.
    - **Stars**: GitHub stars as an indicator of popularity.
    - **URL**: Link to the repository.
- **Class Pollution Vulnerability**
    
    *(Core vulnerability logic)*
    
    - **CodeQL**: Indicates if the current CodeQL query can detect this vulnerability. *(Earlier versions struggled with some manually discovered cases.)*
    - **Confirmed**: Whether there is a **class pollution function (the core logic)**—i.e., if an attacker can control the relevant function parameters (`key`, `value`) to exploit class pollution. (Used to filter out false positives caused by sanitization, type checks, or fixed values.)
    - **FP Reason**: If it cannot be triggered at the function level, this explains why (e.g., sanitization, unreachable code, etc.).
    - **Types**: Categorization of the vulnerability according to our class pollution taxonomy.
- **Input Feasibility**
    
    (Exploitability)
    
    - **Triggering**: Whether an attacker can realistically trigger the vulnerability by controlling both the key and value—remotely, locally, or via exposed library APIs.
    - **Remote Patterns**: Presence of request handlers or other remote entry points. (This is heuristic-based and may be incomplete.)
    - **Local Patterns**: Indicators of local-level entry points.
- **Status**
    - Current status of the vulnerability.
        
        If confirmed as a true positive and triggerable (remotely, locally, or via library APIs), it should be considered for reporting.
        
- **Comment**
    - Any additional notes or observations regarding the case.
- **New**
    - Marks newly added cases for easier tracking.

## Verification Steps

For each row in **Github-Top-1k-0329** and **Github-Top-100-0331,**

1. Check if the repo exists in the Agent-Remote-* sheets as well. Currently, due to the time limits, we only focus on these repositories that can potentially triggered remotely determined by LLM. 
2. Function-level Verification
    1. Found the CodeQL SARIF file from the Github and download the repo source code (TODO: I am considering putting all the results on a shared server)
    2. Analyze the function to verify the class pollution behavior.
    3. Based on the analysis, update the following columns:
        - **Confirmed**: Whether the vulnerability can be triggered at the function level (with controllable key & value).
        - **FP Reason**: If not confirmed, document the reason (e.g., sanitization, fixed values).
3. External Triggering
    1. If the vulnerability is valid at the function level, check the **Agent-Remote-**results to see if it could be triggered remotely or locally.
    2. If it shows potential for exploitation:
        - Set up the target repository locally.
        - You may need to write small piece of application code to drive the framework.
    3. Dynamically trigger the vulnerability by interacting with the running sample.
    4. Update the “Triggering” column accordingly.
