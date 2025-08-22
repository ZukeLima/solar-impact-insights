#!/usr/bin/env python3
"""
Command-line utility for reading and exploring solar data.
This script demonstrates the enhanced data reading capabilities.
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.data_reader import DataReader, read_solar_csv, get_data_info, export_to_format

def main():
    parser = argparse.ArgumentParser(description='Solar Data Reader Utility')
    parser.add_argument('--file', '-f', help='Path to data file')
    parser.add_argument('--validate', '-v', action='store_true', help='Validate data')
    parser.add_argument('--summary', '-s', action='store_true', help='Show data summary')
    parser.add_argument('--export', '-e', help='Export format (csv, json, excel)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--filter-start', help='Filter start date (YYYY-MM-DD)')
    parser.add_argument('--filter-end', help='Filter end date (YYYY-MM-DD)')
    parser.add_argument('--filter-min-intensity', type=float, help='Minimum SEP intensity')
    parser.add_argument('--filter-max-intensity', type=float, help='Maximum SEP intensity')
    parser.add_argument('--high-intensity', action='store_true', help='Show only high intensity events (>5.0)')
    parser.add_argument('--list-files', action='store_true', help='List available data files')
    
    args = parser.parse_args()
    
    # Initialize data reader
    data_reader = DataReader()
    
    # List available files if requested
    if args.list_files:
        print("📂 Available data files:")
        files = data_reader.get_available_files()
        if files:
            for file in files:
                print(f"  • {file}")
        else:
            print("  No data files found in data/ directory")
        return
    
    # Build filters
    filters = {}
    if args.filter_start:
        filters['start_date'] = args.filter_start
    if args.filter_end:
        filters['end_date'] = args.filter_end
    if args.filter_min_intensity is not None:
        filters['min_intensity'] = args.filter_min_intensity
    if args.filter_max_intensity is not None:
        filters['max_intensity'] = args.filter_max_intensity
    if args.high_intensity:
        filters['high_intensity_only'] = True
    
    # Read data
    print("📖 Reading solar data...")
    df = data_reader.read_solar_data(
        file_path=args.file,
        validate_data=args.validate,
        filter_params=filters if filters else None
    )
    
    if df.empty:
        print("❌ No data found or failed to read data")
        return 1
    
    print(f"✅ Successfully loaded {len(df)} records")
    
    # Show summary if requested
    if args.summary:
        print("\n📊 Data Summary:")
        summary = get_data_info(df)
        
        print(f"  • Total records: {summary['total_records']:,}")
        
        if summary.get('date_range'):
            dr = summary['date_range']
            if dr.get('start') and dr.get('end'):
                print(f"  • Date range: {dr['start'][:10]} to {dr['end'][:10]}")
            if dr.get('days_covered'):
                print(f"  • Days covered: {dr['days_covered']}")
        
        if summary.get('statistics'):
            print("  • Key statistics:")
            for var, stats in summary['statistics'].items():
                if stats.get('mean') is not None:
                    print(f"    - {var}: μ={stats['mean']:.2f}, σ={stats.get('std', 0):.2f}")
        
        if summary.get('missing_values'):
            print("  • Missing values:")
            for col, count in summary['missing_values'].items():
                pct = (count / summary['total_records']) * 100
                print(f"    - {col}: {count} ({pct:.1f}%)")
        
        if summary.get('data_quality'):
            dq = summary['data_quality']
            print("  • Event intensity distribution:")
            print(f"    - High intensity (>7): {dq.get('high_intensity_events', 0)}")
            print(f"    - Medium intensity (4-7): {dq.get('medium_intensity_events', 0)}")
            print(f"    - Low intensity (<4): {dq.get('low_intensity_events', 0)}")
    
    # Export data if requested
    if args.export:
        output_file = args.output or f"solar_data_export.{args.export}"
        print(f"\n📥 Exporting data to {output_file}...")
        
        success = export_to_format(df, output_file, args.export)
        if success:
            print(f"✅ Data exported successfully to {output_file}")
        else:
            print(f"❌ Failed to export data")
            return 1
    
    # Show first few rows
    print(f"\n📋 First 5 rows:")
    print(df.head().to_string())
    
    return 0

if __name__ == "__main__":
    sys.exit(main())