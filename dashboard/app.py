"""
Supply Chain Analytics Dashboard - Main Application

Interactive Streamlit dashboard for supply chain analytics and allocation management.
Includes data upload, mock data generation, forecasting, and allocation engines.
"""

import streamlit as st
import pandas as pd
import sys
import os
from typing import Dict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def main():
    """Main dashboard application"""
    st.set_page_config(
        page_title="Supply Chain AI Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🚀 Supply Chain AI Analytics & Allocation Management")
    st.markdown("*Enterprise-grade supply chain analytics with intelligent allocation*")
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    
    # Main navigation options
    page = st.sidebar.selectbox(
        "Choose Section:",
        [
            "🏠 Home",
            "📁 Data Management", 
            "📈 Analytics",
            "🔧 Allocation Engine",
            "🌍 Geographic Analysis"
        ]
    )
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home_page()
    elif page == "📁 Data Management":
        show_data_management()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "🔧 Allocation Engine":
        show_allocation_engine()
    elif page == "🌍 Geographic Analysis":
        show_geographic_analysis()


def show_home_page():
    """Display home page with project overview"""
    st.write("## Welcome to Your Supply Chain Command Center")
    
    # Quick start options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        ### 📁 Data Management
        Upload your own data or generate realistic scenarios
        - CSV/Excel upload with validation
        - Intelligent mock data generator
        - Industry-specific templates
        """)
        
    with col2:
        st.info("""
        ### 📊 Advanced Analytics
        Multi-forecast analysis and optimization
        - Statistical & ML forecasting
        - Push-pull point analysis
        - S&OP planning horizons
        """)
        
    with col3:
        st.info("""
        ### 🔧 Allocation Engine
        Real-time allocation with business rules
        - Customer classification
        - Probability-based reservations
        - Email intelligence processing
        """)
    
    # Key capabilities
    st.write("## 🎯 Platform Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("""
        **Analytics Features:**
        - Multi-model demand forecasting
        - Geographic supply-demand mapping
        - Warehouse transfer optimization
        - Risk analysis and monitoring
        - S&OP/S&OE integration
        """)
    
    with col2:
        st.write("""
        **Allocation Features:**
        - Real-time allocation engine
        - Business rules configuration
        - Dynamic customer prioritization
        - Email intelligence processing
        - Automated decision support
        """)
    
    # Getting started
    st.write("## 🚀 Getting Started")
    st.write("""
    1. **Upload Data**: Use your own supply chain data or generate mock scenarios
    2. **Explore Analytics**: Run forecasting and optimization analysis
    3. **Configure Allocation**: Set up business rules and customer priorities
    4. **Monitor Performance**: Track KPIs and allocation effectiveness
    """)


def show_data_management():
    """Data management section"""
    st.write("## 📁 Data Management Hub")
    st.write("Upload your supply chain data or generate realistic mock datasets for analysis.")
    
    # Data source options
    data_option = st.radio(
        "Choose data source:",
        ["📤 Upload Your Data", "🎲 Generate Mock Data", "📋 Download Templates"],
        horizontal=True
    )
    
    if data_option == "📤 Upload Your Data":
        show_data_upload_section()
            
    elif data_option == "🎲 Generate Mock Data":
        show_mock_data_section()
            
    else:  # Download Templates
        try:
            from data_management.data_templates import DataTemplates
            
            templates = DataTemplates()
            template_result = templates.template_interface()
            
            # Store selected industry for later use
            if template_result['industry']:
                st.session_state.selected_industry = template_result['industry']
                st.session_state.industry_templates = template_result['templates']
                
        except ImportError as e:
            st.error(f"Template module error: {e}")
            # Fallback to simple templates
            st.write("### 📋 Basic Templates")
            basic_templates = {
                "Sales Data": "date,product_id,customer_id,quantity,unit_price",
                "Inventory Data": "product_id,location_id,quantity_on_hand,reorder_point",
                "Customer Data": "customer_id,customer_name,segment,country"
            }
            
            for name, headers in basic_templates.items():
                st.download_button(
                    label=f"📥 {name} Template",
                    data=headers,
                    file_name=f"{name.lower().replace(' ', '_')}_template.csv",
                    mime="text/csv"
                )


def show_data_upload_section():
    """Enhanced data upload with real functionality"""
    st.write("### 📤 Upload Your Supply Chain Data")
    
    try:
        from data_management.file_upload import DataUploadManager
        
        upload_manager = DataUploadManager()
        uploaded_data = upload_manager.upload_interface()
        
        if uploaded_data is not None:
            # Store in session state
            st.session_state.uploaded_data = uploaded_data
            st.session_state.data_source = "uploaded"
            
            # Success actions
            st.success("🎉 Data uploaded successfully! Ready for analysis.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 View Basic Analysis"):
                    st.session_state.show_analysis = True
                    st.rerun()
            with col2:
                # Download processed data
                csv = uploaded_data.to_csv(index=False)
                st.download_button(
                    label="💾 Download Processed Data",
                    data=csv,
                    file_name="processed_data.csv",
                    mime="text/csv"
                )
    
    except ImportError as e:
        st.error(f"Module import error: {e}")
        st.info("Make sure you're running from the project root directory")
        st.code("streamlit run dashboard/app.py")
    
    # Show analysis if requested
    if st.session_state.get('show_analysis', False) and 'uploaded_data' in st.session_state:
        show_basic_analysis()


def show_basic_analysis():
    """Show basic analysis of uploaded data"""
    df = st.session_state.uploaded_data
    
    st.write("### 📈 Basic Data Analysis")
    
    # Data overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    # Numeric analysis
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        st.write("**Numeric Summary:**")
        st.dataframe(df[numeric_cols].describe())
        
        # Simple visualization
        if len(numeric_cols) > 0:
            chart_col = st.selectbox("Select column to visualize:", numeric_cols)
            if chart_col:
                chart_data = df[chart_col].value_counts().head(10)
                if len(chart_data) > 1:
                    st.bar_chart(chart_data)
                else:
                    st.write(f"Only one unique value found: {chart_data.index[0]}")
    
    # Text column analysis
    text_cols = df.select_dtypes(include=['object']).columns
    if len(text_cols) > 0:
        st.write("**Text Columns Summary:**")
        for col in text_cols[:5]:
            unique_vals = df[col].nunique()
            st.write(f"- **{col}**: {unique_vals} unique values")
            if unique_vals <= 10:
                st.write(f"  Values: {list(df[col].unique())}")
    
    # Data sample
    st.write("**Data Sample:**")
    st.dataframe(df.head())


def show_mock_data_section():
    """Mock data generation interface"""
    st.write("### 🎲 Generate Realistic Mock Data")
    st.write("Create comprehensive supply chain datasets with realistic patterns and relationships.")
    
    try:
        from data_management.mock_data_generator import MockDataGenerator
        
        generator = MockDataGenerator()
        mock_datasets = generator.generation_interface()
        
        if mock_datasets:
            # Store in session state
            st.session_state.mock_datasets = mock_datasets
            st.session_state.data_source = "mock"
            
            # Success message and next steps
            st.success("✅ Mock data generated successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Analyze Generated Data"):
                    if 'sales' in mock_datasets:
                        st.session_state.uploaded_data = mock_datasets['sales']
                        st.session_state.show_analysis = True
                        st.rerun()
            
            with col2:
                if st.button("🌍 View All Datasets"):
                    st.session_state.show_all_datasets = True
                    st.rerun()
            
            # Show comprehensive data view if requested
            if st.session_state.get('show_all_datasets', False):
                show_comprehensive_data_view(mock_datasets)
    
    except ImportError as e:
        st.error(f"Module import error: {e}")
        st.info("Make sure the mock data generator module is properly installed")


def show_comprehensive_data_view(datasets: Dict[str, pd.DataFrame]):
    """Show comprehensive view of all generated datasets"""
    st.write("### 📊 Complete Supply Chain Dataset Overview")
    
    # Dataset relationships
    st.write("**Dataset Relationships:**")
    st.write("- Products ↔ Sales (product_id)")
    st.write("- Customers ↔ Sales (customer_id)")
    st.write("- Products ↔ Inventory (product_id)")
    st.write("- Suppliers ↔ Products (product_id)")
    
    # Key metrics across datasets
    if 'sales' in datasets and 'customers' in datasets and 'products' in datasets:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_revenue = datasets['sales']['total_amount'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
            
        with col2:
            avg_order_value = datasets['sales']['total_amount'].mean()
            st.metric("Avg Order Value", f"${avg_order_value:.2f}")
            
        with col3:
            active_customers = datasets['sales']['customer_id'].nunique()
            st.metric("Active Customers", f"{active_customers}")
    
    # Individual dataset tabs
    tab_names = list(datasets.keys())
    tabs = st.tabs([name.title() for name in tab_names])
    
    for i, (name, df) in enumerate(datasets.items()):
        with tabs[i]:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.dataframe(df, height=300)
            
            with col2:
                st.write(f"**{name.title()} Info:**")
                st.write(f"Rows: {len(df):,}")
                st.write(f"Columns: {len(df.columns)}")
                
                # Dataset-specific insights
                if name == 'sales':
                    date_range = pd.to_datetime(df['date'])
                    st.write(f"Date Range: {date_range.min().strftime('%Y-%m-%d')} to {date_range.max().strftime('%Y-%m-%d')}")
                elif name == 'customers':
                    segments = df['segment'].value_counts()
                    st.write("**Segments:**")
                    for segment, count in segments.items():
                        st.write(f"- {segment}: {count}")
                elif name == 'products':
                    categories = df['category'].value_counts()
                    st.write("**Categories:**")
                    for category, count in categories.head(3).items():
                        st.write(f"- {category}: {count}")
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {name.title()}",
                    data=csv,
                    file_name=f"mock_{name}.csv",
                    mime="text/csv",
                    key=f"download_{name}"
                )


def show_analytics():
    """Analytics section"""
    st.write("## 📈 Advanced Supply Chain Analytics")
    
    # Check for available data
    if not ('uploaded_data' in st.session_state or 'mock_datasets' in st.session_state):
        st.warning("⚠️ No data available. Please upload data or generate mock data first.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📁 Go to Data Management"):
                st.experimental_rerun()
        return
    
    # Analytics module selection
    analytics_module = st.selectbox(
        "Choose Analytics Module:",
        [
            "📈 Demand Forecasting",
            "📊 Data Exploration", 
            "📦 Inventory Analysis"
        ]
    )
    
    if analytics_module == "📈 Demand Forecasting":
        show_demand_forecasting()
    elif analytics_module == "📊 Data Exploration":
        show_data_exploration()
    elif analytics_module == "📦 Inventory Analysis":
        show_inventory_analysis()

def show_demand_forecasting():
    """Demand forecasting interface"""
    try:
        from forecasting.demand_forecasting import DemandForecaster
        
        # Get available data
        if 'uploaded_data' in st.session_state:
            data = st.session_state.uploaded_data
            st.info("Using uploaded data for forecasting")
        elif 'mock_datasets' in st.session_state and 'sales' in st.session_state.mock_datasets:
            data = st.session_state.mock_datasets['sales']
            st.info("Using generated mock data for forecasting")
        else:
            st.error("No suitable data found for forecasting")
            return
        
        # Run forecasting
        forecaster = DemandForecaster()
        forecast_result = forecaster.forecasting_interface(data)
        
        if forecast_result:
            st.session_state.latest_forecast = forecast_result
            
    except ImportError as e:
        st.error(f"Forecasting module error: {e}")
        st.info("Forecasting module in development")


def show_data_exploration():
    """Data exploration interface"""
    st.write("### 📊 Data Exploration")
    st.info("🚧 Data exploration module coming soon!")


def show_inventory_analysis():
    """Inventory analysis interface"""
    st.write("### 📦 Inventory Analysis")
    st.info("🚧 Inventory analysis module coming soon!")


def show_allocation_engine():
    """Allocation engine section"""
    st.write("## 🔧 Intelligent Allocation Engine")
    st.info("🚧 Allocation engine in development. Coming soon!")
    
    st.write("**Planned Allocation Features:**")
    st.write("- ⚙️ Business Rules Configuration")
    st.write("- 👥 Customer Classification")
    st.write("- 📋 Real-Time Allocation Dashboard")
    st.write("- 📧 Email Intelligence")
    st.write("- 🔄 Warehouse Transfer Optimization")


def show_geographic_analysis():
    """Geographic analysis section"""
    st.write("## 🌍 Geographic Supply Chain Intelligence")
    st.info("🚧 Geographic analysis in development. Coming soon!")
    
    st.write("**Planned Geographic Features:**")
    st.write("- 🗺️ Global Network Mapping")
    st.write("- 📍 Supply-Demand Flow Analysis")
    st.write("- 🚚 Transportation Optimization")
    st.write("- ⚠️ Geographic Risk Assessment")


if __name__ == "__main__":
    main()