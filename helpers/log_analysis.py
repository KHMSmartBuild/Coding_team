# log_analysis.py - Log Analysis
# A script that analyzes log files, extracts useful information, and generates reports or
# visualizations to help with debugging and performance analysis.
# Typical uses include parsing and analyzing log files for debugging purposes or to understand
# the performance of your application.

import argparse
import re
import json
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

try:
    from .logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def parse_log_file(file_path: str, pattern: Optional[str] = None) -> Dict[str, List[Tuple[str, str]]]:
    """
    Parse the log file and extract useful information.

    :param file_path: The path of the log file.
    :param pattern: Optional custom regex pattern for log parsing.
    :return: A dictionary containing the extracted log data.
    """
    logger.info(f"Parsing log file: {file_path}")
    log_data = defaultdict(list)

    # Default log pattern: YYYY-MM-DD HH:MM:SS - LEVEL - Message
    if pattern is None:
        log_entry_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.*)')
    else:
        log_entry_pattern = re.compile(pattern)

    line_count = 0
    parsed_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line_count += 1
                match = log_entry_pattern.match(line.strip())

                if match:
                    timestamp, log_level, message = match.groups()
                    log_data[log_level].append((timestamp, message))
                    parsed_count += 1
    except FileNotFoundError:
        logger.error(f"Log file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error parsing log file: {e}", exc_info=True)
        raise

    logger.info(f"Parsed {parsed_count} entries from {line_count} lines")
    return log_data


def generate_report(log_data: Dict[str, List[Tuple[str, str]]], detailed: bool = False) -> None:
    """
    Generate a report based on the log data.

    :param log_data: The log data to generate a report for.
    :param detailed: Whether to show detailed entries or just summary.
    """
    logger.info("Generating log analysis report")
    
    total_entries = sum(len(entries) for entries in log_data.values())
    
    print("\n" + "=" * 60)
    print("LOG ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nTotal log entries: {total_entries}")
    print("\nEntries by level:")
    print("-" * 60)
    
    # Sort log levels by severity
    level_order = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
    
    for log_level in level_order:
        if log_level in log_data:
            entries = log_data[log_level]
            percentage = (len(entries) / total_entries * 100) if total_entries > 0 else 0
            print(f"{log_level:10s}: {len(entries):6d} entries ({percentage:5.1f}%)")
    
    # Show entries for other levels not in standard order
    for log_level, entries in sorted(log_data.items()):
        if log_level not in level_order:
            percentage = (len(entries) / total_entries * 100) if total_entries > 0 else 0
            print(f"{log_level:10s}: {len(entries):6d} entries ({percentage:5.1f}%)")
    
    if detailed:
        print("\n" + "=" * 60)
        print("DETAILED ENTRIES")
        print("=" * 60)
        
        for log_level in level_order:
            if log_level in log_data:
                entries = log_data[log_level]
                print(f"\n{log_level} ({len(entries)} entries):")
                print("-" * 60)
                for timestamp, message in entries[:10]:  # Show first 10
                    print(f"  {timestamp} - {message}")
                if len(entries) > 10:
                    print(f"  ... and {len(entries) - 10} more entries")


def analyze_errors(log_data: Dict[str, List[Tuple[str, str]]]) -> None:
    """
    Analyze error and warning messages for patterns.

    :param log_data: The log data to analyze.
    """
    logger.info("Analyzing error patterns")
    
    error_messages = []
    warning_messages = []
    
    if 'ERROR' in log_data:
        error_messages = [msg for _, msg in log_data['ERROR']]
    if 'CRITICAL' in log_data:
        error_messages.extend([msg for _, msg in log_data['CRITICAL']])
    if 'WARNING' in log_data:
        warning_messages = [msg for _, msg in log_data['WARNING']]
    
    if not error_messages and not warning_messages:
        print("\n✓ No errors or warnings found!")
        return
    
    print("\n" + "=" * 60)
    print("ERROR & WARNING ANALYSIS")
    print("=" * 60)
    
    if error_messages:
        print(f"\nTop error messages ({len(error_messages)} total):")
        print("-" * 60)
        error_counter = Counter(error_messages)
        for message, count in error_counter.most_common(5):
            print(f"  [{count:3d}x] {message[:70]}")
    
    if warning_messages:
        print(f"\nTop warning messages ({len(warning_messages)} total):")
        print("-" * 60)
        warning_counter = Counter(warning_messages)
        for message, count in warning_counter.most_common(5):
            print(f"  [{count:3d}x] {message[:70]}")


