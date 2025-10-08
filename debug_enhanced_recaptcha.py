#!/usr/bin/env python3
"""
Enhanced ReCAPTCHA debug script with maximum anti-detection measures.
This script tests the improved stealth techniques against Google's bot detection.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from iras_scraper.scraper import IRASScraper
from iras_scraper.config import Config

def setup_enhanced_logging():
    """Setup enhanced logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/enhanced_debug.log')
        ]
    )
    
    # Reduce selenium logging noise
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def test_enhanced_recaptcha_solving():
    """Test the enhanced ReCAPTCHA solving with maximum anti-detection."""
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("🔒 ENHANCED RECAPTCHA ANTI-DETECTION TEST")
    logger.info("=" * 80)
    logger.info("This test uses advanced stealth techniques to avoid Google's bot detection")
    logger.info("Features: Session management, realistic delays, enhanced fingerprinting")
    logger.info("")
    
    scraper = None
    
    try:
        # Initialize scraper with enhanced configuration
        logger.info("🚀 Initializing scraper with enhanced anti-detection...")
        config = Config()
        
        # Enable more aggressive stealth settings
        config.HEADLESS = False  # Keep visible for debugging
        config.RECAPTCHA_AUTO_SOLVE = True
        config.RECAPTCHA_MAX_RETRIES = 3
        
        scraper = IRASScraper(config)
        
        logger.info("✅ Scraper initialized successfully")
        logger.info("🌐 Navigating to IRAS website with stealth measures...")
        
        # Navigate to the target page
        target_url = "https://www.iras.gov.sg/taxes/corporate-income-tax/income-deduction-for-expenses/business-expenses/gst-registered-suppliers"
        
        scraper.driver.get(target_url)
        logger.info(f"📄 Successfully loaded: {target_url}")
        
        # Wait for page to fully load with random timing
        initial_wait = 5 + (time.time() % 3)  # 5-8 seconds
        logger.info(f"⏳ Waiting {initial_wait:.1f}s for page to fully load...")
        time.sleep(initial_wait)
        
        # Test input field interaction with stealth
        logger.info("🔍 Testing input field interaction with anti-detection...")
        
        try:
            input_field = scraper._find_input_field()
            if input_field:
                logger.info("✅ Input field found successfully")
                
                # Simulate realistic typing with delays
                test_uen = "200012345A"
                logger.info(f"⌨️  Entering test UEN: {test_uen} with human-like typing...")
                
                input_field.clear()
                
                # Type with realistic delays between characters
                for char in test_uen:
                    input_field.send_keys(char)
                    time.sleep(0.1 + (time.time() % 0.1))  # 0.1-0.2s per char
                
                logger.info("✅ UEN entered with realistic timing")
                
            else:
                logger.error("❌ Could not find input field")
                
        except Exception as e:
            logger.error(f"❌ Input field test failed: {e}")
        
        # Now test ReCAPTCHA detection and solving
        logger.info("🔐 Testing enhanced ReCAPTCHA detection and solving...")
        
        try:
            # First, try to trigger ReCAPTCHA by clicking search
            search_button = scraper._find_search_button()
            if search_button:
                logger.info("🔍 Found search button, attempting to trigger ReCAPTCHA...")
                
                # Use enhanced clicking method
                scraper._human_like_click(search_button)
                
                # Wait for ReCAPTCHA to appear
                recaptcha_wait = 3 + (time.time() % 2)  # 3-5 seconds
                logger.info(f"⏳ Waiting {recaptcha_wait:.1f}s for ReCAPTCHA to appear...")
                time.sleep(recaptcha_wait)
                
                # Attempt enhanced ReCAPTCHA solving
                logger.info("🤖 Attempting enhanced ReCAPTCHA solving...")
                recaptcha_result = scraper.solve_recaptcha()
                
                if recaptcha_result:
                    logger.info("🎉 ReCAPTCHA solved successfully with enhanced methods!")
                else:
                    logger.warning("⚠️  ReCAPTCHA solving unsuccessful - checking for detection messages...")
                    
                    # Check for Google's automation detection message
                    page_source = scraper.driver.page_source.lower()
                    if "automated queries" in page_source:
                        logger.error("🚨 DETECTED: Google identified automated behavior!")
                        logger.error("📋 Message: 'Your computer or network may be sending automated queries'")
                        logger.info("💡 This indicates our anti-detection measures need further enhancement")
                    else:
                        logger.info("✅ No automation detection message found")
                    
            else:
                logger.error("❌ Could not find search button")
                
        except Exception as e:
            logger.error(f"❌ ReCAPTCHA test failed: {e}")
        
        # Extended debugging session
        logger.info("=" * 80)
        logger.info("🔍 DEBUGGING SESSION - Browser remains open for manual inspection")
        logger.info("=" * 80)
        logger.info("You can now:")
        logger.info("1. Check if ReCAPTCHA is visible and solved")
        logger.info("2. Manually complete any remaining challenges")
        logger.info("3. Inspect the page for detection warnings")
        logger.info("4. Test different interactions")
        logger.info("")
        logger.info("Press Ctrl+C to end the debugging session...")
        
        try:
            # Keep browser open for extended debugging
            time.sleep(120)  # 2 minutes for inspection
        except KeyboardInterrupt:
            logger.info("🛑 Debugging session interrupted by user")
        
        logger.info("🎯 Enhanced anti-detection test completed")
        
    except Exception as e:
        logger.error(f"❌ Enhanced test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
    finally:
        if scraper:
            logger.info("🧹 Cleaning up scraper session...")
            scraper.close()

def main():
    """Main function."""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Setup logging
    setup_enhanced_logging()
    
    # Run the enhanced test
    test_enhanced_recaptcha_solving()

if __name__ == "__main__":
    main()