import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database.repository import DatabaseRepository
from infrastructure.database.models import get_db
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
def load_data():
    """Load data from database or generate mock data"""
    try:
        repo = DatabaseRepository()
        df = repo.get_sep_events_as_dataframe()
        if df.empty:
            # Generate mock data if database is empty
            sep, temp, ice, ozone, geomag = gerar_dados_mock()
            from adapters.data_adapter import integrar_dados
            df = integrar_dados(sep, temp, ice, ozone, geomag)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Fallback to mock data
        sep, temp, ice, ozone, geomag = gerar_dados_mock()
        from adapters.data_adapter import integrar_dados
        return integrar_dados(sep, temp, ice, ozone, geomag)

def main():
    # Header
    st.markdown('<h1 class="main-header">🌞 Solar Event Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")
        
        # Data refresh
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # Date range filter
        st.subheader("📅 Date Range")
        date_range = st.date_input(
            "Select date range",
            value=[],
            key="date_range"
        )
        
        # Intensity threshold
        st.subheader("⚡ Intensity Filter")
        intensity_threshold = st.slider(
            "Minimum SEP Intensity",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=0.1
        )
        
        # Analysis options
        st.subheader("🔬 Analysis Options")
        show_clustering = st.checkbox("Show Clustering Analysis", value=True)
        show_correlations = st.checkbox("Show Correlations", value=True)
        show_predictions = st.checkbox("Show Predictions", value=True)

    # Load data
    with st.spinner("Loading solar event data..."):
        df = load_data()
    
    # Apply filters
    if len(date_range) == 2:
        df = df[(df['date'] >= pd.Timestamp(date_range[0])) & 
                (df['date'] <= pd.Timestamp(date_range[1]))]
    
    df_filtered = df[df['sep_intensity'] >= intensity_threshold]
    
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
        st.header("📊 Data Explorer")
        
        # Data filtering options
        col1, col2 = st.columns(2)
        
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                ['date', 'sep_intensity', 'temperature', 'kp_index']
            )
            
        with col2:
            sort_order = st.radio("Sort order", ['Ascending', 'Descending'])
        
        # Sort data
        ascending = sort_order == 'Ascending'
        df_sorted = df_filtered.sort_values(sort_by, ascending=ascending)
        
        # Display data
        st.subheader(f"📋 Data Table ({len(df_sorted)} records)")
        
        # Data summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Date Range:**")
            if not df_sorted.empty:
                st.write(f"From: {df_sorted['date'].min().strftime('%Y-%m-%d')}")
                st.write(f"To: {df_sorted['date'].max().strftime('%Y-%m-%d')}")
        
        with col2:
            st.write("**Intensity Range:**")
            if not df_sorted.empty:
                st.write(f"Min: {df_sorted['sep_intensity'].min():.2f}")
                st.write(f"Max: {df_sorted['sep_intensity'].max():.2f}")
        
        with col3:
            if st.button("📥 Download CSV"):
                csv = df_sorted.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f"solar_events_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Display dataframe
        st.dataframe(
            df_sorted,
            use_container_width=True,
            height=400
        )
        
        # Data quality metrics
        st.subheader("📈 Data Quality")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            completeness = (1 - df_sorted.isnull().sum().sum() / (len(df_sorted) * len(df_sorted.columns))) * 100
            st.metric("Data Completeness", f"{completeness:.1f}%")
        
        with col2:
            duplicates = df_sorted.duplicated().sum()
            st.metric("Duplicate Records", duplicates)
        
        with col3:
            outliers = len(df_sorted[df_sorted['sep_intensity'] > df_sorted['sep_intensity'].quantile(0.99)])
            st.metric("Potential Outliers", outliers)
        
        with col4:
            data_points = len(df_sorted)
            st.metric("Total Data Points", data_points)

if __name__ == "__main__":
    main()
