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
- **Language**: Python 3.9+
- **Data Handling**: `Pandas` (for processing the data).
- **Network**: `Requests` (for direct download of the CSV files via API communication).
- **CLI**: `Argparse` for the Command Line Interface (CLI).


## 📋 How to Use
1. Clone the repo: `git clone https://github.com/cardsX/SNB-Data-Streamliner.git`
2. `cd SNB-Data-Streamliner`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the script: `python -m src --help`

### :books: Documentation of the Command Line Interface
```bash
usage: python -m src [-h] [-v] [-s] [--info] [--version] cubes [cubes ...]

SNB Data Streamliner: Extract and structure SNB data cubes.

positional arguments:
  cubes          The name of the SNB data cube (e.g., 'devlandm')

options:
  -h, --help     show this help message and exit
  -v, --verbose  Increase output verbosity
  -s, --save     Save the extracted data to the /data folder. If not set, processing stays in RAM.
  --info         Display all supported cubes Id with description.
  --version      Display the version number.

SNB data portal: 'https://data.snb.ch/en'.
```

### 🐍 Interactive Usage (API)
For more advanced users, `SNB-Data-Streamliner` can be imported as a Python module. The interactive mode offers greater flexibility, allowing for specific operations during the download process.

#### ✨ Advanced Options
1. Column Selection: Load only the specific dimensions you need, reducing memory usage.
2. Date Filtering: Restrict data extraction to specific time ranges (e.g., last 5 years or a specific quarter).
3. Custom Post-processing: Apply transformations or cleaning logic before saving the file.
4. Specify a different download directory.

The advance capabilities are available by the methods `download_to_file`, `download_to_files` and `download_to_dataframe` with the parameter `selection: str` through the parameter `selection: str` and `config: dict`. 


| Parameter | Accepted Values | Description |
| :--- | :--- | :--- |
| `outputFormat` | `nonPivoted`, `pivoted` | Defines the data structure. Use `nonPivoted` (Long) for database integration (default) or `pivoted` (Wide) for human-readable spreadsheets. |
| `fromDate` | `YYYY-MM` (e.g., `2015-01`) | The starting point for the data series. Helps reduce file size for long-running datasets. |
| `toDate` | `YYYY-MM` (e.g., `2023-12`) | The end point for the data series. |
| `lang` | `en`, `de`, `fr`, `it` | Sets the language for column headers and categorical metadata descriptions. |
| `frequence` | `D`, `M`, `Q`, `A` | Specifies the data granularity (Daily, Monthly, Quarterly, or Annual) if supported by the cube. |
| `outputNumberFormat` | `fixed`, `formatted` | `fixed` returns raw numbers (e.g., `1000.50`), while `formatted` may include thousands separators. |
| `selection` | *Dimension Slugs* | Applies a "Slice" to the cube, filtering for specific dimensions (e.g., specific currencies, sectors, or regions). |


##### ⚠️ Important Disclaimer: Parameter Configuration
> [!IMPORTANT]
> **Handle with care**: The selection and `fromDate`/`toDate` parameters interact directly with the SNB's internal database structure.
>
> * **Dimensional Integrity**: The selection string (e.g., `D0,I1`) must follow the exact order and number of dimensions specific to the cube you are requesting. Providing incorrect codes or an invalid sequence will result in an **HTTP 400 Bad Request** or an empty dataset.
> * **Date Constraints**: Ensure that `fromDate` is not later than `toDate` and that the requested range actually contains data.
> * **Validation**: This tool does not pre-validate your custom selection strings. It is recommended to verify the correct dimension slugs on the [SNB Data Portal](https://data.snb.ch/) before using them in interactive mode.


##### 🛠️ Code Example
```python
from src.extractor import SNBDataEngine


cube = 'iucurracpa'
download_folder = "data/raw"
params = {
    'lang': 'de',
    'fromDate': '2024-05',
    'toDate': '2024-05',
    'outputFormat': 'nonPivoted',
    'outputNumberFormat': 'fixed'
}
with SNBDataEngine(logging_verbosity='v') as snb:
    path = snb.download_to_file(cube, folder=download_folder, **params)
```
This special request is encoded in the transmitted url as `https://data.snb.ch/api/cube/iucurracpa/data/csv/en?outputFormat=nonPivoted&lang=de&fromDate=2024-05&toDate=2024-05&outputNumberFormat=fixed`.


## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
