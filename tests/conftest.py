"""Pytest configuration and fixtures."""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def clean_environment():
    """Fixture to provide clean environment for config tests."""
    # Store original environment variables
    original_env = {}
    test_vars = ['IMPLICIT_WAIT', 'REQUEST_DELAY', 'HEADLESS', 'PAGE_LOAD_TIMEOUT']
    
    for var in test_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore original environment variables
    for var, value in original_env.items():
        os.environ[var] = value


@pytest.fixture
def temp_excel_file():
    """Fixture to create temporary Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        temp_path = Path(tmp_file.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_uen_data():
    """Fixture providing sample UEN test data."""
    return [
        {
            'uen': '200012345A',
            'expected_valid': True,
            'description': 'Sample valid UEN format'
        },
        {
            'uen': '199812345B',
            'expected_valid': True, 
            'description': 'Another sample UEN format'
        },
        {
            'uen': 'INVALID123',
            'expected_valid': False,
            'description': 'Invalid UEN format'
        }
    ]


@pytest.fixture
def sample_scraper_results():
    """Fixture providing sample scraper result data."""
    return [
        {
            'uen': '200012345A',
            'success': True,
            'data': {
                'gst_registration_status': 'GST registered',
                'company_name': 'Test Company A Pte Ltd',
                'business_status': 'Live',
                'entity_type': 'Company',
                'registration_date': '2020-01-01'
            },
            'timestamp': '2025-10-07 10:30:15',
            'extraction_status': 'success',
            'page_title': 'IRAS | myTax Portal Search GST Registered Business',
            'page_url': 'https://mytax.iras.gov.sg/ESVWeb/default.aspx'
        },
        {
            'uen': '199812345B',
            'success': False,
            'error': 'UEN not found in IRAS database',
            'timestamp': '2025-10-07 10:30:45',
            'extraction_status': 'failed',
            'page_title': 'IRAS | myTax Portal Search GST Registered Business',
            'page_url': 'https://mytax.iras.gov.sg/ESVWeb/default.aspx'
        }
    ]