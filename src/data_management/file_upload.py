"""
File Upload and Data Validation Module
"""

import pandas as pd
import streamlit as st
import chardet
from typing import Optional, Dict
import logging
from io import StringIO

logger = logging.getLogger(__name__)

class DataUploadManager:
    """Handles file uploads with validation and preview"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        
    def upload_interface(self) -> Optional[pd.DataFrame]:
        """Complete upload interface with validation"""
        st.subheader("Upload Your Supply Chain Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your supply chain data in CSV or Excel format"
        )
        
        if uploaded_file is not None:
            try:
                # Parse file based on extension
                if uploaded_file.name.endswith('.csv'):
                    df = self._parse_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Show results
                return self._show_upload_results(df, uploaded_file.name)
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                return None
        
        return None
    
    def _parse_csv(self, file) -> pd.DataFrame:
        """Parse CSV with encoding detection"""
        # Read file content
        content = file.read()
        
        # Detect encoding
        encoding = chardet.detect(content)['encoding']
        if encoding is None:
            encoding = 'utf-8'
        
        # Parse CSV
        content_str = content.decode(encoding)
        df = pd.read_csv(StringIO(content_str))
        
        return df
    
    def _show_upload_results(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Display upload results and data preview"""
        st.success(f"Successfully uploaded: {filename}")
        
        # Basic statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            missing_pct = (df.isnull().sum().sum() / df.size) * 100
            st.metric("Data Complete", f"{100-missing_pct:.1f}%")
        
        # Data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(10))
        
        # Column information
        with st.expander("Column Details"):
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum()
            })
            st.dataframe(col_info)
        
        return df