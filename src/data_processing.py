"""
Data Processing Module for Supply Chain Analytics

Handles data loading, cleaning, validation, and feature engineering
for supply chain datasets including sales, inventory, and customer data.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sales_data(file_path: str) -> pd.DataFrame:
    """
    Load sales data from CSV or Excel file.
    
    Args:
        file_path (str): Path to the sales data file
        
    Returns:
        pd.DataFrame: Loaded sales dataframe
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        logger.info(f"Successfully loaded {len(df)} sales records from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading sales data: {e}")
        raise


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate sales data.
    
    Args:
        df (pd.DataFrame): Raw sales dataframe
        
    Returns:
        pd.DataFrame: Cleaned sales dataframe
    """
    # Convert date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Remove negative quantities
    if 'quantity' in df.columns:
        df = df[df['quantity'] > 0]
    
    # Remove null customer/product IDs
    essential_cols = ['customer_id', 'product_id']
    for col in essential_cols:
        if col in df.columns:
            df = df.dropna(subset=[col])
    
    logger.info(f"Data cleaning completed. {len(df)} records remaining.")
    return df


def create_time_features(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """
    Create time-based features for forecasting.
    
    Args:
        df (pd.DataFrame): Dataframe with date column
        date_col (str): Name of the date column
        
    Returns:
        pd.DataFrame: Dataframe with additional time features
    """
    if date_col not in df.columns:
        logger.warning(f"Date column '{date_col}' not found")
        return df
    
    # Ensure date column is datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Create time features
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['quarter'] = df[date_col].dt.quarter
    df['day_of_week'] = df[date_col].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6])
    
    logger.info("Time features created successfully")
    return df


def validate_data_quality(df: pd.DataFrame) -> Dict[str, float]:
    """
    Generate data quality metrics.
    
    Args:
        df (pd.DataFrame): Dataframe to analyze
        
    Returns:
        Dict[str, float]: Data quality metrics
    """
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    
    quality_metrics = {
        'completeness': 1 - (missing_cells / total_cells),
        'uniqueness': 1 - (duplicate_rows / len(df)),
        'missing_percentage': (missing_cells / total_cells) * 100,
        'duplicate_percentage': (duplicate_rows / len(df)) * 100
    }
    
    logger.info("Data quality assessment completed")
    return quality_metrics


if __name__ == "__main__":
    print("Data Processing Module - Ready for development!")
    print("Functions available:")
    print("- load_sales_data()")
    print("- clean_sales_data()")
    print("- create_time_features()")
    print("- validate_data_quality()")
