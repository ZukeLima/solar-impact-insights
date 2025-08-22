#!/usr/bin/env python3
"""
Comprehensive data reading utilities for Solar Impact Insights project.
This module enhances data reading capabilities with validation, filtering, and caching.
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from typing import Optional, List, Dict, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataReader:
    """Enhanced data reading utility with validation and filtering capabilities"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.supported_formats = ['.csv', '.json', '.txt', '.parquet']
        self._cache = {}
        
    def read_solar_data(self, 
                       file_path: Optional[str] = None,
                       validate_data: bool = True,
                       filter_params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Read solar data from various sources with enhanced functionality
        
        Args:
            file_path: Path to data file (if None, uses default CSV)
            validate_data: Whether to validate data integrity
            filter_params: Dictionary with filtering parameters
            
        Returns:
            pandas.DataFrame: Processed solar data
        """
        try:
            # Use default file if none provided
            if file_path is None:
                file_path = self.data_dir / "real_solar_data.csv"
            else:
                file_path = Path(file_path)
            
            # Check cache first
            cache_key = f"{file_path}_{hash(str(filter_params))}"
            if cache_key in self._cache:
                logger.info(f"Loading data from cache: {file_path}")
                return self._cache[cache_key].copy()
            
            # Read data based on file extension
            if file_path.suffix == '.csv':
                df = self._read_csv_enhanced(file_path)
            elif file_path.suffix == '.json':
                df = self._read_json_enhanced(file_path)
            elif file_path.suffix == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            logger.info(f"Successfully loaded {len(df)} records from {file_path}")
            
            # Validate data if requested
            if validate_data:
                df = self._validate_solar_data(df)
            
            # Apply filters if provided
            if filter_params:
                df = self._apply_filters(df, filter_params)
            
            # Cache the result
            self._cache[cache_key] = df.copy()
            
            return df
            
        except Exception as e:
            logger.error(f"Error reading data from {file_path}: {e}")
            return pd.DataFrame()
    
    def _read_csv_enhanced(self, file_path: Path) -> pd.DataFrame:
        """Enhanced CSV reading with error handling and optimization"""
        try:
            # Try to infer the structure first
            sample = pd.read_csv(file_path, nrows=5)
            
            # Optimize data types
            dtype_dict = {}
            for col in sample.columns:
                if col in ['datetime', 'date', 'timestamp']:
                    continue  # Handle datetime separately
                elif sample[col].dtype == 'object':
                    try:
                        pd.to_numeric(sample[col])
                        dtype_dict[col] = 'float64'
                    except:
                        dtype_dict[col] = 'object'
                else:
                    dtype_dict[col] = sample[col].dtype
            
            # Read full data with optimized types
            df = pd.read_csv(file_path, dtype=dtype_dict, low_memory=False)
            
            # Handle datetime columns
            for col in df.columns:
                if col in ['datetime', 'date', 'timestamp'] or 'date' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        logger.warning(f"Could not convert {col} to datetime")
            
            return df
            
        except Exception as e:
            logger.error(f"Error in enhanced CSV reading: {e}")
            # Fallback to basic reading
            return pd.read_csv(file_path)
    
    def _read_json_enhanced(self, file_path: Path) -> pd.DataFrame:
        """Enhanced JSON reading with structure detection"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    # Try to flatten the dictionary
                    df = pd.json_normalize(data)
            else:
                raise ValueError("JSON format not supported")
            
            return df
            
        except Exception as e:
            logger.error(f"Error reading JSON: {e}")
            return pd.DataFrame()
    
    def _validate_solar_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate solar data integrity and quality"""
        original_count = len(df)
        
        # Check for required columns
        required_columns = ['datetime', 'sep_intensity']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        if len(df) < original_count:
            logger.info(f"Removed {original_count - len(df)} duplicate records")
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isnull().sum() > 0:
                # Fill with median for numeric columns
                df[col] = df[col].fillna(df[col].median())
                logger.info(f"Filled {df[col].isnull().sum()} missing values in {col}")
        
        # Validate data ranges
        if 'sep_intensity' in df.columns:
            # SEP intensity should be positive
            invalid_sep = df['sep_intensity'] < 0
            if invalid_sep.sum() > 0:
                logger.warning(f"Found {invalid_sep.sum()} negative SEP intensity values")
                df.loc[invalid_sep, 'sep_intensity'] = 0
        
        if 'kp_index' in df.columns:
            # Kp index should be 0-9
            df['kp_index'] = df['kp_index'].clip(0, 9)
        
        logger.info(f"Data validation complete. Final count: {len(df)}")
        return df
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Apply filtering parameters to the dataframe"""
        filtered_df = df.copy()
        
        # Date range filtering
        if 'start_date' in filters and filters['start_date']:
            start_date = pd.to_datetime(filters['start_date'])
            date_col = self._find_date_column(filtered_df)
            if date_col:
                filtered_df = filtered_df[filtered_df[date_col] >= start_date]
        
        if 'end_date' in filters and filters['end_date']:
            end_date = pd.to_datetime(filters['end_date'])
            date_col = self._find_date_column(filtered_df)
            if date_col:
                filtered_df = filtered_df[filtered_df[date_col] <= end_date]
        
        # Intensity filtering
        if 'min_intensity' in filters and filters['min_intensity'] is not None:
            if 'sep_intensity' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['sep_intensity'] >= filters['min_intensity']]
        
        if 'max_intensity' in filters and filters['max_intensity'] is not None:
            if 'sep_intensity' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['sep_intensity'] <= filters['max_intensity']]
        
        # High-intensity events only
        if filters.get('high_intensity_only', False):
            if 'sep_intensity' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['sep_intensity'] > 5.0]
        
        logger.info(f"Applied filters: {len(df)} -> {len(filtered_df)} records")
        return filtered_df
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the main date column in the dataframe"""
        date_columns = ['datetime', 'date', 'timestamp']
        for col in date_columns:
            if col in df.columns:
                return col
        
        # Look for columns with 'date' in the name
        for col in df.columns:
            if 'date' in col.lower():
                return col
        
        return None
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """Generate a comprehensive data summary"""
        if df.empty:
            return {"error": "No data available"}
        
        summary = {
            "total_records": len(df),
            "date_range": {},
            "columns": list(df.columns),
            "statistics": {},
            "missing_values": {},
            "data_quality": {}
        }
        
        # Date range
        date_col = self._find_date_column(df)
        if date_col:
            summary["date_range"] = {
                "start": df[date_col].min().isoformat() if pd.notna(df[date_col].min()) else None,
                "end": df[date_col].max().isoformat() if pd.notna(df[date_col].max()) else None,
                "days_covered": (df[date_col].max() - df[date_col].min()).days if pd.notna(df[date_col].min()) else 0
            }
        
        # Statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            summary["statistics"][col] = {
                "mean": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                "std": float(df[col].std()) if pd.notna(df[col].std()) else None,
                "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
                "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
                "median": float(df[col].median()) if pd.notna(df[col].median()) else None
            }
        
        # Missing values
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                summary["missing_values"][col] = int(missing_count)
        
        # Data quality metrics
        if 'sep_intensity' in df.columns:
            high_events = len(df[df['sep_intensity'] > 7])
            medium_events = len(df[(df['sep_intensity'] > 4) & (df['sep_intensity'] <= 7)])
            low_events = len(df[df['sep_intensity'] <= 4])
            
            summary["data_quality"] = {
                "high_intensity_events": high_events,
                "medium_intensity_events": medium_events,
                "low_intensity_events": low_events,
                "intensity_distribution": {
                    "high": high_events,
                    "medium": medium_events,
                    "low": low_events
                }
            }
        
        return summary
    
    def export_data(self, df: pd.DataFrame, 
                   file_path: str, 
                   format: str = 'csv',
                   **kwargs) -> bool:
        """Export data to various formats"""
        try:
            file_path = Path(file_path)
            
            if format.lower() == 'csv':
                df.to_csv(file_path, index=False, **kwargs)
            elif format.lower() == 'json':
                df.to_json(file_path, orient='records', date_format='iso', **kwargs)
            elif format.lower() == 'parquet':
                df.to_parquet(file_path, **kwargs)
            elif format.lower() == 'excel':
                df.to_excel(file_path, index=False, **kwargs)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Data exported to {file_path} in {format} format")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False
    
    def clear_cache(self):
        """Clear the data cache"""
        self._cache.clear()
        logger.info("Data cache cleared")
    
    def get_available_files(self) -> List[str]:
        """Get list of available data files"""
        files = []
        if self.data_dir.exists():
            for file in self.data_dir.iterdir():
                if file.suffix in self.supported_formats:
                    files.append(str(file.relative_to(self.data_dir)))
        return sorted(files)

# Convenience functions for common operations
def read_solar_csv(file_path: str = None, **kwargs) -> pd.DataFrame:
    """Quick function to read solar CSV data"""
    reader = DataReader()
    return reader.read_solar_data(file_path, **kwargs)

def get_data_info(df: pd.DataFrame) -> Dict:
    """Quick function to get data summary"""
    reader = DataReader()
    return reader.get_data_summary(df)

def export_to_format(df: pd.DataFrame, file_path: str, format: str = 'csv') -> bool:
    """Quick function to export data"""
    reader = DataReader()
    return reader.export_data(df, file_path, format)