"""
Author: Nuno Curado
Date: 25th of June, 2025
Version: 1.0

License:
This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

#!/usr/bin/env python3

import pdfplumber
import csv
import re
import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

try:
    from .config import get_config, ConfigManager, ExtractionConfig
except ImportError:
    # Handle case when running directly as script
    from config import get_config, ConfigManager, ExtractionConfig


class ProcessingState(Enum):
    """Enumeration of possible processing states."""
    NOT_STARTED = "Not Started"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"


@dataclass
class BPRecord:
    """Data class representing a blood pressure record."""
    datetime: str
    systolic: int
    diastolic: int
    heart_rate: int

    @classmethod
    def from_match(cls, date_str: str, time_str: str, sys: str, dia: str, hr: str, config: ExtractionConfig) -> 'BPRecord':
        """Create a BPRecord from matched strings."""
        date_obj = datetime.strptime(f"{date_str} {time_str}", config.input_date_format)
        return cls(
            datetime=date_obj.strftime(config.output_date_format),
            systolic=int(sys),
            diastolic=int(dia),
            heart_rate=int(hr)
        )

    def to_list(self) -> List[str]:
        """Convert record to list format for CSV writing."""
        return [self.datetime, str(self.systolic), str(self.diastolic), str(self.heart_rate)]


class ProcessingStatus:
    """
    Tracks and manages the status of PDF processing operations.

    This class maintains information about the progress of processing a PDF file,
    including page counts, timing, and error states.
    """

    def __init__(self) -> None:
        """Initialize a new processing status tracker."""
        self.total_pages: int = 0
        self.current_page: int = 0
        self.records_found: int = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.status: ProcessingState = ProcessingState.NOT_STARTED
        self.error: Optional[str] = None
        self._progress_bar: Optional[tqdm] = None

    def __enter__(self) -> 'ProcessingStatus':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if exc_type is not None:
            self.fail(str(exc_val))
        else:
            self.complete()
        if self._progress_bar:
            self._progress_bar.close()

    def start(self, total_pages: int, show_progress: bool = True) -> None:
        """
        Start processing with the given total number of pages.

        Args:
            total_pages: The total number of pages to process
            show_progress: Whether to show progress bar
        """
        if total_pages < 0:
            raise ValueError("Total pages cannot be negative")
        self.total_pages = total_pages
        self.start_time = time.time()
        self.status = ProcessingState.PROCESSING
        if show_progress:
            self._progress_bar = tqdm(total=total_pages, desc="Processing pages")

    def update(self, page: int, records: int) -> None:
        """
        Update the current processing status.

        Args:
            page: Current page being processed
            records: Total number of records found so far
        """
        if page < 0 or records < 0:
            raise ValueError("Page and records count cannot be negative")
        self.current_page = page
        self.records_found = records
        if self._progress_bar:
            self._progress_bar.update(1)
            self._progress_bar.set_postfix(records=records)

    def complete(self) -> None:
        """Mark the processing as completed."""
        self.end_time = time.time()
        self.status = ProcessingState.COMPLETED

    def fail(self, error_msg: str) -> None:
        """
        Mark the processing as failed with an error message.

        Args:
            error_msg: Description of the error that occurred
        """
        self.end_time = time.time()
        self.status = ProcessingState.FAILED
        self.error = error_msg

    @property
    def progress(self) -> float:
        """
        Calculate the current progress percentage.

        Returns:
            float: Progress percentage from 0 to 100
        """
        if self.total_pages == 0:
            return 0
        return (self.current_page / self.total_pages) * 100

    @property
    def duration(self) -> float:
        """
        Calculate the elapsed processing time.

        Returns:
            float: Duration in seconds
        """
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def get_status_report(self) -> str:
        """
        Generate a comprehensive status report.

        Returns:
            str: Formatted status report including progress, timing, and any errors
        """
        report = [
            f"Status: {self.status.value}",
            f"Progress: {self.progress:.1f}%",
            f"Pages Processed: {self.current_page}/{self.total_pages}",
            f"Records Found: {self.records_found}",
            f"Time Elapsed: {self.duration:.1f} seconds"
        ]
        if self.error:
            report.append(f"Error: {self.error}")
        return "\n".join(report)


def extract_bp_data(pdf_path: str, csv_output_path: str, status: Optional[ProcessingStatus] = None, config: Optional[ExtractionConfig] = None) -> bool:
    """
    Extract blood pressure data from a PDF file and save it to a CSV file.
    
    Args:
        pdf_path: Path to the input PDF file
        csv_output_path: Path to save the output CSV file
        status: Optional status tracking object
        config: Optional configuration object

    Returns:
        bool: True if successful, False otherwise
    """
    if status is None:
        status = ProcessingStatus()
    
    if config is None:
        config = get_config()

    try:
        # Verify input file exists
        if not Path(pdf_path).is_file():
            error_msg = f"Input file '{pdf_path}' does not exist"
            status.fail(error_msg)
            print(f"Error: {error_msg}")
            return False

        # Lists to store the extracted data
        records: List[BPRecord] = []
        
        # Compile regex pattern from config
        pattern = config.get_compiled_pattern()

        with pdfplumber.open(pdf_path) as pdf:
            # Calculate pages to process based on configuration
            start_page = 1 if config.skip_first_page else 0
            pages_to_process = len(pdf.pages) - start_page
            
            # Initialize status
            status.start(pages_to_process, config.progress_bar)

            # Iterate through pages
            for i in range(start_page, len(pdf.pages)):
                page = pdf.pages[i]
                text = page.extract_text()

                # Extract the lines with BP data
                lines = text.split('\n')
                for line in lines:
                    # Match lines containing Date, Time, SBP, DBP, HR using config pattern
                    match = pattern.match(line)
                    if match:
                        try:
                            record = BPRecord.from_match(*match.groups(), config)
                            
                            # Validate BP values if configured
                            if config.validate_bp_values(record.systolic, record.diastolic, record.heart_rate):
                                records.append(record)
                            else:
                                print(f"Warning: Skipping invalid BP values: {record.systolic}/{record.diastolic} HR:{record.heart_rate}")
                        except ValueError as e:
                            print(f"Warning: Skipping invalid date format in line: {line} ({e})")

                status.update(i - start_page + 1, len(records))

        # Create output directory if it doesn't exist
        output_dir = Path(csv_output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write the extracted data to a CSV file using config settings
        with open(csv_output_path, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=config.csv_delimiter)
            writer.writerow(config.csv_headers)
            writer.writerows(record.to_list() for record in records)

        status.complete()
        print(f"\nCSV file saved successfully: {csv_output_path}")
        print(f"Processed {len(records)} records")
        return True

    except pdfplumber.PDFSyntaxError:
        error_msg = f"'{pdf_path}' is not a valid PDF file"
        status.fail(error_msg)
        print(f"Error: {error_msg}")
        return False
    except PermissionError:
        error_msg = f"Permission denied when writing to '{csv_output_path}'"
        status.fail(error_msg)
        print(f"Error: {error_msg}")
        return False
    except Exception as error:
        error_msg = f"An unexpected error occurred: {str(error)}"
        status.fail(error_msg)
        print(f"Error: {error_msg}")
        return False


def main() -> None:
    """Main entry point for the script."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Extract blood pressure data from Aktiia PDF report to CSV format'
    )
    parser.add_argument(
        'input_pdf',
        nargs='?',
        help='Path to the input PDF file'
    )
    parser.add_argument(
        'output_csv',
        nargs='?',
        help='Path for the output CSV file'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (YAML or JSON)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Print detailed status information'
    )
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create a default configuration file and exit'
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle config creation
    if args.create_config:
        config_manager = ConfigManager(args.config)
        config_manager.create_default_config()
        print("Default configuration file created successfully.")
        sys.exit(0)
    
    # Validate required arguments when not creating config
    if not args.input_pdf or not args.output_csv:
        parser.error("input_pdf and output_csv are required unless using --create-config")

    # Load configuration
    try:
        config = get_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default configuration.")
        config = ExtractionConfig()

    # Use context manager for status tracking
    with ProcessingStatus() as status:
        success = extract_bp_data(args.input_pdf, args.output_csv, status, config)
        
        # Print final status if requested
        if args.status:
            print("\nFinal Status Report:")
            print(status.get_status_report())

        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
