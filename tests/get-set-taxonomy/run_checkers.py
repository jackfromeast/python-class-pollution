import unittest
import os
import sys

# Add ./test-codebase to sys.path so test-checker can import from it
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CURRENT_DIR, "test-codebase"))

def main():
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(CURRENT_DIR, "test-checker"),
        pattern="check_*.py"
    )
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    main()
