This project aims to:

* Systematically catalog Python get/set operations
* Provide testable examples for each case
* Serve as a reference for CodeQL rule writing

### Directory Structure
```
get-set-taxonomy/
├── test-codebase/           # Source files implementing get/set expressions
│   ├── getattr.py
│   ├── getitem.py
│   ├── set.py
│   ├── eval\_and\_exec.py
│   └── ...
│
├── test-checker/            # Unit test files validating codebase functionality
│   ├── check\_getattr.py
│   ├── check\_getitem.py
│   ├── check\_set.py
│   ├── check\_eval\_and\_exec.py
│   └── ...
│
├── run\_checkers.py          # Unified runner that executes all checkers
└── README.md
```

### Run all checkers at once
```bash
python3.11 run_checkers.py
````