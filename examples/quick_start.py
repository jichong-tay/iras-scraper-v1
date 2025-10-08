"""
IRAS Scraper - Quick Start Examples

This file demonstrates the main ways to use the IRAS scraper package.
"""

from iras_scraper import IRASScraper, ExcelHandler, Config

def example_1_single_uen():
    """Example 1: Process a single UEN programmatically."""
    print("🔍 Example 1: Single UEN Processing")
    
    # Initialize with custom configuration
    config = Config()
    config.HEADLESS = False  # Show browser for demo
    scraper = IRASScraper(config)
    
    try:
        # Start session (handles ReCAPTCHA)
        scraper.start_session()
        
        # Search single UEN
        uen = "200012345A"
        result = scraper.search_uen(uen)
        
        # Display results
        print(f"UEN: {uen}")
        print(f"Success: {result['success']}")
        if result['success']:
            data = result.get('data', {})
            print(f"Company: {data.get('company_name', 'N/A')}")
            print(f"GST Status: {data.get('gst_registration_status', 'N/A')}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    finally:
        scraper.close_session()
    
    print("✅ Example 1 completed\n")


def example_2_batch_processing():
    """Example 2: Process multiple UENs efficiently with session reuse."""
    print("📊 Example 2: Batch Processing")
    
    config = Config()
    config.REQUEST_DELAY = 0.3  # Faster processing
    scraper = IRASScraper(config)
    
    # List of UENs to process
    uens = [
        "200012345A",
        "199812345B", 
        "202112345C"
    ]
    
    try:
        # Process all UENs with session reuse (efficient!)
        print(f"Processing {len(uens)} UENs...")
        results = scraper.scrape_multiple_uens(uens)
        
        # Display summary
        successful = sum(1 for r in results if r['success'])
        print(f"Results: {successful}/{len(results)} successful")
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['uen']}")
            
    finally:
        # Session is automatically closed by scrape_multiple_uens
        pass
    
    print("✅ Example 2 completed\n")


def example_3_excel_integration():
    """Example 3: Read UENs from Excel, process, and save results."""
    print("📁 Example 3: Excel Integration")
    
    # File paths
    input_file = "data/input_uens.xlsx"
    output_file = "data/example_results.xlsx"
    
    try:
        # Initialize Excel handler
        excel_handler = ExcelHandler(input_file, output_file)
        
        # Create sample input if it doesn't exist
        if not excel_handler.input_file.exists():
            print("Creating sample input file...")
            excel_handler.create_sample_input()
        
        # Read UENs from Excel
        uens = excel_handler.read_uens("UEN")
        print(f"Read {len(uens)} UENs from Excel file")
        
        # Process UENs
        config = Config()
        config.HEADLESS = True  # Background processing
        scraper = IRASScraper(config)
        
        results = scraper.scrape_multiple_uens(uens)
        
        # Save enhanced results to Excel
        excel_handler.write_results(results)
        
        print(f"Results saved to: {output_file}")
        print("✅ Example 3 completed\n")
        
    except Exception as e:
        print(f"Error in Excel processing: {e}")


def example_4_custom_business_logic():
    """Example 4: Integration with custom business logic."""
    print("🏢 Example 4: Business Logic Integration")
    
    class CompanyValidator:
        def __init__(self):
            config = Config()
            config.HEADLESS = True
            self.scraper = IRASScraper(config)
        
        def is_gst_registered(self, uen):
            """Check if a company is GST registered."""
            try:
                self.scraper.start_session()
                result = self.scraper.search_uen(uen)
                
                if result['success']:
                    gst_status = result.get('data', {}).get('gst_registration_status', '')
                    return 'registered' in gst_status.lower()
                return False
            finally:
                self.scraper.close_session()
        
        def get_company_info(self, uen):
            """Get detailed company information."""
            try:
                self.scraper.start_session()
                result = self.scraper.search_uen(uen)
                
                if result['success']:
                    data = result.get('data', {})
                    return {
                        'uen': uen,
                        'name': data.get('company_name', 'N/A'),
                        'gst_registered': 'registered' in data.get('gst_registration_status', '').lower(),
                        'business_status': data.get('business_status', 'N/A'),
                        'entity_type': data.get('entity_type', 'N/A')
                    }
                return {'uen': uen, 'error': result.get('error', 'Unknown error')}
            finally:
                self.scraper.close_session()
    
    # Use the custom validator
    validator = CompanyValidator()
    
    test_uen = "200012345A"
    
    # Check GST registration
    is_registered = validator.is_gst_registered(test_uen)
    print(f"UEN {test_uen} GST registered: {is_registered}")
    
    # Get full company info
    company_info = validator.get_company_info(test_uen)
    print(f"Company info: {company_info}")
    
    print("✅ Example 4 completed\n")


if __name__ == "__main__":
    print("🚀 IRAS Scraper - Quick Start Examples")
    print("=" * 50)
    print()
    
    # Run examples
    try:
        example_1_single_uen()
        example_2_batch_processing() 
        example_3_excel_integration()
        example_4_custom_business_logic()
        
        print("🎉 All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure Chrome browser is installed and the package is properly configured.")