def analyze_timeline(log_data: Dict[str, List[Tuple[str, str]]]) -> None:
    """
    Analyze log timeline to identify patterns.

    :param log_data: The log data to analyze.
    """
    logger.info("Analyzing log timeline")
    
    all_entries = []
    for log_level, entries in log_data.items():
        for timestamp, message in entries:
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                all_entries.append((dt, log_level))
            except ValueError:
                continue
    
    if not all_entries:
        return
    
    all_entries.sort()
    
    print("\n" + "=" * 60)
    print("TIMELINE ANALYSIS")
    print("=" * 60)
    
    first_entry = all_entries[0][0]
    last_entry = all_entries[-1][0]
    duration = last_entry - first_entry
    
    print(f"\nFirst entry: {first_entry}")
    print(f"Last entry:  {last_entry}")
    print(f"Duration:    {duration}")
    
    # Group by hour
    hourly_counts = defaultdict(int)
    for dt, _ in all_entries:
        hour_key = dt.strftime('%Y-%m-%d %H:00')
        hourly_counts[hour_key] += 1
    
    if len(hourly_counts) > 1:
        print(f"\nActivity by hour:")
        print("-" * 60)
        for hour in sorted(hourly_counts.keys())[:10]:  # Show first 10 hours
            count = hourly_counts[hour]
            bar = '█' * min(count // 10, 50)
            print(f"  {hour}  {count:5d} {bar}")


def export_to_json(log_data: Dict[str, List[Tuple[str, str]]], output_file: str) -> None:
    """
    Export log data to JSON format.

    :param log_data: The log data to export.
    :param output_file: Path to output JSON file.
    """
    logger.info(f"Exporting log data to JSON: {output_file}")
    
    export_data = {
        level: [{'timestamp': ts, 'message': msg} for ts, msg in entries]
        for level, entries in log_data.items()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\n✓ Exported log data to: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Log Analysis Utility - Analyze and generate reports from log files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('log_file', help='The log file to analyze')
    parser.add_argument('-d', '--detailed', action='store_true', 
                       help='Show detailed entries for each log level')
    parser.add_argument('-e', '--errors', action='store_true',
                       help='Show error and warning analysis')
    parser.add_argument('-t', '--timeline', action='store_true',
                       help='Show timeline analysis')
    parser.add_argument('-j', '--json', metavar='OUTPUT_FILE',
                       help='Export results to JSON file')
    parser.add_argument('-p', '--pattern', 
                       help='Custom regex pattern for log parsing')

    args = parser.parse_args()

    try:
        log_data = parse_log_file(args.log_file, args.pattern)
        
        # Always show basic report
        generate_report(log_data, detailed=args.detailed)
        
        # Optional analyses
        if args.errors:
            analyze_errors(log_data)
        
        if args.timeline:
            analyze_timeline(log_data)
        
        # Export if requested
        if args.json:
            export_to_json(log_data, args.json)
        
        print("\n" + "=" * 60)
        print("Analysis complete!")
        print("=" * 60 + "\n")
        
    except FileNotFoundError:
        print(f"Error: Log file not found: {args.log_file}")
        return 1
    except Exception as e:
        print(f"Error analyzing log file: {e}")
        logger.error(f"Log analysis failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())



    """
    Script name: Log Analysis

    Filename: log_analysis.py

    Description: A script that analyzes log files, extracts useful information, 
    and generates reports or visualizations to help with debugging and 
    performance analysis.

    Typical uses: This script can be used to parse and analyze log files for 
    debugging purposes or to understand the performance of your application.

    Typical locations: This script can be saved in the project's root directory 
    or in a "scripts" or "utilities" folder.

    Purpose and functions: The purpose of this script is to assist in debugging 
    and performance analysis by parsing and analyzing log files.

    Please note that this example is for a Python project. Modify the script 
    accordingly for your project's specific needs.

    """