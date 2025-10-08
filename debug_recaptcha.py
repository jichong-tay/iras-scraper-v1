#!/usr/bin/env python3
"""Debug script for ReCAPTCHA solver issues."""

import logging
import time
from iras_scraper.scraper import IRASScraper
from iras_scraper.config import Config

def setup_debug_logging():
    """Set up detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/debug_recaptcha.log')
        ]
    )

def debug_recaptcha():
    """Debug ReCAPTCHA detection and solving."""
    setup_debug_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ReCAPTCHA debug session")
    
    # Create config with debug settings
    config = Config()
    config.HEADLESS = False  # Keep browser visible for debugging
    config.RECAPTCHA_AUTO_SOLVE = True
    
    # Create scraper instance
    scraper = IRASScraper(config)
    
    try:
        # Start session
        logger.info("Starting scraper session...")
        scraper.start_session()
        
        # Navigate to IRAS
        logger.info("Navigating to IRAS...")
        if not scraper.navigate_to_iras():
            logger.error("Failed to navigate to IRAS")
            return
        
        # Debug page elements
        debug_info = scraper._debug_page_elements()
        logger.info(f"Page debug info: {debug_info}")
        
        # Save initial screenshot
        scraper._save_debug_screenshot("initial_page")
        
        # Check for ReCAPTCHA
        logger.info("Checking for ReCAPTCHA elements...")
        
        # Look for ReCAPTCHA iframes
        from selenium.webdriver.common.by import By
        recaptcha_frames = scraper.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
        logger.info(f"Found {len(recaptcha_frames)} ReCAPTCHA iframes")
        
        for i, frame in enumerate(recaptcha_frames):
            src = frame.get_attribute('src')
            logger.info(f"ReCAPTCHA iframe {i}: {src}")
        
        # Look for ReCAPTCHA containers
        recaptcha_containers = scraper.driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha")
        logger.info(f"Found {len(recaptcha_containers)} ReCAPTCHA containers")
        
        # Look for response tokens
        response_elements = scraper.driver.find_elements(By.NAME, "g-recaptcha-response")
        logger.info(f"Found {len(response_elements)} g-recaptcha-response elements")
        
        for i, element in enumerate(response_elements):
            value = element.get_attribute("value")
            logger.info(f"Response element {i} value length: {len(value) if value else 0}")
        
        # Try to solve ReCAPTCHA if found
        if recaptcha_frames or recaptcha_containers:
            logger.info("Attempting to solve ReCAPTCHA...")
            logger.info("Note: Image challenges will automatically be switched to audio challenges")
            result = scraper.solve_recaptcha()
            logger.info(f"ReCAPTCHA solving result: {result}")
            
            # Additional check after solving
            if result:
                logger.info("✅ ReCAPTCHA appears to be solved successfully!")
            else:
                logger.warning("❌ ReCAPTCHA solving failed or timed out")
                logger.info("This might be due to:")
                logger.info("- Network issues preventing audio download")
                logger.info("- Audio challenge being too difficult") 
                logger.info("- Missing ffmpeg for audio processing")
        else:
            logger.info("No ReCAPTCHA detected on page")
        
        # Keep browser open for manual inspection
        logger.info("Debug session complete. Browser will stay open for 60 seconds for manual inspection...")
        logger.info("You can use this time to verify ReCAPTCHA status or solve any remaining challenges.")
        time.sleep(60)
        
    except Exception as e:
        logger.error(f"Error in debug session: {str(e)}", exc_info=True)
    
    finally:
        logger.info("Closing scraper session...")
        scraper.close_session()

if __name__ == "__main__":
    debug_recaptcha()