#!/bin/bash

# Function to print commands in green
print_command() {
    echo -e "\033[0;32m\$ $1\033[0m"
}

# Change directory
print_command "cd codeql-query/class-pollution-all"
cd codeql-query/class-pollution-all || exit

# Install CodeQL pack
print_command "codeql pack install"
codeql pack install

# Compile query
print_command "codeql query compile class-pollution.qls"
codeql query compile class-pollution.qls

# Install pip dependency
print_command "python3 -m pip install psutil PyYAML packageurl-python ruamel.yaml"
python3 -m pip install psutil PyYAML packageurl-python ruamel.yaml langgraph langchain-deepseek