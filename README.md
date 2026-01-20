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
snb-data-streamliner/
├── src/                # Source code
│   ├── main.py         # Entry point
│   └── extractor.py    # Core logic for data parsing
├── data/               # Local storage for outputs (git-ignored)
├── requirements.txt    # Python dependencies
└── LICENSE             # MIT License
```

## 🛠️ Tech Stack
- **Language**: Python 3.x
- **Libraries**: `requests` (API communication), `pandas` (data structuring).

## 📋 How to Use
1. Clone the repo: `git clone ...`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the script: `python src/main.py`
