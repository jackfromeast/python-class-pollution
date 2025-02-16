def get_non_overlapping_lines(file1, file2, output_file):
    """
    Compare two text files and write non-overlapping lines to an output file.

    :param file1: Path to the first text file.
    :param file2: Path to the second text file.
    :param output_file: Path to the output file for non-overlapping lines.
    """
    try:
        # Read the contents of the files into sets
        with open(file1, 'r') as f1:
            lines1 = set(line.strip() for line in f1 if line.strip())

        with open(file2, 'r') as f2:
            lines2 = set(line.strip() for line in f2 if line.strip())

        # Find non-overlapping lines
        non_overlapping = lines1.symmetric_difference(lines2)

        # Write non-overlapping lines to the output file
        with open(output_file, 'w') as output:
            for line in sorted(non_overlapping):
                output.write(line + '\n')

        print(f"Non-overlapping lines have been written to {output_file}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
file1_path = '/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K-has-python/input/has-python-github-repo-Top-1K-20100101-20241001.txt'  # Replace with the path to your first file
file2_path = '/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K-r2/input/github-20141001-20241001-stars-1000.txt'  # Replace with the path to your second file
output_path = '/home/jackfromeast/Desktop/python-class-pollution/tasks/codeql-class-pollution-1K-has-python/input/has-python-github-repo-Top-1K-20100101-20241001-no-overlap.txt'  # Replace with your desired output file path

get_non_overlapping_lines(file1_path, file2_path, output_path)
