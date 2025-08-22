import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database.repository import DatabaseRepository
from infrastructure.database.models import get_db
from infrastructure.data_reader import DataReader, read_solar_csv, get_data_info
from use_cases.analysis import analisar_correlacoes, clusterizar_eventos, prever_eventos
from infrastructure.data_collection import gerar_dados_mock

# Page configuration
st.set_page_config(
    page_title="🌞 Solar Event Analytics",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #ff6b35;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 107, 53, 0.1);
        border-radius: 10px;
        padding: 0 24px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(data_source="database", file_path=None, filters=None):
    """Enhanced data loading with multiple sources and filtering"""
    data_reader = DataReader()
    
    try:
        if data_source == "database":
            # Try to load from database first
            repo = DatabaseRepository()
            df = repo.get_sep_events_as_dataframe()
            if not df.empty:
                st.success(f"✅ Loaded {len(df)} records from database")
                return df
            else:
                st.warning("⚠️ Database is empty, trying CSV file...")
                data_source = "csv"
        
        if data_source == "csv":
            # Load from CSV file with enhanced reader
            df = data_reader.read_solar_data(
                file_path=file_path,
                validate_data=True,
                filter_params=filters
            )
            if not df.empty:
                st.success(f"✅ Loaded {len(df)} records from CSV")
                return df
            else:
                st.warning("⚠️ CSV file not found or empty, generating mock data...")
                data_source = "mock"
        
        if data_source == "mock":
            # Generate mock data as fallback
            sep, temp, ice, ozone, geomag = gerar_dados_mock()
            from adapters.data_adapter import integrar_dados
            df = integrar_dados(sep, temp, ice, ozone, geomag)
            st.info(f"ℹ️ Generated {len(df)} mock records")
            return df
            
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        # Final fallback to mock data
        try:
            sep, temp, ice, ozone, geomag = gerar_dados_mock()
            from adapters.data_adapter import integrar_dados
            df = integrar_dados(sep, temp, ice, ozone, geomag)
            st.info("ℹ️ Using mock data as fallback")
            return df
        except Exception as fallback_error:
            st.error(f"❌ Critical error: {fallback_error}")
            return pd.DataFrame()

@st.cache_data
def get_data_summary(df):
    """Get enhanced data summary"""
    return get_data_info(df)

def main():
    # Header
    st.markdown('<h1 class="main-header">🌞 Solar Event Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar with Enhanced Data Controls
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        
        # Data Source Selection
        st.subheader("📂 Data Source")
        data_reader = DataReader()
        available_files = data_reader.get_available_files()
        
        data_source = st.selectbox(
            "Choose data source:",
            options=["database", "csv", "mock"],
            format_func=lambda x: {
                "database": "🗄️ Database", 
                "csv": "📄 CSV File", 
                "mock": "🎲 Mock Data"
            }[x]
        )
        
        file_path = None
        if data_source == "csv":
            if available_files:
                selected_file = st.selectbox("Select CSV file:", available_files)
                file_path = f"data/{selected_file}"
            else:
                st.warning("⚠️ No CSV files found in data/ directory")
                st.info("Available files will be shown here when found")
        
        # Enhanced Filtering
        st.subheader("🔍 Data Filters")
        
        # Date range filter
        use_date_filter = st.checkbox("Filter by date range", value=False)
        start_date, end_date = None, None
        
        if use_date_filter:
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input("Start date", value=datetime.now() - timedelta(days=30))
            with date_col2:
                end_date = st.date_input("End date", value=datetime.now())
        
        # Intensity filters
        use_intensity_filter = st.checkbox("Filter by intensity", value=False)
        min_intensity, max_intensity = None, None
        
        if use_intensity_filter:
            intensity_col1, intensity_col2 = st.columns(2)
            with intensity_col1:
                min_intensity = st.number_input("Min intensity", min_value=0.0, max_value=20.0, value=0.0, step=0.1)
            with intensity_col2:
                max_intensity = st.number_input("Max intensity", min_value=0.0, max_value=20.0, value=20.0, step=0.1)
        
        # High intensity events only
        high_intensity_only = st.checkbox("High intensity events only (>5.0)", value=False)
        
        # Build filters dictionary
        filters = {}
        if use_date_filter:
            filters.update({"start_date": start_date, "end_date": end_date})
        if use_intensity_filter:
            filters.update({"min_intensity": min_intensity, "max_intensity": max_intensity})
        if high_intensity_only:
            filters["high_intensity_only"] = True
        
        # Data operations
        st.subheader("⚙️ Data Operations")
        
        col_refresh, col_clear = st.columns(2)
        with col_refresh:
            refresh_data = st.button("🔄 Refresh", type="primary", use_container_width=True)
        with col_clear:
            clear_cache = st.button("🗑️ Clear Cache", use_container_width=True)
        
        if refresh_data:
            st.cache_data.clear()
            st.rerun()
            
        if clear_cache:
            data_reader.clear_cache()
            st.cache_data.clear()
            st.success("Cache cleared!")
            st.rerun()
        
        # Analysis options
        st.subheader("🔬 Analysis Options")
        show_clustering = st.checkbox("Show Clustering Analysis", value=True)
        show_correlations = st.checkbox("Show Correlations", value=True)
        show_predictions = st.checkbox("Show Predictions", value=True)

    # Load data with enhanced parameters
    with st.spinner("Loading solar event data..."):
        df = load_data(data_source=data_source, file_path=file_path, filters=filters)
    
    if df.empty:
        st.error("❌ No data available. Please check your data source.")
        return
    
    # Get and display data summary
    data_summary = get_data_summary(df)
    
    # Apply additional client-side filtering for legacy compatibility
    df_filtered = df.copy()
    
    # Legacy date filtering (if filters weren't applied server-side)
    if not filters and 'date_range' in st.session_state and len(st.session_state.date_range) == 2:
        date_col = 'date' if 'date' in df.columns else 'datetime'
        if date_col in df.columns:
            df_filtered = df_filtered[
                (df_filtered[date_col] >= pd.Timestamp(st.session_state.date_range[0])) & 
                (df_filtered[date_col] <= pd.Timestamp(st.session_state.date_range[1]))
            ]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f'<div class="metric-card"><h3>{len(df_filtered)}</h3><p>Total Events</p></div>',
            unsafe_allow_html=True
        )
    
    with col2:
        avg_intensity = df_filtered['sep_intensity'].mean() if not df_filtered.empty else 0
        st.markdown(
            f'<div class="metric-card"><h3>{avg_intensity:.2f}</h3><p>Avg Intensity</p></div>',
            unsafe_allow_html=True
        )
    
    with col3:
        high_intensity = len(df_filtered[df_filtered['sep_intensity'] > 5.0])
        st.markdown(
            f'<div class="metric-card"><h3>{high_intensity}</h3><p>High Intensity</p></div>',
            unsafe_allow_html=True
        )
    
    with col4:
        max_intensity = df_filtered['sep_intensity'].max() if not df_filtered.empty else 0
        st.markdown(
            f'<div class="metric-card"><h3>{max_intensity:.2f}</h3><p>Peak Intensity</p></div>',
            unsafe_allow_html=True
        )

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Time Series", "🔍 Analysis", "🎯 Correlations", 
        "🔮 Predictions", "📊 Data Explorer"
    ])
    
    with tab1:
        st.header("📈 Time Series Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Main time series plot
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_filtered['date'],
                y=df_filtered['sep_intensity'],
                mode='lines+markers',
                name='SEP Intensity',
                line=dict(color='#ff6b35', width=2),
                marker=dict(size=4)
            ))
            
            # Add threshold line
            fig.add_hline(
                y=5.0, 
                line_dash="dash", 
                line_color="red",
                annotation_text="High Intensity Threshold"
            )
            
            fig.update_layout(
                title="SEP Intensity Over Time",
                xaxis_title="Date",
                yaxis_title="SEP Intensity",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Statistics
            st.subheader("📊 Statistics")
            
            if not df_filtered.empty:
                stats = df_filtered['sep_intensity'].describe()
                
                st.metric("Mean", f"{stats['mean']:.2f}")
                st.metric("Std Dev", f"{stats['std']:.2f}")
                st.metric("Min", f"{stats['min']:.2f}")
                st.metric("Max", f"{stats['max']:.2f}")
                
                # Distribution histogram
                fig_hist = px.histogram(
                    df_filtered, 
                    x='sep_intensity',
                    nbins=20,
                    title="Intensity Distribution"
                )
                fig_hist.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig_hist, use_container_width=True)
        
        # Multi-variable time series
        st.subheader("🌡️ Multi-Variable Analysis")
        
        variables = st.multiselect(
            "Select variables to display",
            ['sep_intensity', 'temperature', 'ice_extent', 'ozone_level', 'kp_index'],
            default=['sep_intensity', 'temperature']
        )
        
        if variables and not df_filtered.empty:
            fig_multi = make_subplots(
                rows=len(variables), cols=1,
                shared_xaxes=True,
                subplot_titles=variables
            )
            
            colors = ['#ff6b35', '#f7931e', '#ffcd3c', '#17a2b8', '#28a745']
            
            for i, var in enumerate(variables):
                fig_multi.add_trace(
                    go.Scatter(
                        x=df_filtered['date'],
                        y=df_filtered[var],
                        mode='lines',
                        name=var,
                        line=dict(color=colors[i % len(colors)])
                    ),
                    row=i+1, col=1
                )
            
            fig_multi.update_layout(
                template="plotly_dark",
                height=150 * len(variables),
                showlegend=False
            )
            
            st.plotly_chart(fig_multi, use_container_width=True)

    with tab2:
        st.header("🔍 Advanced Analysis")
        
        if show_clustering and not df_filtered.empty:
            st.subheader("🎯 Clustering Analysis")
            
            try:
                clustered_data = clusterizar_eventos(df_filtered.copy())
                
                if 'cluster' in clustered_data.columns:
                    # 3D scatter plot
                    fig_3d = px.scatter_3d(
                        clustered_data,
                        x='sep_intensity',
                        y='temperature',
                        z='kp_index',
                        color='cluster',
                        title="3D Cluster Visualization",
                        labels={'cluster': 'Cluster'}
                    )
                    fig_3d.update_layout(template="plotly_dark")
                    st.plotly_chart(fig_3d, use_container_width=True)
                    
                    # Cluster statistics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        cluster_stats = clustered_data.groupby('cluster').agg({
                            'sep_intensity': ['mean', 'std', 'count']
                        }).round(2)
                        st.write("Cluster Statistics:")
                        st.dataframe(cluster_stats, use_container_width=True)
                    
                    with col2:
                        # Cluster distribution
                        cluster_counts = clustered_data['cluster'].value_counts()
                        fig_pie = px.pie(
                            values=cluster_counts.values,
                            names=cluster_counts.index,
                            title="Cluster Distribution"
                        )
                        fig_pie.update_layout(template="plotly_dark")
                        st.plotly_chart(fig_pie, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error in clustering analysis: {e}")
        
        # Anomaly Detection
        st.subheader("🚨 Anomaly Detection")
        
        if not df_filtered.empty:
            # Simple anomaly detection using IQR
            Q1 = df_filtered['sep_intensity'].quantile(0.25)
            Q3 = df_filtered['sep_intensity'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            anomalies = df_filtered[
                (df_filtered['sep_intensity'] < lower_bound) | 
                (df_filtered['sep_intensity'] > upper_bound)
            ]
            
            if not anomalies.empty:
                st.warning(f"🚨 {len(anomalies)} anomalies detected!")
                
                fig_anom = go.Figure()
                
                # Normal data
                normal_data = df_filtered[
                    (df_filtered['sep_intensity'] >= lower_bound) & 
                    (df_filtered['sep_intensity'] <= upper_bound)
                ]
                
                fig_anom.add_trace(go.Scatter(
                    x=normal_data['date'],
                    y=normal_data['sep_intensity'],
                    mode='markers',
                    name='Normal',
                    marker=dict(color='blue', size=4)
                ))
                
                # Anomalies
                fig_anom.add_trace(go.Scatter(
                    x=anomalies['date'],
                    y=anomalies['sep_intensity'],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=8, symbol='x')
                ))
                
                fig_anom.update_layout(
                    title="Anomaly Detection",
                    template="plotly_dark",
                    height=400
                )
                
                st.plotly_chart(fig_anom, use_container_width=True)
                
                # Show anomaly details
                st.write("Anomalous Events:")
                st.dataframe(anomalies[['date', 'sep_intensity', 'temperature', 'kp_index']])
            else:
                st.success("✅ No anomalies detected in current data")

    with tab3:
        st.header("🎯 Correlation Analysis")
        
        if show_correlations and not df_filtered.empty:
            # Correlation matrix
            numeric_cols = ['sep_intensity', 'temperature', 'ice_extent', 'ozone_level', 'kp_index']
            corr_data = df_filtered[numeric_cols].corr()
            
            fig_corr = px.imshow(
                corr_data,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix",
                color_continuous_scale="RdBu_r"
            )
            fig_corr.update_layout(template="plotly_dark")
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Pairwise relationships
            st.subheader("📊 Pairwise Relationships")
            
            var1 = st.selectbox("Select X variable", numeric_cols, index=0)
            var2 = st.selectbox("Select Y variable", numeric_cols, index=1)
            
            if var1 != var2:
                fig_scatter = px.scatter(
                    df_filtered,
                    x=var1,
                    y=var2,
                    color='sep_intensity',
                    title=f"{var1} vs {var2}",
                    trendline="ols"
                )
                fig_scatter.update_layout(template="plotly_dark")
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Correlation coefficient
                corr_coeff = df_filtered[var1].corr(df_filtered[var2])
                st.metric("Correlation Coefficient", f"{corr_coeff:.3f}")

    with tab4:
        st.header("🔮 Prediction Models")
        
        if show_predictions and not df_filtered.empty:
            try:
                forecast = prever_eventos(df_filtered.copy())
                
                # Prediction plot
                fig_pred = go.Figure()
                
                # Historical data
                fig_pred.add_trace(go.Scatter(
                    x=df_filtered['date'],
                    y=df_filtered['sep_intensity'],
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#17a2b8')
                ))
                
                # Predictions
                fig_pred.add_trace(go.Scatter(
                    x=forecast['date'],
                    y=forecast['predicted_sep_intensity'],
                    mode='lines+markers',
                    name='Predicted',
                    line=dict(color='#ffcd3c', dash='dash')
                ))
                
                fig_pred.update_layout(
                    title="SEP Intensity Predictions",
                    template="plotly_dark",
                    height=400
                )
                
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # Prediction metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_pred = forecast['predicted_sep_intensity'].mean()
                    st.metric("Avg Predicted Intensity", f"{avg_pred:.2f}")
                
                with col2:
                    max_pred = forecast['predicted_sep_intensity'].max()
                    st.metric("Peak Predicted Intensity", f"{max_pred:.2f}")
                
                with col3:
                    high_risk_days = len(forecast[forecast['predicted_sep_intensity'] > 5.0])
                    st.metric("High Risk Days", high_risk_days)
                
                # Prediction table
                st.subheader("📅 Detailed Predictions")
                forecast_display = forecast.copy()
                forecast_display['date'] = forecast_display['date'].dt.strftime('%Y-%m-%d')
                forecast_display['predicted_sep_intensity'] = forecast_display['predicted_sep_intensity'].round(2)
                
                st.dataframe(forecast_display, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error generating predictions: {e}")

    with tab5:
        st.header("📊 Enhanced Data Explorer")
        
        # Data source information
        st.subheader("📋 Data Source Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Source:** {data_source.upper()}")
            if file_path:
                st.info(f"**File:** {file_path}")
            st.info(f"**Records:** {len(df_filtered):,}")
            
        with col2:
            if data_summary.get("date_range"):
                st.info(f"**Period:** {data_summary['date_range'].get('days_covered', 0)} days")
                if data_summary['date_range'].get('start'):
                    start_str = data_summary['date_range']['start'][:10]  # Get date part
                    end_str = data_summary['date_range']['end'][:10]
                    st.info(f"**Range:** {start_str} to {end_str}")
        
        # Enhanced filtering and operations
        st.subheader("🔍 Advanced Data Operations")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sort_column = st.selectbox(
                "Sort by:",
                options=[col for col in df_filtered.columns if col != 'cluster'],
                index=0 if 'datetime' not in df_filtered.columns else 
                      list(df_filtered.columns).index('datetime') if 'datetime' in df_filtered.columns
                      else 0
            )
            
        with col2:
            sort_ascending = st.checkbox("Ascending", value=False)
            
        with col3:
            show_sample = st.checkbox("Show sample only", value=False)
            if show_sample:
                sample_size = st.slider("Sample size", 10, min(1000, len(df_filtered)), 100)
                
        with col4:
            search_term = st.text_input("Search in data:", placeholder="Enter search term...")
        
        # Apply advanced operations
        display_df = df_filtered.copy()
        
        # Sorting
        if sort_column in display_df.columns:
            display_df = display_df.sort_values(sort_column, ascending=sort_ascending)
        
        # Sampling
        if show_sample and len(display_df) > sample_size:
            display_df = display_df.sample(n=sample_size).sort_index()
            
        # Searching
        if search_term:
            # Search in string columns
            mask = pd.Series([False] * len(display_df))
            for col in display_df.select_dtypes(include=['object']).columns:
                mask |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
            display_df = display_df[mask]
        
        # Data summary metrics
        st.subheader("📊 Data Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Records", f"{len(display_df):,}")
            
        with col2:
            if 'sep_intensity' in display_df.columns:
                avg_intensity = display_df['sep_intensity'].mean()
                st.metric("Avg Intensity", f"{avg_intensity:.2f}")
            
        with col3:
            if data_summary.get("data_quality"):
                high_events = data_summary["data_quality"].get("high_intensity_events", 0)
                st.metric("High Intensity", high_events)
                
        with col4:
            missing_values = display_df.isnull().sum().sum()
            st.metric("Missing Values", missing_values)
            
        with col5:
            completeness = (1 - missing_values / (len(display_df) * len(display_df.columns))) * 100
            st.metric("Completeness", f"{completeness:.1f}%")
        
        # Data quality analysis
        if data_summary.get("missing_values"):
            st.subheader("⚠️ Data Quality Issues")
            missing_df = pd.DataFrame([
                {"Column": col, "Missing Count": count, "Missing %": f"{(count/len(df_filtered)*100):.1f}%"}
                for col, count in data_summary["missing_values"].items()
            ])
            st.dataframe(missing_df, hide_index=True)
        
        # Export functionality
        st.subheader("📥 Data Export")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            export_format = st.selectbox("Export format:", ["csv", "json", "excel"])
            
        with export_col2:
            filename_prefix = st.text_input("Filename prefix:", value="solar_data")
            
        with export_col3:
            include_filters = st.checkbox("Include filter info", value=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.{export_format}"
        
        # Export buttons
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("📥 Export Current View", type="primary"):
                try:
                    if export_format == "csv":
                        data = display_df.to_csv(index=False)
                        mime_type = "text/csv"
                    elif export_format == "json":
                        data = display_df.to_json(orient='records', date_format='iso', indent=2)
                        mime_type = "application/json"
                    elif export_format == "excel":
                        # For Excel, we need to use BytesIO
                        import io
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            display_df.to_excel(writer, sheet_name='Solar Data', index=False)
                        data = buffer.getvalue()
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    st.download_button(
                        label=f"Download {filename}",
                        data=data,
                        file_name=filename,
                        mime=mime_type
                    )
                    st.success(f"✅ Export ready: {filename}")
                    
                except Exception as e:
                    st.error(f"❌ Export error: {e}")
        
        with export_col2:
            if include_filters and st.button("📋 Export Filter Summary"):
                filter_info = {
                    "export_timestamp": datetime.now().isoformat(),
                    "data_source": data_source,
                    "file_path": file_path,
                    "total_records": len(df_filtered),
                    "filters_applied": filters or {},
                    "data_summary": data_summary
                }
                
                filter_json = json.dumps(filter_info, indent=2, default=str)
                st.download_button(
                    label="Download Filter Info",
                    data=filter_json,
                    file_name=f"filter_info_{timestamp}.json",
                    mime="application/json"
                )
        
        # Interactive data table
        st.subheader("🗂️ Interactive Data Table")
        
        # Column selection
        available_columns = list(display_df.columns)
        selected_columns = st.multiselect(
            "Select columns to display:",
            available_columns,
            default=available_columns[:min(6, len(available_columns))]  # Show first 6 columns by default
        )
        
        if selected_columns:
            display_table = display_df[selected_columns]
        else:
            display_table = display_df
        
        # Display the interactive dataframe
        st.dataframe(
            display_table,
            use_container_width=True,
            height=500,
            column_config={
                col: st.column_config.NumberColumn(
                    format="%.3f"
                ) for col in display_table.select_dtypes(include=['float64']).columns
            }
        )
        
        # Quick statistics
        if not display_table.empty:
            st.subheader("📈 Quick Statistics")
            
            # Select numeric column for statistics
            numeric_columns = display_table.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_columns:
                stats_column = st.selectbox("Choose column for detailed stats:", numeric_columns)
                
                if stats_column:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Basic Statistics:**")
                        stats = display_table[stats_column].describe()
                        for stat, value in stats.items():
                            st.write(f"- **{stat.title()}:** {value:.3f}")
                    
                    with col2:
                        st.write("**Distribution:**")
                        fig_hist = px.histogram(
                            display_table, 
                            x=stats_column, 
                            title=f"Distribution of {stats_column}",
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)

if __name__ == "__main__":
    main()
