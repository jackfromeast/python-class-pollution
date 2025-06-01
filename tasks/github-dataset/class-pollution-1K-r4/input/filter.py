# Read URLs from a file
with open('/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K-r3/input/github-20101001-20241001-stars-1000.txt', 'r') as file:
    urls = file.read().splitlines()

# Remove duplicates by converting the list to a set and back to a sorted list
unique_urls = sorted(set(urls))

# Write the unique URLs to a new file
with open('/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K-r3/input/github-20101001-20241001-stars-1000.txt', 'w') as output_file:
    for url in unique_urls:
        output_file.write(url + '\n')
