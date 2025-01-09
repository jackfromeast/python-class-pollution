import os

vuln_input_directory = 'class-pollution'
gadgets_input_directory = 'cp-gadgets'
github_base_url = 'https://github.com/jackfromeast/python-class-pollution/blob/main/class-pollution/'
output_file = 'README.md'

readme_content = """## Python Class Pollution Vulnerability and its Gadgets

> The Python World-Class Pollution: Understanding the New Python Prototype Pollution Vulnerability and its Consequnces

This repository contains a list of packages that are vulnerable to class pollution (i.e., prototype pollution in Python) and class pollution gadgets that can result in severe issues like RCE.

| Library | Type | Stars | Version | Payloads | Found By | Status | CVE | Exploitability |
|:-------:|:----:|:-----:|:-------:|----------|:--------:|:------:|:---:|:--------------:|
"""

def convert_stars_to_number(stars_str):
    if 'K' in stars_str:
        return float(stars_str.replace('K', '')) * 1000
    elif 'M' in stars_str:
        return float(stars_str.replace('M', '')) * 1000000
    else:
        return 0

def extract_metadata(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    metadata = {}
    lines = content.split('\n')
    for line in lines:
        if line.startswith("+ Library:"):
            metadata['Library'] = line.split(": ")[1]
        elif line.startswith("+ Type:"):
            metadata['Type'] = line.split(": ")[1]
        elif line.startswith("+ Exploitability:"):
            metadata['Exploitability'] = line.split(": ")[1]
        elif line.startswith("+ Input:"):
            metadata['Input'] = line.split(": ")[1]
        elif line.startswith("+ Stars:"):
            stars_str = line.split(": ")[1]
            metadata['Stars'] = stars_str
            metadata['StarsNumeric'] = convert_stars_to_number(stars_str)
        elif line.startswith("+ Version:"):
            metadata['Version'] = line.split(": ")[1]
        elif line.startswith("+ Payload:"):
            metadata['Payload'] = ''.join(line.split(": ")[1:])
        elif line.startswith("+ Impact:"):
            metadata['Impact'] = line.split(": ")[1]
        elif line.startswith("+ Foundby:"):
            metadata['Foundby'] = line.split(": ")[1]
        elif line.startswith("+ CVE:"):
            metadata['CVE'] = line.split(": ")[1]
        elif line.startswith("+ Status:"):
            metadata['Status'] = line.split(": ")[1]
    return metadata

def process_files(input_directory):
    metadata_list = []
    
    # Recursively walk through the input directory
    for root, _, files in os.walk(input_directory):
        for filename in files:
            if filename == 'README.md':  # Look for README.md in subfolders
                file_path = os.path.join(root, filename)
                metadata = extract_metadata(file_path)
                if metadata:
                    # Store the relative path to the library's folder
                    relative_path = os.path.relpath(root, input_directory)
                    metadata['filename'] = f"{relative_path}/README.md"
                    metadata_list.append(metadata)
    
    # Sort metadata by 'StarsNumeric' in descending order
    metadata_list = sorted(metadata_list, key=lambda x: x.get('StarsNumeric', 0), reverse=True)
    
    # Generate section content
    section_content = ""
    for metadata in metadata_list:
        filename = metadata['filename']
        library_link = f"[{metadata['Library']}]({github_base_url}{filename})"
        section_content += f"| {library_link} | {metadata.get('Type', 'N/A')} | {metadata.get('Stars', 'N/A')} | {metadata.get('Version', 'N/A')} | {metadata.get('Payload', 'N/A')} | {metadata.get('Input', 'N/A')} | {metadata.get('Foundby', 'N/A')} | {metadata.get('Status', 'Reported')} | {metadata.get('CVE', 'N/A')} |\n"
    
    return section_content

class_pollution_section = process_files(vuln_input_directory)

readme_content += class_pollution_section

with open(output_file, 'w') as file:
    file.write(readme_content)

print("README.md has been generated successfully.")
