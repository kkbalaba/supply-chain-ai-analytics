"""
Data Management Package

Handles file uploads, mock data generation, and data validation
for the supply chain analytics platform.
"""

from .file_upload import DataUploadManager
from .mock_data_generator import MockDataGenerator
from .data_templates import DataTemplates

__all__ = ['DataUploadManager', 'MockDataGenerator', 'DataTemplates']