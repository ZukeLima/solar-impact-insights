# 📖 Enhanced Data Reading - "Leia" Module

This module implements comprehensive data reading capabilities for the Solar Impact Insights project, addressing the "leia" (read) functionality requirements.

## 🚀 Features

### Enhanced Data Reading
- **Multi-format Support**: CSV, JSON, Parquet, Excel files
- **Intelligent Type Detection**: Automatic optimization of data types
- **Error Handling**: Robust error handling with fallback mechanisms
- **Caching**: Built-in caching for improved performance
- **Validation**: Comprehensive data validation and quality checks

### Advanced Filtering
- **Date Range Filtering**: Filter data by start/end dates
- **Intensity Filtering**: Min/max SEP intensity filters
- **High-Intensity Events**: Quick filter for events >5.0 intensity
- **Search Functionality**: Text-based search across data
- **Dynamic Filtering**: Real-time filtering in the dashboard

### Data Export
- **Multiple Formats**: Export to CSV, JSON, Excel, Parquet
- **Custom Filenames**: Configurable export filenames
- **Filter Preservation**: Export with filter information
- **Metadata Inclusion**: Export includes data quality metrics

## 📁 Files Added/Modified

### New Files:
- `infrastructure/data_reader.py` - Core data reading utility
- `scripts/read_data.py` - Command-line data reading tool
- `DATA_READING.md` - This documentation

### Modified Files:
- `streamlit_app.py` - Enhanced dashboard with new data reading capabilities
- `scripts/quick_collect.py` - Added data validation using enhanced reader

## 🔧 Usage Examples

### 1. Command Line Usage

```bash
# List available data files
python scripts/read_data.py --list-files

# Read data with validation and summary
python scripts/read_data.py --validate --summary

# Filter data by date range
python scripts/read_data.py --filter-start 2024-01-01 --filter-end 2024-12-31 --summary

# Export high-intensity events to JSON
python scripts/read_data.py --high-intensity --export json --output high_intensity_events.json

# Filter by intensity and export
python scripts/read_data.py --filter-min-intensity 5.0 --export csv --output intense_events.csv
```

### 2. Python API Usage

```python
from infrastructure.data_reader import DataReader, read_solar_csv, get_data_info

# Quick CSV reading
df = read_solar_csv()

# Advanced reading with filters
reader = DataReader()
filters = {
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'min_intensity': 3.0,
    'high_intensity_only': True
}

df = reader.read_solar_data(
    validate_data=True,
    filter_params=filters
)

# Get data summary
summary = get_data_info(df)
print(f"Records: {summary['total_records']:,}")

# Export data
reader.export_data(df, 'filtered_data.json', format='json')
```

### 3. Streamlit Dashboard Features

The enhanced dashboard now includes:

- **Data Source Selection**: Choose between database, CSV, or mock data
- **Advanced Filtering**: Multiple filter options with real-time application
- **Data Export**: Export filtered data in multiple formats
- **Data Quality Metrics**: Comprehensive data quality analysis
- **Interactive Tables**: Enhanced data exploration with search and sorting
- **Caching Controls**: Clear cache and refresh data options

## 📊 Data Validation Features

### Automatic Validation:
- **Duplicate Removal**: Automatic detection and removal of duplicates
- **Missing Value Handling**: Smart filling of missing values with medians
- **Range Validation**: Ensures data values are within expected ranges
- **Type Conversion**: Automatic conversion of date/time columns

### Quality Metrics:
- **Completeness**: Percentage of non-missing data
- **Intensity Distribution**: Classification of events by intensity
- **Date Coverage**: Analysis of temporal data coverage
- **Outlier Detection**: Identification of potential data anomalies

## 🔍 Enhanced Dashboard Features

### Data Source Panel:
- Source selection (Database/CSV/Mock)
- Available file listing
- Connection status indicators

### Advanced Filtering Panel:
- Date range selection with checkbox toggle
- Intensity range filtering
- High-intensity event filter
- Filter combination logic

### Data Operations Panel:
- Refresh data functionality
- Cache clearing options
- Export functionality with format selection

### Data Explorer Tab:
- **Source Information**: Shows data source and key metrics
- **Advanced Operations**: Sorting, sampling, searching
- **Quality Analysis**: Missing values and completeness metrics
- **Export Tools**: Multiple format export with metadata
- **Interactive Table**: Column selection and enhanced display
- **Quick Statistics**: Detailed statistics with visualizations

## 🚀 Performance Improvements

### Caching:
- **Memory Caching**: Prevents redundant file reading
- **Query Caching**: Caches filtered results
- **Smart Invalidation**: Automatic cache clearing when needed

### Optimization:
- **Type Optimization**: Automatic dtype optimization reduces memory usage
- **Lazy Loading**: Data loaded only when needed
- **Efficient Filtering**: Server-side filtering reduces client processing

## 🎯 Integration Points

The enhanced data reading functionality integrates with:

1. **Database Repository**: Fallback to CSV when database is empty
2. **Analysis Modules**: Provides clean, validated data for analysis
3. **Visualization**: Optimized data format for plotting
4. **Export Systems**: Standardized export across the application

## 🐛 Error Handling

Robust error handling includes:

- **File Not Found**: Graceful fallback to alternative sources
- **Format Errors**: Automatic format detection and correction
- **Network Issues**: Timeout handling for remote data sources
- **Memory Issues**: Chunked processing for large datasets
- **Validation Failures**: Clear error messages and recovery options

## 📈 Future Enhancements

Planned improvements:
- **Real-time Data Streaming**: Live data feed integration
- **Advanced Analytics**: Built-in statistical analysis
- **Data Lineage**: Track data processing history
- **API Integration**: Direct connection to solar data APIs
- **Automated Quality Reports**: Scheduled data quality assessments

---

This enhanced "leia" (read) functionality significantly improves the project's data handling capabilities, making it easier to work with solar data across different formats and sources while maintaining high data quality standards.