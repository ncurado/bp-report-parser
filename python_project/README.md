# 🩺 smartBP: Aktiia Blood Pressure Data Extractor

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-CC%20BY--SA%204.0-green.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A powerful Python tool that extracts blood pressure data from Aktiia PDF reports and converts them to structured CSV format. Features comprehensive configuration management, medical validation, and robust error handling.

## ✨ Features

- 📊 **PDF to CSV Conversion**: Extract structured BP data from Aktiia PDF reports
- ⚙️ **Configuration Management**: Flexible YAML/JSON configuration system
- 🔍 **Medical Validation**: Built-in validation for BP and heart rate ranges
- 📈 **Progress Tracking**: Real-time progress bars and detailed status reporting
- 🛡️ **Robust Error Handling**: Comprehensive error handling with graceful fallbacks
- 🔧 **Customizable Patterns**: Adaptable regex patterns for different PDF formats
- 📝 **Multiple Output Formats**: Configurable CSV headers and delimiters
- 🚀 **Easy Configuration**: Simple command-line configuration management

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ncurado/smartBP.git
   cd smartBP/python_project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Extract your first report**:
   ```bash
   python src/bp_extractor.py your_aktiia_report.pdf output.csv
   ```

## 📖 Usage

### Basic Usage

```bash
# Simple extraction
python src/bp_extractor.py input.pdf output.csv

# With detailed status information
python src/bp_extractor.py input.pdf output.csv --status

# Using custom configuration
python src/bp_extractor.py input.pdf output.csv --config my_config.yaml
```

### Configuration Management

**Create a configuration file**:
```bash
# Generate default configuration
python src/bp_extractor.py --create-config

# Create configuration at specific location
python src/bp_extractor.py --create-config --config custom_config.yaml
```

**Example configuration** (`bp_extractor_config.yaml`):
```yaml
# Date and time formats
input_date_format: "%d %B, %y %H:%M"
output_date_format: "%m/%d/%y %H:%M"

# Data extraction pattern
bp_data_pattern: "(\\d{1,2}\\s\\w+,\\s\\d{2})\\s(\\d{2}:\\d{2})\\s+(\\d+)\\s+(\\d+)\\s+(\\d+)"

# CSV output settings
csv_headers: ["Date/Time", "Systolic", "Diastolic", "Pulse"]
csv_delimiter: ","

# Processing options
skip_first_page: true
progress_bar: true

# Medical validation ranges
min_systolic: 50
max_systolic: 300
min_diastolic: 30
max_diastolic: 200
min_heart_rate: 30
max_heart_rate: 250
```

## 🏗️ Project Structure

```
smartBP/python_project/
├── 📁 src/
│   ├── bp_extractor.py      # Main extraction script
│   ├── config.py            # Configuration management
│   └── __init__.py
├── 📁 tests/                # Unit tests
├── 📄 requirements.txt      # Dependencies
├── 📄 bp_extractor_config.yaml  # Default configuration
├── 📄 CONFIG_README.md      # Configuration documentation
├── 📄 setup.py              # Package setup
└── 📄 README.md             # This file
```

## 🔧 Command Line Options

| Option | Description |
|--------|-------------|
| `input_pdf` | Path to the Aktiia PDF report |
| `output_csv` | Output CSV file path |
| `--config` | Path to configuration file (YAML/JSON) |
| `--status` | Show detailed processing status |
| `--create-config` | Generate default configuration file |
| `--help` | Display help information |

## 📊 Output Format

The extracted CSV contains:

| Column | Description | Example |
|--------|-------------|----------|
| Date/Time | Measurement timestamp | `06/25/25 14:30` |
| Systolic | Systolic pressure (mmHg) | `120` |
| Diastolic | Diastolic pressure (mmHg) | `80` |
| Pulse | Heart rate (BPM) | `72` |

**Sample output**:
```csv
Date/Time,Systolic,Diastolic,Pulse
06/25/25 14:30,120,80,72
06/25/25 15:45,118,78,68
06/25/25 17:20,125,82,75
```

## 🛡️ Medical Validation

The tool includes built-in validation to ensure data quality:
- **Systolic BP**: 50-300 mmHg
- **Diastolic BP**: 30-200 mmHg  
- **Heart Rate**: 30-250 BPM
- **Date Format**: Validates timestamp parsing
- **Warning System**: Alerts for out-of-range values

## 🔍 Status Tracking

With the `--status` flag, get detailed information:
- ✅ Processing status (Not Started/Processing/Completed/Failed)
- 📊 Progress percentage and page count
- 📈 Records found and processing speed
- ⏱️ Elapsed time
- ⚠️ Error details and warnings

## 🔧 Advanced Configuration

For detailed configuration options, see [CONFIG_README.md](CONFIG_README.md).

### Adapting to Different PDF Formats

1. **Create custom config**: `python src/bp_extractor.py --create-config --config custom.yaml`
2. **Modify regex pattern**: Update `bp_data_pattern` for your PDF format
3. **Adjust date formats**: Change `input_date_format` and `output_date_format`
4. **Set validation ranges**: Customize medical validation limits

## 🧪 Development

### Requirements
- Python 3.11+
- Dependencies: `pdfplumber`, `PyYAML`, `tqdm`, `argparse`

### Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Running Tests

```bash
# Run tests (when implemented)
python -m pytest tests/

# Test configuration system
python src/bp_extractor.py --create-config
python src/bp_extractor.py sample.pdf output.csv --config bp_extractor_config.yaml --status
```

## 📋 Changelog

### v1.1.0 (Latest)
- ✨ Added comprehensive configuration management system
- 🔧 Flexible YAML/JSON configuration support
- 🛡️ Medical validation with configurable ranges
- 📊 Enhanced progress tracking and status reporting
- 🔍 Improved error handling and validation warnings
- 📝 Comprehensive documentation

### v1.0.0
- 🎉 Initial release
- 📊 Basic PDF to CSV extraction
- 📈 Progress bar support
- ⚠️ Error handling

## 🤝 Support

- 📖 **Documentation**: See [CONFIG_README.md](CONFIG_README.md) for detailed configuration
- 🐛 **Issues**: [Report bugs](https://github.com/ncurado/smartBP/issues)
- 💬 **Discussions**: [Ask questions](https://github.com/ncurado/smartBP/discussions)

## 📄 License

This work is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).

## 👨‍💻 Author

**Nuno Curado**
- 📧 Email: ncurado@gmx.com
- 🐙 GitHub: [@ncurado](https://github.com/ncurado)

---

⭐ **Star this repository if you find it helpful!**
