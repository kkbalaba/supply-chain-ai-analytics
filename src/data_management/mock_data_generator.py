"""
Mock Data Generation Module
Creates realistic supply chain datasets for testing and demonstration
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
import streamlit as st

fake = Faker()

class MockDataGenerator:
    """Generate realistic supply chain mock data"""
    
    def __init__(self):
        self.fake = Faker()
        self.industry_templates = {
            'retail': {
                'categories': ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books'],
                'seasonality': {'Q1': 0.8, 'Q2': 1.0, 'Q3': 1.2, 'Q4': 1.5},
                'customer_segments': ['Premium', 'Standard', 'Budget'],
                'price_ranges': {'Electronics': (50, 2000), 'Clothing': (10, 300)}
            },
            'manufacturing': {
                'categories': ['Raw Materials', 'Components', 'Sub-assemblies', 'Finished Goods'],
                'seasonality': {'Q1': 1.1, 'Q2': 1.2, 'Q3': 0.9, 'Q4': 1.0},
                'customer_segments': ['Strategic', 'Key', 'Standard'],
                'price_ranges': {'Raw Materials': (5, 100), 'Components': (20, 500)}
            },
            'pharmaceutical': {
                'categories': ['Prescription', 'OTC', 'Medical Devices', 'Vitamins'],
                'seasonality': {'Q1': 1.3, 'Q2': 0.9, 'Q3': 1.0, 'Q4': 1.1},
                'customer_segments': ['Hospital', 'Pharmacy', 'Distributor'],
                'price_ranges': {'Prescription': (10, 500), 'OTC': (5, 50)}
            }
        }
    
    def generation_interface(self) -> Dict[str, pd.DataFrame]:
        """Streamlit interface for mock data generation"""
        st.subheader("Generate Mock Supply Chain Data")
        
        # Industry and parameters
        col1, col2 = st.columns(2)
        
        with col1:
            industry = st.selectbox("Industry Template:", [key.title() for key in self.industry_templates.keys()])
            num_products = st.slider("Products", 10, 500, 50)
            num_customers = st.slider("Customers", 20, 1000, 100)
        
        with col2:
            num_locations = st.slider("Warehouses", 3, 20, 5)
            time_periods = st.slider("Months History", 6, 36, 24)
            complexity = st.select_slider("Data Complexity", ["Simple", "Moderate", "Complex"], "Moderate")
        
        # Advanced options
        with st.expander("Advanced Options"):
            seasonal_strength = st.slider("Seasonal Variation", 0.0, 2.0, 1.0)
            demand_variability = st.slider("Demand Variability", 0.1, 1.0, 0.3)
            include_issues = st.checkbox("Include Supply Chain Issues", True)
        
        # Generate button
        if st.button("Generate Realistic Data", type="primary"):
            with st.spinner("Creating realistic supply chain scenarios..."):
                try:
                    datasets = self._generate_complete_dataset(
                        industry=industry.lower(),
                        num_products=num_products,
                        num_customers=num_customers,
                        num_locations=num_locations,
                        time_periods=time_periods,
                        seasonal_strength=seasonal_strength,
                        demand_variability=demand_variability,
                        complexity=complexity,
                        include_issues=include_issues
                    )
                    
                    st.success("Mock data generated successfully!")
                    self._preview_generated_data(datasets)
                    return datasets
                    
                except Exception as e:
                    st.error(f"Error generating data: {str(e)}")
                    return {}
        
        return {}
    
    def _generate_complete_dataset(self, **params) -> Dict[str, pd.DataFrame]:
        """Generate complete interconnected supply chain dataset"""
        datasets = {}
        
        # Generate master data first
        datasets['products'] = self._generate_products(params['num_products'], params['industry'])
        datasets['customers'] = self._generate_customers(params['num_customers'], params['industry'])
        datasets['locations'] = self._generate_locations(params['num_locations'])
        datasets['suppliers'] = self._generate_suppliers(datasets['products'])
        
        # Generate transactional data with relationships
        datasets['sales'] = self._generate_sales_data(
            datasets['products'], datasets['customers'], 
            params['time_periods'], params['demand_variability'], 
            params['seasonal_strength'], params['industry']
        )
        
        datasets['inventory'] = self._generate_inventory_data(
            datasets['products'], datasets['locations'], datasets['sales']
        )
        
        # Add supply chain issues if requested
        if params.get('include_issues', False):
            datasets['supply_issues'] = self._generate_supply_issues(
                datasets['products'], datasets['suppliers'], params['time_periods']
            )
        
        return datasets
    
    def _generate_products(self, num_products: int, industry: str) -> pd.DataFrame:
        """Generate realistic product master data"""
        template = self.industry_templates[industry]
        categories = template['categories']
        
        products = []
        for i in range(num_products):
            category = random.choice(categories)
            price_range = template['price_ranges'].get(category, (10, 100))
            
            # Create realistic product names
            if industry == 'retail':
                product_name = f"{self.fake.catch_phrase()} {category[:-1]}"
            elif industry == 'manufacturing':
                product_name = f"{category[:-1]} {random.choice(['Type A', 'Type B', 'Standard', 'Premium'])}"
            else:
                product_name = f"{self.fake.catch_phrase()} {category[:-1]}"
            
            unit_cost = round(random.uniform(price_range[0] * 0.6, price_range[1] * 0.7), 2)
            unit_price = round(unit_cost * random.uniform(1.3, 2.5), 2)
            
            products.append({
                'product_id': f"SKU_{i+1:04d}",
                'product_name': product_name,
                'category': category,
                'unit_cost': unit_cost,
                'unit_price': unit_price,
                'lead_time_days': random.randint(1, 90),
                'weight_kg': round(random.uniform(0.1, 50), 2),
                'shelf_life_days': random.randint(30, 365) if industry == 'pharmaceutical' else None
            })
        
        return pd.DataFrame(products)
    
    def _generate_customers(self, num_customers: int, industry: str) -> pd.DataFrame:
        """Generate realistic customer data with proper segmentation"""
        template = self.industry_templates[industry]
        segments = template['customer_segments']
        
        # Realistic segment distribution
        if industry == 'retail':
            segment_weights = [0.15, 0.60, 0.25]  # Premium, Standard, Budget
        elif industry == 'manufacturing':
            segment_weights = [0.10, 0.30, 0.60]  # Strategic, Key, Standard
        else:
            segment_weights = [0.20, 0.50, 0.30]  # Hospital, Pharmacy, Distributor
        
        customers = []
        for i in range(num_customers):
            segment = np.random.choice(segments, p=segment_weights)
            
            # Segment affects company size and credit
            if segment in ['Premium', 'Strategic', 'Hospital']:
                credit_multiplier = random.uniform(5, 10)
            elif segment in ['Standard', 'Key', 'Pharmacy']:
                credit_multiplier = random.uniform(2, 5)
            else:
                credit_multiplier = random.uniform(0.5, 2)
            
            customers.append({
                'customer_id': f"CUST_{i+1:04d}",
                'customer_name': self.fake.company(),
                'segment': segment,
                'country': self.fake.country(),
                'city': self.fake.city(),
                'industry_type': self.fake.bs(),
                'credit_limit': int(50000 * credit_multiplier),
                'payment_terms': random.choice(['Net 30', 'Net 60', 'Net 15', 'COD']),
                'established_date': self.fake.date_between(start_date='-10y', end_date='-1y')
            })
        
        return pd.DataFrame(customers)
    
    def _generate_locations(self, num_locations: int) -> pd.DataFrame:
        """Generate warehouse/location data"""
        location_types = ['Distribution Center', 'Warehouse', 'Store', 'Factory']
        
        locations = []
        for i in range(num_locations):
            locations.append({
                'location_id': f"LOC_{i+1:03d}",
                'location_name': f"{self.fake.city()} {random.choice(location_types)}",
                'location_type': random.choice(location_types),
                'country': self.fake.country(),
                'city': self.fake.city(),
                'latitude': float(self.fake.latitude()),
                'longitude': float(self.fake.longitude()),
                'capacity_units': random.randint(1000, 100000),
                'operational_since': self.fake.date_between(start_date='-10y', end_date='-1y')
            })
        
        return pd.DataFrame(locations)

    def _generate_suppliers(self, products: pd.DataFrame) -> pd.DataFrame:
        """Generate supplier information"""
        suppliers = []
        
        # Create some suppliers that serve multiple products
        supplier_names = [self.fake.company() for _ in range(min(20, len(products) // 3))]
        
        for _, product in products.iterrows():
            # Each product can have 1-3 suppliers
            num_suppliers = random.randint(1, min(3, len(supplier_names)))
            product_suppliers = random.sample(supplier_names, num_suppliers)
            
            for supplier_name in product_suppliers:
                supplier_id = f"SUP_{hash(supplier_name) % 999:03d}"
                
                suppliers.append({
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name,
                    'product_id': product['product_id'],
                    'lead_time_days': random.randint(7, 120),
                    'min_order_qty': random.randint(1, 100),
                    'unit_cost': round(product['unit_cost'] * random.uniform(0.8, 1.2), 2),
                    'reliability_score': round(random.uniform(0.7, 1.0), 2),
                    'country': self.fake.country(),
                    'payment_terms': random.choice(['Net 30', 'Net 60', 'COD', 'Net 45']),
                    'quality_rating': random.choice(['A', 'B', 'C'])
                })
        
        return pd.DataFrame(suppliers)
    
    def _generate_sales_data(self, products: pd.DataFrame, customers: pd.DataFrame, 
                           time_periods: int, variability: float, seasonality: float, 
                           industry: str) -> pd.DataFrame:
        """Generate realistic sales transactions with patterns"""
        template = self.industry_templates[industry]
        seasonal_factors = template['seasonality']
        
        sales = []
        start_date = datetime.now() - timedelta(days=time_periods * 30)
        
        # Create customer-product affinities
        customer_preferences = {}
        for _, customer in customers.iterrows():
            # Each customer prefers certain product categories
            preferred_categories = random.sample(
                template['categories'], 
                random.randint(1, min(3, len(template['categories'])))
            )
            customer_preferences[customer['customer_id']] = preferred_categories
        
        for days in range(time_periods * 30):
            current_date = start_date + timedelta(days=days)
            quarter = f"Q{((current_date.month - 1) // 3) + 1}"
            seasonal_multiplier = seasonal_factors.get(quarter, 1.0)
            
            # Number of transactions per day varies by industry
            if industry == 'retail':
                daily_transactions = random.randint(20, 150)
            elif industry == 'manufacturing':
                daily_transactions = random.randint(5, 30)
            else:
                daily_transactions = random.randint(10, 60)
            
            for _ in range(daily_transactions):
                # Select customer and product with realistic relationships
                customer = customers.sample(1).iloc[0]
                
                # Customer prefers certain categories
                preferred_cats = customer_preferences[customer['customer_id']]
                available_products = products[products['category'].isin(preferred_cats)]
                
                if len(available_products) == 0:
                    available_products = products
                
                product = available_products.sample(1).iloc[0]
                
                # Quantity based on customer segment and product type
                if customer['segment'] in ['Premium', 'Strategic', 'Hospital']:
                    base_qty = random.randint(50, 500)
                elif customer['segment'] in ['Standard', 'Key', 'Pharmacy']:
                    base_qty = random.randint(10, 100)
                else:
                    base_qty = random.randint(1, 50)
                
                # Apply seasonality and variability
                final_qty = max(1, int(base_qty * seasonal_multiplier * seasonality * 
                                     random.uniform(1-variability, 1+variability)))
                
                # Realistic pricing with discounts for large customers
                base_price = product['unit_price']
                if customer['segment'] in ['Premium', 'Strategic']:
                    discount = random.uniform(0.05, 0.15)
                    final_price = base_price * (1 - discount)
                else:
                    final_price = base_price * random.uniform(0.95, 1.05)
                
                sales.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'order_id': f"ORD_{self.fake.uuid4()[:8].upper()}",
                    'product_id': product['product_id'],
                    'customer_id': customer['customer_id'],
                    'quantity': final_qty,
                    'unit_price': round(final_price, 2),
                    'total_amount': round(final_qty * final_price, 2),
                    'order_status': np.random.choice(
                        ['Completed', 'Shipped', 'Pending'], 
                        p=[0.85, 0.10, 0.05]
                    ),
                    'sales_channel': random.choice(['Direct', 'Online', 'Distributor', 'Retail'])
                })
        
        return pd.DataFrame(sales)
    
    def _generate_inventory_data(self, products: pd.DataFrame, locations: pd.DataFrame, 
                               sales: pd.DataFrame) -> pd.DataFrame:
        """Generate realistic current inventory levels based on sales patterns"""
        inventory = []
        
        # Calculate average demand per product for realistic inventory levels
        product_demand = sales.groupby('product_id')['quantity'].agg(['mean', 'sum', 'count']).fillna(0)
        
        for _, product in products.iterrows():
            for _, location in locations.iterrows():
                # Not all products in all locations (80% coverage)
                if random.random() > 0.2:
                    
                    # Base inventory on historical demand
                    avg_demand = product_demand.loc[product['product_id'], 'mean'] if product['product_id'] in product_demand.index else 10
                    total_demand = product_demand.loc[product['product_id'], 'sum'] if product['product_id'] in product_demand.index else 50
                    
                    # Calculate realistic inventory levels
                    safety_stock = max(5, int(avg_demand * random.uniform(1, 3)))
                    max_stock = max(safety_stock * 3, int(avg_demand * random.uniform(5, 15)))
                    current_stock = random.randint(0, max_stock)
                    allocated = min(current_stock, random.randint(0, int(current_stock * 0.3)))
                    
                    inventory.append({
                        'product_id': product['product_id'],
                        'location_id': location['location_id'],
                        'quantity_on_hand': current_stock,
                        'quantity_allocated': allocated,
                        'quantity_available': current_stock - allocated,
                        'reorder_point': safety_stock,
                        'max_stock': max_stock,
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'abc_classification': np.random.choice(['A', 'B', 'C'], p=[0.2, 0.3, 0.5])
                    })
        
        return pd.DataFrame(inventory)

    def _generate_supply_issues(self, products: pd.DataFrame, suppliers: pd.DataFrame, 
                              time_periods: int) -> pd.DataFrame:
        """Generate supply chain issues and disruptions"""
        issues = []
        start_date = datetime.now() - timedelta(days=time_periods * 30)
        
        # Generate random supply issues
        issue_types = [
            'Delayed Shipment', 'Quality Issue', 'Supplier Capacity Constraint',
            'Transportation Delay', 'Weather Disruption', 'Raw Material Shortage',
            'Labor Strike', 'Port Congestion'
        ]
        
        # Generate 1-3 issues per month on average
        num_issues = random.randint(time_periods, time_periods * 3)
        
        for _ in range(num_issues):
            issue_date = start_date + timedelta(days=random.randint(0, time_periods * 30))
            
            # Random product and supplier
            product = products.sample(1).iloc[0]
            supplier_options = suppliers[suppliers['product_id'] == product['product_id']]
            
            if len(supplier_options) > 0:
                supplier = supplier_options.sample(1).iloc[0]
                
                issue_type = random.choice(issue_types)
                severity = random.choice(['Low', 'Medium', 'High', 'Critical'])
                
                # Impact duration based on severity
                if severity == 'Critical':
                    duration_days = random.randint(7, 30)
                elif severity == 'High':
                    duration_days = random.randint(3, 14)
                elif severity == 'Medium':
                    duration_days = random.randint(1, 7)
                else:
                    duration_days = random.randint(1, 3)
                
                issues.append({
                    'issue_id': f"ISS_{len(issues)+1:04d}",
                    'date_reported': issue_date.strftime('%Y-%m-%d'),
                    'issue_type': issue_type,
                    'severity': severity,
                    'product_id': product['product_id'],
                    'supplier_id': supplier['supplier_id'],
                    'impact_duration_days': duration_days,
                    'status': random.choice(['Open', 'In Progress', 'Resolved']),
                    'estimated_cost_impact': random.randint(1000, 50000),
                    'description': f"{issue_type} affecting {product['product_name']} from {supplier['supplier_name']}"
                })
        
        return pd.DataFrame(issues)
    
    def _preview_generated_data(self, datasets: Dict[str, pd.DataFrame]):
        """Preview the generated datasets with insights"""
        st.subheader("Generated Data Preview")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Products", len(datasets['products']))
        with col2:
            st.metric("Customers", len(datasets['customers']))
        with col3:
            st.metric("Sales Records", len(datasets['sales']))
        with col4:
            st.metric("Inventory Items", len(datasets['inventory']))
        
        # Quick insights
        if 'sales' in datasets:
            total_revenue = datasets['sales']['total_amount'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        
        # Data previews with download options
        for name, df in datasets.items():
            with st.expander(f"{name.title()} Data ({len(df)} records)"):
                st.dataframe(df.head())
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"Download {name.title()} CSV",
                    data=csv,
                    file_name=f"mock_{name}_data.csv",
                    mime="text/csv"
                )