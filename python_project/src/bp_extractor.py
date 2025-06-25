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

# Constants
DATE_FORMAT = "%d %B, %y %H:%M"
OUTPUT_DATE_FORMAT = "%m/%d/%y %H:%M"
CSV_HEADERS = ["Date/Time", "Systolic", "Diastolic", "Pulse"]


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
    def from_match(cls, date_str: str, time_str: str, sys: str, dia: str, hr: str) -> 'BPRecord':
        """Create a BPRecord from matched strings."""
        date_obj = datetime.strptime(f"{date_str} {time_str}", DATE_FORMAT)
        return cls(
            datetime=date_obj.strftime(OUTPUT_DATE_FORMAT),
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

    def start(self, total_pages: int) -> None:
        """
        Start processing with the given total number of pages.

        Args:
            total_pages: The total number of pages to process
        """
        if total_pages < 0:
            raise ValueError("Total pages cannot be negative")
        self.total_pages = total_pages
        self.start_time = time.time()
        self.status = ProcessingState.PROCESSING
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


def extract_bp_data(pdf_path: str, csv_output_path: str, status: Optional[ProcessingStatus] = None) -> bool:
    """
    Extract blood pressure data from a PDF file and save it to a CSV file.
    
    Args:
        pdf_path: Path to the input PDF file
        csv_output_path: Path to save the output CSV file
        status: Optional status tracking object

    Returns:
        bool: True if successful, False otherwise
    """
    if status is None:
        status = ProcessingStatus()

    try:
        # Verify input file exists
        if not Path(pdf_path).is_file():
            error_msg = f"Input file '{pdf_path}' does not exist"
            status.fail(error_msg)
            print(f"Error: {error_msg}")
            return False

        # Lists to store the extracted data
        records: List[BPRecord] = []

        with pdfplumber.open(pdf_path) as pdf:
            # Initialize status
            status.start(len(pdf.pages) - 1)  # -1 because we skip first page

            # Iterate through pages starting from page 2 (index 1)
            for i in range(1, len(pdf.pages)):
                page = pdf.pages[i]
                text = page.extract_text()

                # Extract the lines with BP data
                lines = text.split('\n')
                for line in lines:
                    # Match lines containing Date, Time, SBP, DBP, HR
                    match = re.match(r"(\d{1,2}\s\w+,\s\d{2})\s(\d{2}:\d{2})\s+(\d+)\s+(\d+)\s+(\d+)", line)
                    if match:
                        record = BPRecord.from_match(*match.groups())
                        records.append(record)

                status.update(i, len(records))

        # Create output directory if it doesn't exist
        output_dir = Path(csv_output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write the extracted data to a CSV file
        with open(csv_output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)
            writer.writerows(record.to_list() for record in records)

        status.complete()
        print(f"\nCSV file saved successfully: {csv_output_path}")
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
        help='Path to the input PDF file'
    )
    parser.add_argument(
        'output_csv',
        help='Path for the output CSV file'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Print detailed status information'
    )

    # Parse arguments
    args = parser.parse_args()

    # Use context manager for status tracking
    with ProcessingStatus() as status:
        success = extract_bp_data(args.input_pdf, args.output_csv, status)
        
        # Print final status if requested
        if args.status:
            print("\nFinal Status Report:")
            print(status.get_status_report())

        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
