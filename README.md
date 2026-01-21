# SNB Data Streamliner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Python tool designed to automate the extraction of complex data cubes from the Swiss National Bank (SNB) open data portal. It simplifies the transition from raw, nested API responses to structured, analysis-ready formats.

## 🎯 Purpose
The SNB provides high-quality economic data, but navigating its hierarchical "data cubes" manually can be time-consuming. This tool acts as a bridge, automating the retrieval process and eliminating the friction of manual data collection.

## ✨ Key Features
- **Automated Retrieval**: Programmatically fetches the latest data from SNB web resources.
- **Structural Flattening**: Converts complex, multi-layered JSON/RSS structures into clean, tabular formats.
- **Efficiency**: Designed to be integrated into larger data pipelines or used as a standalone tool to save time.

## 📂 Project Structure
```text
SNB-Data-Streamliner/
├── src/                # Source code
│   ├── __init__.py     # Module declaration
│   ├── __main__.py     # Entry point
│   └── extractor.py    # Core logic for data parsing (module)
├── metadata/           # Data included in the package (for distribution)
|   └── cube_list.csv   # CSV-file containing all(?) the cubes' ID and descriptions
├── data/               # Local storage for outputs (git-ignored)
│   └── raw/            # Default location of saved cubes (created automatically at run time if not present)
├── pyproject.toml      # Project's configuration
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
└── README.md           # This file
```

## 🛠️ Tech Stack
- **Language**: Python 3.x
- **Libraries**: `requests` (API communication), `pandas` (data structuring).

## 📋 How to Use
1. Clone the repo: `git clone https://github.com/cardsX/SNB-Data-Streamliner.git`
2. `cd SNB-Data-Streamliner`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the script: `python -m src --help`

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
