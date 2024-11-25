import os

vuln_input_directory = 'class-pollution'
gadgets_input_directory = 'cp-gadgets'
github_base_url = 'https://github.com/jackfromeast/python-class-pollution/class-pollution/'
output_file = 'README.md'

readme_content = """## Python Class Pollution Vulnerability and its Gadgets

> A snake in the (polluted) grass

This repository contains a list of package that are vulnerable to class pollution (i.e., prototype pollution in python) and class pollution gadgets that can result in severe issues like RCE.

| Library | Stars | Version | Payloads | Found By | Status | CVE |
|:-------:|:-----:|:-------:|----------|:--------:|:------:|:---:|
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
        elif line.startswith("+ Stars:"):
            stars_str = line.split(": ")[1]
            metadata['Stars'] = stars_str
            metadata['StarsNumeric'] = convert_stars_to_number(stars_str)
        elif line.startswith("+ Version:"):
            metadata['Version'] = line.split(": ")[1]
        else:
            if line.startswith("+ Payload:"):
                metadata['Payload'] = ''.join(line.split(": ")[1:])
            elif line.startswith("+ Impact:"):
                metadata['Impact'] = line.split(": ")[1]
            elif line.startswith("+ Foundby:"):
                metadata['Foundby'] = line.split(": ")[1]
        if line.startswith("+ CVE:"):
            metadata['CVE'] = line.split(": ")[1]
        elif line.startswith("+ Status:"):
            metadata['Status'] = line.split(": ")[1]
    return metadata

def process_files(input_directory):
    metadata_list = []
    for filename in sorted(os.listdir(input_directory)):
        if filename.endswith('.md'):
            file_path = os.path.join(input_directory, filename)
            metadata = extract_metadata(file_path)
            if metadata:
                metadata['filename'] = filename  # Store the filename for later use
                metadata_list.append(metadata)
    
    metadata_list = sorted(metadata_list, key=lambda x: x.get('StarsNumeric', 0), reverse=True)
    
    section_content = ""
    for metadata in metadata_list:
        filename = metadata['filename']
        library_link = f"[{metadata['Library']}]({github_base_url}{filename})"
        section_content += f"| {library_link} | {metadata.get('Stars', 'N/A')} | {metadata.get('Version', 'N/A')} | {metadata.get('Payload', 'N/A')} | {metadata.get('Foundby', 'N/A')} | {metadata.get('Status', 'Reported')} | {metadata.get('CVE', 'N/A')} |\n"
    
    return section_content

class_pollution_section = process_files(vuln_input_directory)

readme_content += class_pollution_section

with open(output_file, 'w') as file:
    file.write(readme_content)

print("README.md has been generated successfully.")