"""
Industry-Specific Data Templates Module
Provides standardized templates and examples for different supply chain industries
"""

import pandas as pd
from typing import Dict, List, Any
import streamlit as st

class DataTemplates:
    """Industry-specific data templates and examples"""
    
    def __init__(self):
        self.industry_templates = {
            'retail': {
                'name': 'Retail & E-commerce',
                'description': 'Consumer goods, online sales, seasonal patterns',
                'use_cases': ['Fashion retail', 'Electronics stores', 'Online marketplaces'],
                'key_metrics': ['Sales velocity', 'Inventory turnover', 'Customer lifetime value'],
                'templates': self._get_retail_templates()
            },
            'manufacturing': {
                'name': 'Manufacturing & Industrial',
                'description': 'Production planning, raw materials, finished goods',
                'use_cases': ['Automotive', 'Electronics manufacturing', 'Industrial equipment'],
                'key_metrics': ['Production efficiency', 'Material utilization', 'Lead times'],
                'templates': self._get_manufacturing_templates()
            },
            'pharmaceutical': {
                'name': 'Pharmaceutical & Healthcare',
                'description': 'Regulated products, expiration tracking, compliance',
                'use_cases': ['Drug manufacturing', 'Medical devices', 'Hospital supply'],
                'key_metrics': ['Batch tracking', 'Expiration management', 'Regulatory compliance'],
                'templates': self._get_pharmaceutical_templates()
            },
            'food_beverage': {
                'name': 'Food & Beverage',
                'description': 'Perishable goods, cold chain, food safety',
                'use_cases': ['Food processing', 'Restaurant chains', 'Beverage distribution'],
                'key_metrics': ['Freshness tracking', 'Cold chain integrity', 'Waste reduction'],
                'templates': self._get_food_beverage_templates()
            }
        }
    
    def template_interface(self) -> Dict[str, Any]:
        """Streamlit interface for template selection and download"""
        st.subheader("📋 Industry-Specific Templates")
        st.write("Download standardized templates tailored for your industry")
        
        # Industry selection
        industry_names = [info['name'] for info in self.industry_templates.values()]
        selected_industry = st.selectbox("Select your industry:", industry_names)
        
        # Find the industry key
        industry_key = None
        for key, info in self.industry_templates.items():
            if info['name'] == selected_industry:
                industry_key = key
                break
        
        if industry_key:
            industry_info = self.industry_templates[industry_key]
            
            # Display industry information
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Description:** {industry_info['description']}")
                st.write("**Common Use Cases:**")
                for use_case in industry_info['use_cases']:
                    st.write(f"• {use_case}")
            
            with col2:
                st.write("**Key Metrics:**")
                for metric in industry_info['key_metrics']:
                    st.write(f"• {metric}")
            
            # Template downloads
            st.write("### 📥 Download Templates")
            templates = industry_info['templates']
            
            # Create download buttons for each template
            cols = st.columns(min(3, len(templates)))
            for i, (template_name, template_data) in enumerate(templates.items()):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    csv_data = template_data['data']
                    st.download_button(
                        label=f"📄 {template_name}",
                        data=csv_data,
                        file_name=f"{industry_key}_{template_name.lower().replace(' ', '_')}_template.csv",
                        mime="text/csv",
                        help=template_data['description']
                    )
            
            # Show template previews
            st.write("### 👀 Template Previews")
            template_tabs = st.tabs(list(templates.keys()))
            
            for i, (template_name, template_data) in enumerate(templates.items()):
                with template_tabs[i]:
                    st.write(template_data['description'])
                    
                    # Parse the CSV data for preview
                    from io import StringIO
                    df = pd.read_csv(StringIO(template_data['data']))
                    st.dataframe(df, height=200)
                    
                    # Show column descriptions
                    if 'columns' in template_data:
                        st.write("**Column Descriptions:**")
                        for col, desc in template_data['columns'].items():
                            st.write(f"• **{col}**: {desc}")
        
        return {'industry': industry_key, 'templates': industry_info['templates'] if industry_key else {}}
    
    def _get_retail_templates(self) -> Dict[str, Dict]:
        """Retail industry templates"""
        return {
            'Sales Data': {
                'description': 'Point-of-sale transaction data with customer and product information',
                'data': '''date,store_id,product_id,customer_id,quantity,unit_price,total_amount,payment_method,sales_channel
2024-01-01,STORE_001,SKU_001,CUST_001,2,29.99,59.98,Credit Card,Online
2024-01-01,STORE_002,SKU_002,CUST_002,1,149.99,149.99,Cash,In-Store
2024-01-02,STORE_001,SKU_003,CUST_003,3,19.99,59.97,Credit Card,Mobile App
2024-01-02,STORE_003,SKU_001,CUST_004,1,29.99,29.99,Debit Card,In-Store''',
                'columns': {
                    'date': 'Transaction date (YYYY-MM-DD)',
                    'store_id': 'Unique store identifier',
                    'product_id': 'Product SKU or identifier',
                    'customer_id': 'Customer identifier (optional)',
                    'quantity': 'Number of units sold',
                    'unit_price': 'Price per unit',
                    'total_amount': 'Total transaction value',
                    'payment_method': 'How customer paid',
                    'sales_channel': 'Where sale occurred'
                }
            },
            'Inventory Data': {
                'description': 'Current inventory levels across stores and warehouses',
                'data': '''product_id,location_id,quantity_on_hand,reserved_quantity,available_quantity,reorder_point,max_capacity
SKU_001,STORE_001,45,5,40,10,100
SKU_001,WAREHOUSE_001,500,50,450,100,1000
SKU_002,STORE_002,12,2,10,5,50
SKU_003,WAREHOUSE_001,200,25,175,50,500''',
                'columns': {
                    'product_id': 'Product SKU or identifier',
                    'location_id': 'Store or warehouse identifier',
                    'quantity_on_hand': 'Total physical inventory',
                    'reserved_quantity': 'Inventory reserved for orders',
                    'available_quantity': 'Inventory available for sale',
                    'reorder_point': 'Minimum level before reordering',
                    'max_capacity': 'Maximum storage capacity'
                }
            },
            'Product Catalog': {
                'description': 'Master product information with categories and attributes',
                'data': '''product_id,product_name,category,brand,unit_cost,unit_price,supplier,season,size,color
SKU_001,Wireless Headphones,Electronics,TechBrand,15.00,29.99,SUPPLIER_001,All-Season,One Size,Black
SKU_002,Running Shoes,Footwear,SportsBrand,45.00,149.99,SUPPLIER_002,Spring/Summer,Size 10,Blue
SKU_003,Cotton T-Shirt,Clothing,FashionBrand,8.00,19.99,SUPPLIER_003,Summer,Medium,White''',
                'columns': {
                    'product_id': 'Unique product identifier',
                    'product_name': 'Display name of product',
                    'category': 'Product category for grouping',
                    'brand': 'Product brand or manufacturer',
                    'unit_cost': 'Cost to acquire/produce',
                    'unit_price': 'Selling price to customers',
                    'supplier': 'Primary supplier identifier',
                    'season': 'Seasonal relevance',
                    'size': 'Size specification',
                    'color': 'Color specification'
                }
            }
        }
    
    def _get_manufacturing_templates(self) -> Dict[str, Dict]:
        """Manufacturing industry templates"""
        return {
            'Production Orders': {
                'description': 'Manufacturing orders with materials and scheduling',
                'data': '''order_id,product_id,quantity_planned,quantity_produced,start_date,target_completion,actual_completion,status,work_center
PO_001,FINISHED_001,100,95,2024-01-01,2024-01-05,2024-01-06,Completed,WC_Assembly
PO_002,FINISHED_002,200,200,2024-01-03,2024-01-08,2024-01-08,Completed,WC_Machining
PO_003,FINISHED_001,150,,2024-01-10,2024-01-15,,In Progress,WC_Assembly''',
                'columns': {
                    'order_id': 'Unique production order identifier',
                    'product_id': 'Finished good being produced',
                    'quantity_planned': 'Target production quantity',
                    'quantity_produced': 'Actual quantity produced',
                    'start_date': 'Production start date',
                    'target_completion': 'Planned completion date',
                    'actual_completion': 'Actual completion date',
                    'status': 'Current order status',
                    'work_center': 'Manufacturing work center'
                }
            },
            'Bill of Materials': {
                'description': 'Component requirements for finished products',
                'data': '''finished_product,component_id,component_name,quantity_required,unit_of_measure,supplier,lead_time_days
FINISHED_001,COMP_001,Steel Bracket,2,pieces,SUPPLIER_A,14
FINISHED_001,COMP_002,Motor Assembly,1,each,SUPPLIER_B,21
FINISHED_002,COMP_001,Steel Bracket,1,pieces,SUPPLIER_A,14
FINISHED_002,COMP_003,Control Board,1,each,SUPPLIER_C,28''',
                'columns': {
                    'finished_product': 'Final product identifier',
                    'component_id': 'Component part identifier',
                    'component_name': 'Component description',
                    'quantity_required': 'Quantity needed per finished unit',
                    'unit_of_measure': 'How component is measured',
                    'supplier': 'Component supplier',
                    'lead_time_days': 'Supplier lead time in days'
                }
            },
            'Material Inventory': {
                'description': 'Raw materials and component inventory levels',
                'data': '''component_id,location_id,quantity_on_hand,allocated_quantity,available_quantity,safety_stock,last_receipt_date
COMP_001,WAREHOUSE_A,500,100,400,50,2024-01-15
COMP_002,WAREHOUSE_A,25,5,20,10,2024-01-10
COMP_003,WAREHOUSE_B,80,20,60,15,2024-01-12''',
                'columns': {
                    'component_id': 'Component identifier',
                    'location_id': 'Storage location',
                    'quantity_on_hand': 'Total physical inventory',
                    'allocated_quantity': 'Reserved for production orders',
                    'available_quantity': 'Available for new orders',
                    'safety_stock': 'Minimum stock level',
                    'last_receipt_date': 'Most recent receipt date'
                }
            }
        }
    
    def _get_pharmaceutical_templates(self) -> Dict[str, Dict]:
        """Pharmaceutical industry templates"""
        return {
            'Batch Records': {
                'description': 'Manufacturing batch tracking with expiration and compliance',
                'data': '''batch_id,product_id,manufacture_date,expiration_date,quantity_produced,status,gmp_compliant,temperature_controlled
BATCH_001,DRUG_001,2024-01-01,2025-01-01,1000,Released,Yes,Yes
BATCH_002,DRUG_002,2024-01-05,2024-07-05,500,Testing,Yes,No
BATCH_003,DRUG_001,2024-01-10,2025-01-10,1200,Quarantine,Yes,Yes''',
                'columns': {
                    'batch_id': 'Unique batch identifier',
                    'product_id': 'Drug or device identifier',
                    'manufacture_date': 'Production date',
                    'expiration_date': 'Product expiration date',
                    'quantity_produced': 'Units in batch',
                    'status': 'Batch status (Released/Testing/Quarantine)',
                    'gmp_compliant': 'Good Manufacturing Practice compliance',
                    'temperature_controlled': 'Requires cold chain storage'
                }
            },
            'Distribution Records': {
                'description': 'Product distribution with chain of custody tracking',
                'data': '''shipment_id,batch_id,destination,ship_date,arrival_date,temperature_log,chain_of_custody,regulatory_docs
SHIP_001,BATCH_001,PHARMACY_001,2024-01-15,2024-01-16,2-8C_Maintained,Verified,Complete
SHIP_002,BATCH_002,HOSPITAL_001,2024-01-18,2024-01-19,Room_Temperature,Verified,Complete
SHIP_003,BATCH_001,DISTRIBUTOR_001,2024-01-20,2024-01-22,2-8C_Maintained,Verified,Pending''',
                'columns': {
                    'shipment_id': 'Unique shipment identifier',
                    'batch_id': 'Product batch being shipped',
                    'destination': 'Receiving facility',
                    'ship_date': 'Shipment departure date',
                    'arrival_date': 'Delivery date',
                    'temperature_log': 'Temperature requirements/monitoring',
                    'chain_of_custody': 'Custody verification status',
                    'regulatory_docs': 'Required documentation status'
                }
            }
        }
    
    def _get_food_beverage_templates(self) -> Dict[str, Dict]:
        """Food & beverage industry templates"""
        return {
            'Perishable Inventory': {
                'description': 'Inventory tracking with expiration and freshness management',
                'data': '''product_id,location_id,batch_number,production_date,best_by_date,quantity,storage_temp,freshness_score
FOOD_001,COLD_STORAGE_1,B20240101,2024-01-01,2024-01-15,500,2C,95
FOOD_002,DRY_STORAGE_1,B20240102,2024-01-02,2024-07-02,1000,Room,100
BEVERAGE_001,COLD_STORAGE_2,B20240103,2024-01-03,2024-04-03,200,4C,98''',
                'columns': {
                    'product_id': 'Food/beverage product identifier',
                    'location_id': 'Storage facility identifier',
                    'batch_number': 'Production batch number',
                    'production_date': 'Manufacturing/processing date',
                    'best_by_date': 'Product expiration/best by date',
                    'quantity': 'Units in inventory',
                    'storage_temp': 'Required storage temperature',
                    'freshness_score': 'Quality score (0-100)'
                }
            },
            'Cold Chain Monitoring': {
                'description': 'Temperature monitoring for cold chain products',
                'data': '''shipment_id,product_id,origin,destination,departure_temp,arrival_temp,duration_hours,temperature_breach
COLD_001,FOOD_001,FACILITY_A,STORE_001,2.1,2.3,4,No
COLD_002,BEVERAGE_001,FACILITY_B,RESTAURANT_001,3.8,4.2,2,No
COLD_003,FOOD_002,FACILITY_A,STORE_002,2.5,8.1,6,Yes''',
                'columns': {
                    'shipment_id': 'Cold chain shipment identifier',
                    'product_id': 'Product being transported',
                    'origin': 'Shipping origin facility',
                    'destination': 'Delivery destination',
                    'departure_temp': 'Temperature at departure (°C)',
                    'arrival_temp': 'Temperature at arrival (°C)',
                    'duration_hours': 'Transport duration in hours',
                    'temperature_breach': 'Whether temperature limits exceeded'
                }
            }
        }