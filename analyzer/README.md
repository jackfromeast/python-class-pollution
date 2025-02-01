This folder contains the source code used to analyze the class-pollution vulnerability using CodeQL.

The followings are introduction for each folder.

**/codeql_driver**

This folder holds the code that drives CodeQL to perform an analysis, including:

+ Fetching source code from GitHub repositories or PyPI packages
+ Building the CodeQL database
+ Running specific CodeQL queries
+ Summarizing and reporting the resulting findings