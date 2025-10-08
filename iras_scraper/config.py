"""Configuration settings for the IRAS scraper."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for IRAS scraper settings."""
    
    # IRAS Website Settings
    IRAS_URL = "https://mytax.iras.gov.sg/ESVWeb/default.aspx?target=MGSTListingSearch"
    
    # Browser Settings
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    WINDOW_SIZE = os.getenv("WINDOW_SIZE", "1920,1080")
    
    # User Agents (Updated to current versions)
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    
    # Selenium Settings (CAPTCHA-Friendly Timeouts)
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "8"))       # Slightly longer for CAPTCHA elements
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "20"))  # More time for CAPTCHA loading
    ELEMENT_WAIT_TIMEOUT = int(os.getenv("ELEMENT_WAIT_TIMEOUT", "10"))  # CAPTCHA elements need time
    
    # ReCAPTCHA Settings (Optimized for Success Rate)
    RECAPTCHA_AUDIO_SOLVING = True
    RECAPTCHA_MAX_RETRIES = int(os.getenv("RECAPTCHA_MAX_RETRIES", "3"))  # Increased for better success
    RECAPTCHA_AUTO_SOLVE = os.getenv("RECAPTCHA_AUTO_SOLVE", "true").lower() == "true"
    
    # Auto-detect ffmpeg availability for audio CAPTCHA solving
    @staticmethod
    def is_ffmpeg_available():
        """Check if ffmpeg is available on the system."""
        import shutil
        return shutil.which("ffmpeg") is not None
    
    # Rate Limiting (Optimized)
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))   # Reduced from 2.0
    RANDOM_DELAY_RANGE = (0.2, 0.8)  # Much faster delays
    NAVIGATION_DELAY = float(os.getenv("NAVIGATION_DELAY", "1.0"))  # Page navigation delays
    
    # File Paths
    INPUT_EXCEL_PATH = os.getenv("INPUT_EXCEL_PATH", "data/input_uens.xlsx")
    OUTPUT_EXCEL_PATH = os.getenv("OUTPUT_EXCEL_PATH", "data/output_results.xlsx")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/scraper.log")
    
    # Chrome Driver Settings (Ultra-Lightweight & CAPTCHA-Friendly)
    CHROME_OPTIONS = [
        "--no-sandbox",  # Required for Docker/Linux environments
        "--disable-dev-shm-usage",  # Prevents crashes in limited memory
        "--disable-blink-features=AutomationControlled",  # Essential webdriver hiding
        "--no-first-run",  # Skip first-run setup
        "--disable-default-apps"  # Minimal system interaction
    ]
