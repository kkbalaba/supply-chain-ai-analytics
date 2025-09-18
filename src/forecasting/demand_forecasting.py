"""
Basic Demand Forecasting Module
Implements simple forecasting methods for supply chain demand prediction
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DemandForecaster:
    """Basic demand forecasting using multiple methods"""
    
    def __init__(self):
        self.methods = {
            'moving_average': 'Moving Average',
            'exponential_smoothing': 'Exponential Smoothing',
            'linear_trend': 'Linear Trend',
            'seasonal_naive': 'Seasonal Naive',
            'holt_winters': 'Holt-Winters (Triple Smoothing)',
            'arima': 'ARIMA (Auto-Regressive)',
            'random_walk': 'Random Walk with Drift'
        }
        self.aggregation_options = ["Daily", "Weekly", "Monthly", "Yearly"]
    
    def forecasting_interface(self, data: pd.DataFrame) -> Dict:
        """Streamlit interface for demand forecasting"""
        st.subheader(" 📈  Demand Forecasting")
        st.write("Generate demand forecasts using historical sales data")

        # Data preparation
        forecast_data = self._prepare_data(data)
        if forecast_data is None:
            return {}

        # Forecasting parameters
        col1, col2 = st.columns(2)

        with col1:
            aggregation = st.selectbox("Data Aggregation", self.aggregation_options)

            # Dynamic forecast periods based on aggregation
            if aggregation == "Daily":
                period_label = "days"
                default_periods = 30
                min_periods, max_periods = 7, 90
            elif aggregation == "Weekly":
                period_label = "weeks"
                default_periods = 12
                min_periods, max_periods = 4, 52
            elif aggregation == "Monthly":
                period_label = "months"
                default_periods = 6
                min_periods, max_periods = 3, 24
            else:  # Yearly
                period_label = "years"
                default_periods = 2
                min_periods, max_periods = 1, 5

            forecast_periods = st.slider(
                f"Forecast Periods ({period_label})",
                min_periods, max_periods, default_periods
            )

        with col2:
            method = st.selectbox("Forecasting Method", list(self.methods.values()))
            confidence_level = st.slider("Confidence Level (%)", 80, 99, 95)

        # Advanced options
        with st.expander("Advanced Options"):
            col3, col4 = st.columns(2)
            with col3:
                if method in ['ARIMA (Auto-Regressive)', 'Holt-Winters (Triple Smoothing)']:
                    seasonality_periods = st.number_input(
                        "Seasonality Periods",
                        min_value=2, max_value=52, value=12,
                        help="Number of periods in one seasonal cycle"
                    )
                else:
                    seasonality_periods = 12

            with col4:
                if method == 'Exponential Smoothing':
                    alpha = st.slider("Smoothing Parameter (α)", 0.1, 0.9, 0.3)
                else:
                    alpha = 0.3

        # Product selection
        if 'product_id' in forecast_data.columns:
            products = forecast_data['product_id'].unique()
            selected_product = st.selectbox("Select Product", ['All Products'] + list(products))
        else:
            selected_product = 'All Products'

        # Generate forecast button
        if st.button("Generate Forecast", type="primary"):
            with st.spinner("Generating demand forecast..."):
                try:
                    forecast_result = self._generate_forecast(
                        forecast_data,
                        method,
                        forecast_periods,
                        aggregation,
                        selected_product,
                        confidence_level,
                        seasonality_periods,
                        alpha
                    )

                    if forecast_result:
                        self._display_forecast_results(forecast_result)
                        return forecast_result

                except Exception as e:
                    st.error(f"Forecasting error: {str(e)}")
                    return {}

        return {}
    
    def _prepare_data(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Prepare data for forecasting"""
        # Check required columns
        required_cols = ['date']
        if not all(col in data.columns for col in required_cols):
            st.error("Data must contain 'date' column for forecasting")
            return None
        
        # Determine quantity column
        quantity_cols = ['quantity', 'total_amount', 'sales', 'demand']
        quantity_col = None
        for col in quantity_cols:
            if col in data.columns:
                quantity_col = col
                break
        
        if quantity_col is None:
            st.error("Data must contain a quantity/sales column")
            return None
        
        # Prepare the dataset
        df = data.copy()
        
        try:
            df['date'] = pd.to_datetime(df['date'])
            df[quantity_col] = pd.to_numeric(df[quantity_col], errors='coerce').fillna(0)
            df = df.sort_values('date')
            
            # Handle negative values
            df[quantity_col] = df[quantity_col].clip(lower=0)
            
            # Remove rows with invalid dates or quantities
            df = df.dropna(subset=['date', quantity_col])
            
            if len(df) == 0:
                st.error("No valid data remaining after cleaning")
                return None
                
            st.success(f"Data prepared: {len(df)} records, using '{quantity_col}' as demand")
            return df
            
        except Exception as e:
            st.error(f"Error preparing data: {str(e)}")
            return None
    
    def _generate_forecast(self, data: pd.DataFrame, method: str, periods: int,
                          aggregation: str, product: str, confidence: int,
                          seasonality_periods: int = 12, alpha: float = 0.3) -> Dict:
        """Generate forecast using selected method"""

        # Filter data by product if specified
        if product != 'All Products' and 'product_id' in data.columns:
            data = data[data['product_id'] == product]

        # Aggregate data
        agg_data = self._aggregate_data(data, aggregation)
        min_periods_req = 7 if aggregation == "Daily" else 4

        if len(agg_data) < min_periods_req:
            st.error(f"Insufficient data for forecasting (minimum {min_periods_req} periods required)")
            return {}

        # Get method key
        method_key = None
        for key, value in self.methods.items():
            if value == method:
                method_key = key
                break

        # Generate forecast
        if method_key == 'moving_average':
            forecast = self._moving_average_forecast(agg_data, periods, aggregation)
        elif method_key == 'exponential_smoothing':
            forecast = self._exponential_smoothing_forecast(agg_data, periods, aggregation, alpha)
        elif method_key == 'linear_trend':
            forecast = self._linear_trend_forecast(agg_data, periods, aggregation)
        elif method_key == 'seasonal_naive':
            forecast = self._seasonal_naive_forecast(agg_data, periods, aggregation)
        elif method_key == 'holt_winters':
            forecast = self._holt_winters_forecast(agg_data, periods, aggregation, seasonality_periods)
        elif method_key == 'arima':
            forecast = self._arima_forecast(agg_data, periods, aggregation)
        elif method_key == 'random_walk':
            forecast = self._random_walk_forecast(agg_data, periods, aggregation)
        else:
            forecast = self._moving_average_forecast(agg_data, periods, aggregation)

        # Add confidence intervals
        forecast = self._add_confidence_intervals(forecast, confidence)

        # Calculate accuracy metrics
        accuracy = self._calculate_accuracy(agg_data)

        return {
            'historical': agg_data,
            'forecast': forecast,
            'method': method,
            'periods': periods,
            'aggregation': aggregation,
            'product': product,
            'accuracy': accuracy
        }
    
    def _aggregate_data(self, data: pd.DataFrame, aggregation: str) -> pd.DataFrame:
        """Aggregate data by time period"""
        quantity_col = None
        for col in ['quantity', 'total_amount', 'sales', 'demand']:
            if col in data.columns:
                quantity_col = col
                break
        
        if quantity_col is None:
            raise ValueError("No quantity column found")
        
        # Ensure date is datetime and quantity is numeric
        data = data.copy()
        data['date'] = pd.to_datetime(data['date'])
        data[quantity_col] = pd.to_numeric(data[quantity_col], errors='coerce').fillna(0)
        
        if aggregation == 'Daily':
            agg_data = data.groupby(data['date'].dt.date)[quantity_col].sum().reset_index()
            agg_data['date'] = pd.to_datetime(agg_data['date'])
        elif aggregation == 'Weekly':
            agg_data = data.groupby(data['date'].dt.to_period('W'))[quantity_col].sum().reset_index()
            agg_data['date'] = agg_data['date'].dt.start_time
        elif aggregation == 'Monthly':
            agg_data = data.groupby(data['date'].dt.to_period('M'))[quantity_col].sum().reset_index()
            agg_data['date'] = agg_data['date'].dt.start_time
        else:  # Yearly
            agg_data = data.groupby(data['date'].dt.to_period('Y'))[quantity_col].sum().reset_index()
            agg_data['date'] = agg_data['date'].dt.start_time

        # Ensure proper column names and types
        agg_data = agg_data.sort_values('date').reset_index(drop=True)
        agg_data.columns = ['date', 'demand']
        agg_data['demand'] = pd.to_numeric(agg_data['demand'], errors='coerce').fillna(0)
        
        return agg_data
    
    def _generate_forecast_dates(self, last_date: pd.Timestamp, periods: int, aggregation: str) -> List[pd.Timestamp]:
        """Generate forecast dates based on aggregation type"""
        forecast_dates = []

        for i in range(1, periods + 1):
            if aggregation == "Daily":
                next_date = last_date + pd.Timedelta(days=i)
            elif aggregation == "Weekly":
                next_date = last_date + pd.Timedelta(weeks=i)
            elif aggregation == "Monthly":
                next_date = last_date + pd.DateOffset(months=i)
            else:  # Yearly
                next_date = last_date + pd.DateOffset(years=i)

            forecast_dates.append(next_date)

        return forecast_dates

    def _moving_average_forecast(self, data: pd.DataFrame, periods: int, aggregation: str) -> pd.DataFrame:
        """Simple moving average forecast"""
        window = min(7, len(data) // 2) if len(data) > 1 else 1
        moving_avg = data['demand'].rolling(window=window).mean().iloc[-1]

        forecast_dates = self._generate_forecast_dates(data['date'].iloc[-1], periods, aggregation)

        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': [float(moving_avg)] * periods
        })
    
    def _exponential_smoothing_forecast(self, data: pd.DataFrame, periods: int, aggregation: str, alpha: float = 0.3) -> pd.DataFrame:
        """Exponential smoothing forecast"""
        smoothed = [float(data['demand'].iloc[0])]
        for i in range(1, len(data)):
            smoothed.append(alpha * float(data['demand'].iloc[i]) + (1 - alpha) * smoothed[-1])

        forecast_value = float(smoothed[-1])
        forecast_dates = self._generate_forecast_dates(data['date'].iloc[-1], periods, aggregation)

        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': [forecast_value] * periods
        })
    
    def _linear_trend_forecast(self, data: pd.DataFrame, periods: int, aggregation: str) -> pd.DataFrame:
        """Linear trend forecast"""
        data = data.copy()
        data['time_index'] = range(len(data))
        
        x = data['time_index'].values.astype(float)
        y = data['demand'].values.astype(float)
        
        if len(x) < 2:
             return self._moving_average_forecast(data, periods, aggregation)
        
        n = len(x)
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        slope_numerator = np.sum((x - x_mean) * (y - y_mean))
        slope_denominator = np.sum((x - x_mean) ** 2)

        if slope_denominator == 0:
            slope = 0
        else:
            slope = slope_numerator / slope_denominator
            
        intercept = y_mean - slope * x_mean
        
        future_indices = range(len(data), len(data) + periods)
        forecast_values = [max(0, float(slope * i + intercept)) for i in future_indices]
        
        forecast_dates = self._generate_forecast_dates(data['date'].iloc[-1], periods, aggregation)
        
        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast_values
        })
    
    def _seasonal_naive_forecast(self, data: pd.DataFrame, periods: int, aggregation: str) -> pd.DataFrame:
        """Seasonal naive forecast (repeat last season)"""
        season_length = min(7, len(data))
        
        seasonal_pattern = data['demand'].iloc[-season_length:].values.astype(float)
        
        forecast_values = []
        for i in range(periods):
            forecast_values.append(float(seasonal_pattern[i % len(seasonal_pattern)]))
        
        forecast_dates = self._generate_forecast_dates(data['date'].iloc[-1], periods, aggregation)
        
        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast_values
        })

    def _holt_winters_forecast(self, data: pd.DataFrame, periods: int, aggregation: str, season_length: int = 12) -> pd.DataFrame:
        """Holt-Winters triple exponential smoothing"""
        values = data['demand'].values.astype(float)

        if len(values) < season_length * 2:
            st.warning(f"Insufficient data for Holt-Winters (requires {season_length*2} periods). Falling back to Exponential Smoothing.")
            return self._exponential_smoothing_forecast(data, periods, aggregation)

        alpha, beta, gamma = 0.3, 0.1, 0.1
        
        level = np.mean(values[:season_length])
        trend = (values[season_length] - values[0]) / season_length
        seasonal_components = list(values[:season_length] - level)

        forecasts = []
        for i in range(len(values)):
            if i >= season_length:
                # Forecasting
                forecast_val = level + trend + seasonal_components[i % season_length]
                forecasts.append(forecast_val)

            # Updating
            last_level = level
            level = alpha * (values[i] - seasonal_components[i % season_length]) + (1 - alpha) * (level + trend)
            trend = beta * (level - last_level) + (1 - beta) * trend
            seasonal_components[i % season_length] = gamma * (values[i] - level) + (1 - gamma) * seasonal_components[i % season_length]

        # Generate future forecasts
        forecast_values = []
        for i in range(1, periods + 1):
            seasonal_idx = (len(values) + i - 1) % season_length
            forecast_values.append(level + i * trend + seasonal_components[seasonal_idx])

        forecast_dates = self._generate_forecast_dates(data['date'].iloc[-1], periods, aggregation)

        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': [max(0, f) for f in forecast_values]
        })

    def _arima_forecast(self, data: pd.DataFrame, periods: int, aggregation: str) -> pd.DataFrame:
        """Simple ARIMA-like forecast"""
        values = data['demand'].values.astype(float)

        if len(values) < 3:
            return self._moving_average_forecast(data, periods, aggregation)

        y = values[1:]
        x = values[:-1]

        if np.var(x) > 0:
            ar_coef = np.cov(x, y)[0, 1] / np.var(x)
            intercept = np.mean(y) - ar_coef * np.mean(x)
        else:
            ar_coef = 0
            intercept = np.mean(values)

        forecast_values = []
        last_value = values[-1]

        for _ in range(periods):
            next_forecast = intercept + ar_coef * last_value
            forecast_values.append(max(0, next_forecast))
            last_value = next_forecast

        forecast_dates = self._generate_forecast_dates(data['date'].iloc[-1], periods, aggregation)

        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast_values
        })

    def _random_walk_forecast(self, data: pd.DataFrame, periods: int, aggregation: str) -> pd.DataFrame:
        """Random walk with drift forecast"""
        values = data['demand'].values.astype(float)

        if len(values) > 1:
            changes = np.diff(values)
            drift = np.mean(changes)
            std_dev = np.std(changes)
        else:
            drift = 0
            std_dev = np.std(values) if len(values) > 0 else 1

        forecast_values = []
        last_value = values[-1] if len(values) > 0 else 0

        for _ in range(periods):
            next_forecast = last_value + drift + np.random.normal(0, std_dev * 0.1)  # Small random component
            forecast_values.append(max(0, next_forecast))
            last_value = next_forecast

        forecast_dates = self._generate_forecast_dates(data['date'].iloc[-1], periods, aggregation)

        return pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast_values
        })

    def _add_confidence_intervals(self, forecast: pd.DataFrame, confidence: int) -> pd.DataFrame:
        """Add confidence intervals to forecast"""
        forecast_std = forecast['forecast'].std()
        if forecast_std == 0 or pd.isna(forecast_std):
            forecast_std = forecast['forecast'].mean() * 0.1
        
        z_scores = {80: 1.28, 85: 1.44, 90: 1.64, 95: 1.96, 99: 2.58}
        z = z_scores.get(confidence, 1.96)
        
        margin = z * forecast_std
        
        forecast['lower_bound'] = (forecast['forecast'] - margin).clip(lower=0)
        forecast['upper_bound'] = forecast['forecast'] + margin
        
        return forecast
    
    def _calculate_accuracy(self, data: pd.DataFrame) -> Dict:
        """Calculate forecast accuracy metrics"""
        if len(data) < 2:
            return {'mae': 0, 'mape': 0, 'rmse': 0}
        
        actual = data['demand'].iloc[1:].values.astype(float)
        naive_forecast = data['demand'].iloc[:-1].values.astype(float)
        
        mae = np.mean(np.abs(actual - naive_forecast))
        mape = np.mean(np.abs((actual - naive_forecast) / np.maximum(actual, 1e-8))) * 100
        rmse = np.sqrt(np.mean((actual - naive_forecast) ** 2))
        
        return {
            'mae': round(mae, 2),
            'mape': round(mape, 2),
            'rmse': round(rmse, 2)
        }
    
    def _display_forecast_results(self, result: Dict):
        """Display forecast results with visualizations"""
        st.subheader("📊 Forecast Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_forecast = result['forecast']['forecast'].mean()
            st.metric("Avg Forecast", f"{avg_forecast:.1f}")
        
        with col2:
            total_forecast = result['forecast']['forecast'].sum()
            st.metric("Total Forecast", f"{total_forecast:.0f}")
        
        with col3:
            st.metric("MAE", f"{result['accuracy']['mae']:.1f}")
        
        with col4:
            st.metric("MAPE", f"{result['accuracy']['mape']:.1f}%")
        
        self._create_forecast_chart(result)
        
        forecast_csv = result['forecast'].to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast",
            data=forecast_csv,
            file_name=f"demand_forecast_{result['method'].lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
    
    def _create_forecast_chart(self, result: Dict):
        """Create interactive forecast visualization"""
        historical = result['historical']
        forecast = result['forecast']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical['date'],
            y=historical['demand'],
            mode='lines+markers',
            name='Historical Demand',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['date'],
            y=forecast['forecast'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        if 'upper_bound' in forecast.columns and 'lower_bound' in forecast.columns:
            fig.add_trace(go.Scatter(
                x=list(forecast['date']) + list(forecast['date'][::-1]),
                y=list(forecast['upper_bound']) + list(forecast['lower_bound'][::-1]),
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval',
                showlegend=True
            ))
        
        fig.update_layout(
            title=f"Demand Forecast - {result['method']}",
            xaxis_title="Date",
            yaxis_title="Demand",
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)