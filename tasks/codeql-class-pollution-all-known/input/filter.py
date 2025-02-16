import os

# Define file paths
input_file_path = "/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-all-known/input/all-known-class-pollution.txt"
output_file_path = "/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-all-known/input/all-known-class-pollution_.txt"

# Read unique lines from the input file
with open(input_file_path, "r") as input_file:
    unique_lines = set(input_file.readlines())

# Write the unique lines to the output file
with open(output_file_path, "w") as output_file:
    output_file.writelines(unique_lines)