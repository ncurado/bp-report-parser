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


class ProcessingStatus:
    def __init__(self):
        self.total_pages = 0
        self.current_page = 0
        self.records_found = 0
        self.start_time = None
        self.end_time = None
        self.status = "Not Started"
        self.error = None

    def start(self, total_pages):
        self.total_pages = total_pages
        self.start_time = time.time()
        self.status = "Processing"

    def update(self, page, records):
        self.current_page = page
        self.records_found = records

    def complete(self):
        self.end_time = time.time()
        self.status = "Completed"

    def fail(self, error_msg):
        self.end_time = time.time()
        self.status = "Failed"
        self.error = error_msg

    def get_progress(self):
        if self.total_pages == 0:
            return 0
        return (self.current_page / self.total_pages) * 100

    def get_duration(self):
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def get_status_report(self):
        duration = self.get_duration()
        report = [
            f"Status: {self.status}",
            f"Progress: {self.get_progress():.1f}%",
            f"Pages Processed: {self.current_page}/{self.total_pages}",
            f"Records Found: {self.records_found}",
            f"Time Elapsed: {duration:.1f} seconds"
        ]
        if self.error:
            report.append(f"Error: {self.error}")
        return "\n".join(report)


def extract_bp_data(pdf_path, csv_output_path, status=None):
    """
    Extract blood pressure data from a PDF file and save it to a CSV file.
    
    Args:
        pdf_path (str): Path to the input PDF file
        csv_output_path (str): Path to save the output CSV file
        status (ProcessingStatus): Optional status tracking object
    
    Returns:
        bool: True if successful, False otherwise
    """
    if status is None:
        status = ProcessingStatus()

    try:
        # Verify input file exists
        if not Path(pdf_path).is_file():
            error_msg = f"Input file '{pdf_path}' does not exist"
            if status:
                status.fail(error_msg)
            print(f"Error: {error_msg}")
            return False

        # Lists to store the extracted data
        data = []

        with pdfplumber.open(pdf_path) as pdf:
            # Initialize status
            if status:
                status.start(len(pdf.pages) - 1)  # -1 because we skip first page

            # Iterate through pages starting from page 2 (index 1)
            for i in tqdm(range(1, len(pdf.pages)), desc="Processing pages"):
                page = pdf.pages[i]
                text = page.extract_text()

                # Extract the lines with BP data
                lines = text.split('\n')
                for line in lines:
                    # Match lines containing Date, Time, SBP, DBP, HR
                    match = re.match(r"(\d{1,2}\s\w+,\s\d{2})\s(\d{2}:\d{2})\s+(\d+)\s+(\d+)\s+(\d+)", line)
                    if match:
                        date_str = match.group(1)
                        time_str = match.group(2)
                        systolic = match.group(3)
                        diastolic = match.group(4)
                        heart_rate = match.group(5)

                        # Convert date and time to MM/DD/YY HH:MM (24-hour time)
                        date_obj = datetime.strptime(f"{date_str} {time_str}", "%d %B, %y %H:%M")
                        datetime_str = date_obj.strftime("%m/%d/%y %H:%M")

                        # Append the formatted data
                        data.append([datetime_str, systolic, diastolic, heart_rate])

                if status:
                    status.update(i, len(data))

        # Create output directory if it doesn't exist
        output_dir = Path(csv_output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write the extracted data to a CSV file
        with open(csv_output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date/Time", "Systolic", "Diastolic", "Pulse"])
            writer.writerows(data)

        if status:
            status.complete()
        print(f"\nCSV file saved successfully: {csv_output_path}")
        return True

    except pdfplumber.PDFSyntaxError:
        error_msg = f"'{pdf_path}' is not a valid PDF file"
        if status:
            status.fail(error_msg)
        print(f"Error: {error_msg}")
        return False
    except PermissionError:
        error_msg = f"Permission denied when writing to '{csv_output_path}'"
        if status:
            status.fail(error_msg)
        print(f"Error: {error_msg}")
        return False
    except Exception as error:
        error_msg = f"An unexpected error occurred: {str(error)}"
        if status:
            status.fail(error_msg)
        print(f"Error: {error_msg}")
        return False


def main():
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

    # Create status tracker
    status = ProcessingStatus()

    # Extract data
    success = extract_bp_data(args.input_pdf, args.output_csv, status)
    
    # Print final status if requested
    if args.status:
        print("\nFinal Status Report:")
        print(status.get_status_report())

    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
