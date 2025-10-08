"""Main application entry point for IRAS scraper."""

import argparse
import sys
import logging
from pathlib import Path

from iras_scraper import IRASScraper, ExcelHandler, Config


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/main.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='IRAS Web Scraper with ReCAPTCHA v2 Solving')
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='data/input_uens.xlsx',
        help='Path to input Excel file containing UENs (default: data/input_uens.xlsx)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/output_results.xlsx',
        help='Path to output Excel file for results (default: data/output_results.xlsx)'
    )
    
    parser.add_argument(
        '--column', '-c',
        type=str,
        default='UEN',
        help='Name of the column containing UENs (default: UEN)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (not recommended for ReCAPTCHA solving)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create a sample input Excel file and exit'
    )
    
    parser.add_argument(
        '--validate-input',
        action='store_true',
        help='Validate input file format and exit'
    )
    
    parser.add_argument(
        '--debug-single-uen',
        type=str,
        help='Debug mode: process only one UEN and show detailed page information'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level)
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    try:
        # Initialize Excel handler
        excel_handler = ExcelHandler(args.input, args.output)
        
        # Handle special operations
        if args.create_sample:
            logger.info("Creating sample input file...")
            excel_handler.create_sample_input()
            logger.info(f"Sample input file created: {args.input}")
            return 0
        
        if args.validate_input:
            logger.info("Validating input file...")
            if excel_handler.validate_input_file([args.column]):
                logger.info("Input file validation successful")
                return 0
            else:
                logger.error("Input file validation failed")
                return 1
        
        # Validate input file exists
        if not excel_handler.validate_input_file([args.column]):
            logger.error("Input file validation failed. Use --create-sample to create a sample file.")
            return 1
        
        # Handle debug mode for single UEN
        if args.debug_single_uen:
            logger.info(f"Debug mode: Processing single UEN: {args.debug_single_uen}")
            uens = [args.debug_single_uen]
        else:
            # Read UENs from Excel file
            logger.info(f"Reading UENs from: {args.input}")
            uens = excel_handler.read_uens(args.column)
            
            if not uens:
                logger.error("No UENs found in input file")
                return 1
            
            logger.info(f"Found {len(uens)} UENs to process")
        
        # Configure scraper
        config = Config()
        if args.headless:
            config.HEADLESS = True
            logger.warning("Running in headless mode - ReCAPTCHA solving may be more difficult")
        
        # Initialize and run scraper
        logger.info("Starting IRAS scraping session...")
        scraper = IRASScraper(config)
        
        # Process all UENs
        results = scraper.scrape_multiple_uens(uens)
        
        # Write results to Excel
        logger.info(f"Writing results to: {args.output}")
        excel_handler.write_results(results)
        
        # Summary
        successful_results = sum(1 for r in results if r['success'])
        failed_results = len(results) - successful_results
        
        logger.info(f"Scraping completed!")
        logger.info(f"  Total UENs processed: {len(results)}")
        logger.info(f"  Successful: {successful_results}")
        logger.info(f"  Failed: {failed_results}")
        logger.info(f"  Results saved to: {args.output}")
        
        return 0 if failed_results == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())