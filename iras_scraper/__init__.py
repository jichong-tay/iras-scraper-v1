"""IRAS Web Scraper Package

A high-performance Python package for scraping IRAS website data with advanced 
ReCAPTCHA v2 solving capabilities and optimized batch processing.
"""

from .scraper import IRASScraper
from .excel_handler import ExcelHandler
from .config import Config

__version__ = "1.0.0"
__all__ = ["IRASScraper", "ExcelHandler", "Config"]