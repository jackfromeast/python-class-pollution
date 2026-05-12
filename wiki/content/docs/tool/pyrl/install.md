---
title: "Installation"
weight: 1
---

# Installing Pyrl

## Prerequisites

- Python 3.10+
- [CodeQL CLI](https://github.com/github/codeql-cli-binaries) v2.21.3 or later
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/jackfromeast/python-class-pollution.git
cd python-class-pollution
```

### 2. Install Python Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 3. Install CodeQL CLI

Download the CodeQL CLI from the [official releases](https://github.com/github/codeql-cli-binaries/releases):

```bash
# Linux/macOS
wget https://github.com/github/codeql-cli-binaries/releases/download/v2.21.3/codeql-linux64.zip
unzip codeql-linux64.zip
export PATH="$PWD/codeql:$PATH"

# Verify installation
codeql version
```

### 4. Download CodeQL Libraries

```bash
# Clone the CodeQL standard libraries
git clone https://github.com/github/codeql.git codeql-repo
```

### 5. Verify Installation

```bash
# Check Pyrl is accessible
python -m pyrl --help
```

## Docker (Alternative)

If you prefer containerized setup:

```bash
docker build -t pyrl .
docker run -v $(pwd)/target:/target pyrl analyze /target
```

## Troubleshooting

### CodeQL version mismatch
Pyrl requires CodeQL v2.21.3+ with Python language support v4.0.5. Check with:
```bash
codeql version
codeql resolve languages  # Should show python
```

### Python version
Pyrl requires Python 3.10+:
```bash
python --version  # Must be >= 3.10
```
