# Blood Pressure Data Extractor

A Python tool to extract blood pressure data from Aktiia PDF reports and convert them to CSV format.

## Project Structure

```markdown
python_project/
│
├── src/                    # Source code
│   ├── __init__.py
│   └── bp_extractor.py    # Main script for BP data extraction
│
├── tests/                  # Test files
│   └── __init__.py
│
├── docs/                   # Documentation
│
├── data/                   # Data files
│   ├── raw/               # Raw PDF reports
│   └── processed/         # Processed CSV files
│
├── notebooks/             # Jupyter notebooks
│
├── requirements.txt       # Project dependencies
├── setup.py              # Package setup file
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## Setup

1. Activate the conda environment:

```bash
conda activate python311-env
```

```bash
pip install -r requirements.txt
```

## Usage

The script accepts two command-line arguments and one optional flag:

1. Path to the input PDF file

2. Path where the output CSV file should be saved

3. Optional: --status flag to show detailed processing information

Example usage:

```bash
# Basic usage
python src/bp_extractor.py data/raw/AktiiaReport.pdf data/processed/output.csv

# With status tracking
python src/bp_extractor.py data/raw/AktiiaReport.pdf data/processed/output.csv --status
```

### Command Line Arguments

- `input_pdf`: Path to the Aktiia PDF report file
- `output_csv`: Path where the CSV file should be saved
- `--status`: Optional flag to display detailed processing information

### Status Tracking

When run with the `--status` flag, the script provides detailed information about:

- Current processing status (Not Started/Processing/Completed/Failed)
- Progress percentage
- Number of pages processed
- Number of records found
- Time elapsed
- Any errors encountered

The script also shows a progress bar during processing, allowing you to monitor the extraction in real-time.

### Output Format

The script generates a CSV file with the following columns:

- Date/Time (format: MM/DD/YY HH:MM in 24-hour time)
- Systolic
- Diastolic
- Pulse

For example:

```
Date/Time,Systolic,Diastolic,Pulse
10/15/23 14:30,120,80,72
```

## Error Handling

The script includes error handling for common scenarios:

- Invalid PDF files
- Missing input files
- Permission issues when writing output
- Invalid date formats
- General exceptions

Each error is logged with detailed information when using the --status flag.

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Submit a pull request

## License

Specify your license.
