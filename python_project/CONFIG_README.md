# Configuration Management

The BP Extractor now supports flexible configuration management to customize extraction behavior for different PDF formats and requirements.

## Overview

Configuration management has been added to make the BP extractor more flexible and maintainable. All previously hard-coded constants have been moved to configurable settings that can be customized via YAML or JSON files.

## Configuration Features

### 1. **Configurable Settings**

- **Date/Time Formats**: Customize input and output date formats
- **Regex Pattern**: Modify the pattern used to extract BP data from PDF text
- **CSV Output**: Configure headers, delimiter, and formatting
- **Processing Options**: Control page skipping and progress bar display
- **Validation Ranges**: Set acceptable ranges for BP and heart rate values

### 2. **Configuration File Formats**

The extractor supports both YAML and JSON configuration files:

- **YAML** (recommended): `bp_extractor_config.yaml`
- **JSON**: `bp_extractor_config.json`

### 3. **Configuration File Locations**

The extractor looks for configuration files in the following order:

1. Custom path specified via `--config` argument
2. Current working directory: `bp_extractor_config.yaml`
3. Script directory: `src/bp_extractor_config.yaml`
4. User config directory: `~/.config/bp_extractor/bp_extractor_config.yaml`

If no configuration file is found, default settings are used.

## Usage

### Creating a Configuration File

Generate a default configuration file:

```bash
python -m src.bp_extractor --create-config
```

Create a configuration file at a specific path:

```bash
python -m src.bp_extractor --create-config --config my_config.yaml
```

### Using a Custom Configuration

```bash
python -m src.bp_extractor input.pdf output.csv --config my_config.yaml
```

### Example Configuration File (YAML)

```yaml
# Date and Time Format Settings
input_date_format: "%d %B, %y %H:%M"    # Format in PDF (e.g., "25 June, 25 14:30")
output_date_format: "%m/%d/%y %H:%M"    # Format in CSV (e.g., "06/25/25 14:30")

# Data Extraction Pattern
bp_data_pattern: "(\d{1,2}\s\w+,\s\d{2})\s(\d{2}:\d{2})\s+(\d+)\s+(\d+)\s+(\d+)"

# CSV Output Settings
csv_headers:
  - "Date/Time"
  - "Systolic"
  - "Diastolic" 
  - "Pulse"
csv_delimiter: ","

# Processing Settings
skip_first_page: true      # Skip the first page (headers/info)
progress_bar: true         # Show progress bar during processing

# Validation Ranges (medical ranges)
min_systolic: 50
max_systolic: 300
min_diastolic: 30
max_diastolic: 200
min_heart_rate: 30
max_heart_rate: 250
```

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_date_format` | string | `"%d %B, %y %H:%M"` | Python strftime format for parsing PDF dates |
| `output_date_format` | string | `"%m/%d/%y %H:%M"` | Python strftime format for CSV output |
| `bp_data_pattern` | string | Regex pattern | Regular expression to extract BP data |
| `csv_headers` | list | `["Date/Time", "Systolic", "Diastolic", "Pulse"]` | CSV column headers |
| `csv_delimiter` | string | `","` | CSV field delimiter |
| `skip_first_page` | boolean | `true` | Whether to skip the first PDF page |
| `progress_bar` | boolean | `true` | Whether to show processing progress |
| `min_systolic` | integer | `50` | Minimum valid systolic BP (mmHg) |
| `max_systolic` | integer | `300` | Maximum valid systolic BP (mmHg) |
| `min_diastolic` | integer | `30` | Minimum valid diastolic BP (mmHg) |
| `max_diastolic` | integer | `200` | Maximum valid diastolic BP (mmHg) |
| `min_heart_rate` | integer | `30` | Minimum valid heart rate (BPM) |
| `max_heart_rate` | integer | `250` | Maximum valid heart rate (BPM) |

## Benefits

### 1. **Flexibility**
- Easily adapt to different PDF formats by modifying the regex pattern
- Support multiple date/time formats without code changes
- Customize output format and validation ranges

### 2. **Maintainability**
- No need to modify code for different PDF layouts
- Configuration changes can be version controlled separately
- Easy to test different settings

### 3. **Validation**
- Built-in validation for medical ranges
- Automatic skipping of invalid readings
- Warning messages for data quality issues

### 4. **User Experience**
- Simple command-line configuration management
- Clear error messages and fallback to defaults
- Optional progress bar control

## Migration Notes

This update is backward compatible. Existing scripts will continue to work using default settings. No changes are required unless you want to customize the behavior.

The configuration system automatically handles missing configuration files and invalid settings by falling back to sensible defaults.
