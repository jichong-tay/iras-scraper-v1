"""Main IRAS web scraper with ReCAPTCHA v2 solving capabilities."""

import time
import random
import logging
from typing import Dict, Any, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Optional import for ReCAPTCHA solver
try:
    from selenium_recaptcha_solver import RecaptchaSolver
    RECAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    RECAPTCHA_SOLVER_AVAILABLE = False
    print("Warning: selenium-recaptcha-solver not available. Install with: uv sync --extra recaptcha")

from .config import Config


class IRASScraper:
    """Main scraper class for IRAS website with ReCAPTCHA v2 solving."""
    
    def __init__(self, config: Config = None):
        """Initialize the IRAS scraper.
        
        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()
        self.driver = None
        self.wait = None
        self.solver = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        
        if not logger.handlers:
            # Create logs directory if it doesn't exist
            import os
            os.makedirs("logs", exist_ok=True)
            
            # File handler
            file_handler = logging.FileHandler(self.config.LOG_FILE)
            file_handler.setLevel(getattr(logging, self.config.LOG_LEVEL))
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        return logger
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with CAPTCHA-friendly anti-detection measures."""
        try:
            chrome_options = Options()
            
            # Add basic Chrome options from config (no duplicates)
            for option in self.config.CHROME_OPTIONS:
                chrome_options.add_argument(option)
            
            # Essential anti-detection (minimal set)
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-component-update")
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--disable-background-networking")
            
            # Set realistic window size with slight randomization
            if not self.config.HEADLESS:
                base_width, base_height = self.config.WINDOW_SIZE.split(',')
                # Add random variation to window size
                width = int(base_width) + random.randint(-50, 50)
                height = int(base_height) + random.randint(-30, 30)
                chrome_options.add_argument(f"--window-size={width},{height}")
            else:
                chrome_options.add_argument("--headless")
            
            # Set random user agent
            user_agent = random.choice(self.config.USER_AGENTS)
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Critical automation detection bypass (enhanced)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # CAPTCHA-friendly preferences (keep images and CSS!)
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 1,  # IMPORTANT: Keep images for CAPTCHA
                    "javascript": 1,  # Keep JavaScript for CAPTCHA
                },
                "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize driver with manual or automatic ChromeDriver
            if self.config.CHROMEDRIVER_PATH:
                # Use manually specified ChromeDriver path
                self.logger.info(f"Using manual ChromeDriver: {self.config.CHROMEDRIVER_PATH}")
                service = webdriver.chrome.service.Service(self.config.CHROMEDRIVER_PATH)
            elif self.config.WDM_LOCAL:
                # Use system-installed ChromeDriver (no automatic download)
                self.logger.info("Using system-installed ChromeDriver (WDM_LOCAL=true)")
                service = webdriver.chrome.service.Service()
            else:
                # Automatic ChromeDriver download (default behavior)
                self.logger.info("Automatically downloading ChromeDriver")
                service = webdriver.chrome.service.Service(ChromeDriverManager().install())
            
            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            
            # Apply lightweight stealth scripts
            self._apply_stealth_scripts(driver)
            
            # Set realistic timeouts with slight randomization
            implicit_wait = self.config.IMPLICIT_WAIT + random.uniform(-0.5, 0.5)
            page_load_timeout = self.config.PAGE_LOAD_TIMEOUT + random.uniform(-1, 1)
            
            driver.implicitly_wait(max(2, implicit_wait))
            driver.set_page_load_timeout(max(10, page_load_timeout))
            
            # Set realistic viewport
            self._set_realistic_viewport(driver)
            
            self.logger.info("Chrome WebDriver initialized with CAPTCHA-friendly settings")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def _apply_stealth_scripts(self, driver):
        """Apply lightweight CAPTCHA-friendly anti-detection JavaScript."""
        stealth_js = """
        // Remove primary webdriver detection
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        
        // Clean Chrome automation variables (most critical ones only)
        ['cdc_adoQpoasnfa76pfcZLmcfl_Array', 'cdc_adoQpoasnfa76pfcZLmcfl_Promise', 
         'cdc_adoQpoasnfa76pfcZLmcfl_Symbol'].forEach(prop => delete window[prop]);
        
        // Fix chrome.runtime detection (key for Google services)
        if (window.chrome) {
            window.chrome.runtime = window.chrome.runtime || {};
            Object.defineProperty(window.chrome.runtime, 'onConnect', {value: undefined});
        }
        """
        
        try:
            # Use CDP for most effective injection
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth_js})
            self.logger.debug("Applied lightweight stealth scripts via CDP")
        except Exception as e:
            try:
                driver.execute_script(stealth_js)
                self.logger.debug("Applied stealth scripts via execute_script")
            except Exception as e2:
                self.logger.warning(f"Failed to apply stealth scripts: {e2}")
    
    def _set_realistic_viewport(self, driver):
        """Set realistic viewport and screen properties."""
        viewport_js = """
        // Set realistic viewport
        const viewport = {
            width: window.screen.width,
            height: window.screen.height,
            deviceScaleFactor: window.devicePixelRatio || 1
        };
        
        // Add slight randomization to timing functions
        const originalSetTimeout = window.setTimeout;
        window.setTimeout = function(fn, delay) {
            const randomDelay = delay + (Math.random() * 10 - 5);
            return originalSetTimeout(fn, Math.max(0, randomDelay));
        };
        
        // Mock realistic mouse movements
        let mouseX = Math.floor(Math.random() * window.innerWidth);
        let mouseY = Math.floor(Math.random() * window.innerHeight);
        
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        """
        
        try:
            driver.execute_script(viewport_js)
            self.logger.debug("Set realistic viewport properties")
        except Exception as e:
            self.logger.warning(f"Failed to set viewport properties: {e}")
    
    def _simulate_human_page_interaction(self):
        """Simulate human-like page interactions before ReCAPTCHA."""
        try:
            # Random small mouse movements and clicks
            actions = ActionChains(self.driver)
            
            # Simulate reading the page by scrolling slightly
            self.driver.execute_script("window.scrollBy(0, Math.random() * 100);")
            time.sleep(random.uniform(0.3, 0.8))
            
            # Random cursor movement to simulate human behavior
            body = self.driver.find_element(By.TAG_NAME, "body")
            actions.move_to_element_with_offset(body, 
                random.randint(100, 400), random.randint(100, 300)).perform()
            
            time.sleep(random.uniform(0.2, 0.5))
            
        except Exception as e:
            self.logger.debug(f"Could not simulate human interaction: {str(e)}")

    def _human_like_click(self, element):
        """Perform a human-like click with realistic timing and movement."""
        try:
            # Move to element with slight randomization
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(element, 
                random.randint(-3, 3), random.randint(-3, 3))
            
            # Add small pause before click (human hesitation)
            time.sleep(random.uniform(0.1, 0.3))
            
            # Perform click
            actions.click().perform()
            
            # Brief pause after click
            time.sleep(random.uniform(0.2, 0.5))
            
        except Exception as e:
            self.logger.debug(f"Human-like click failed, using regular click: {str(e)}")
            # Fallback to regular click
            element.click()
    
    def _manage_session_state(self):
        """Manage browser session to appear more human-like."""
        try:
            # Clear some cookies randomly to simulate human behavior
            if random.random() < 0.3:  # 30% chance
                self.driver.delete_all_cookies()
                self.logger.debug("Cleared cookies for session reset")
            
            # Simulate browsing other pages occasionally
            if random.random() < 0.2:  # 20% chance
                self.logger.debug("Simulating browsing behavior")
                # Visit IRAS homepage briefly
                self.driver.get("https://www.iras.gov.sg/")
                time.sleep(random.uniform(2, 5))
                
                # Then navigate back to target page
                self.driver.get("https://www.iras.gov.sg/taxes/corporate-income-tax/income-deduction-for-expenses/business-expenses/gst-registered-suppliers")
                time.sleep(random.uniform(3, 6))
            
            # Add random scrolling to simulate reading
            scroll_pause = random.uniform(0.5, 2.0)
            scroll_amount = random.randint(100, 500)
            
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount}); ")
            time.sleep(scroll_pause)
            
            self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount // 2}); ")
            time.sleep(scroll_pause)
            
        except Exception as e:
            self.logger.debug(f"Session management failed: {e}")
    
    def start_session(self):
        """Start a new scraping session."""
        try:
            self.driver = self._setup_driver()
            self.wait = WebDriverWait(self.driver, 10)
            
            # Initialize ReCAPTCHA solver (if available)
            if RECAPTCHA_SOLVER_AVAILABLE:
                self.solver = RecaptchaSolver(driver=self.driver)
                
                # Check ffmpeg availability for audio CAPTCHA solving
                if not self.config.is_ffmpeg_available():
                    self.logger.warning("ffmpeg not found - audio CAPTCHA solving disabled. Manual clicking will be used.")
                else:
                    self.logger.info("ffmpeg found - full audio CAPTCHA solving enabled")
            else:
                self.solver = None
                self.logger.warning("ReCAPTCHA solver not available - manual solving may be required")
            
            self.logger.info("Scraping session started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start session: {str(e)}")
            self.close_session()
            raise
    
    def close_session(self):
        """Close the scraping session and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver session closed")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
                self.wait = None
    
    def navigate_to_iras(self) -> bool:
        """Navigate to IRAS website.
        
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            self.logger.info(f"Navigating to IRAS website: {self.config.IRAS_URL}")
            self.driver.get(self.config.IRAS_URL)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check if we're on a results page instead of the search page
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            if "MGSTListingResult" in current_url or "Search Result" in page_title:
                self.logger.info("Currently on results page, attempting to go back to search")
                try:
                    # Try to find and click "Search Again" button
                    search_again_selectors = [
                        (By.ID, "btnSearchAgain"),
                        (By.CSS_SELECTOR, "input[value*='SEARCH AGAIN']"),
                        (By.CSS_SELECTOR, "input[name*='SearchAgain']"),
                        (By.XPATH, "//input[@value='SEARCH AGAIN' or contains(@value, 'Search Again')]")
                    ]
                    
                    for selector_type, selector_value in search_again_selectors:
                        try:
                            search_again_btn = self.wait.until(
                                EC.element_to_be_clickable((selector_type, selector_value))
                            )
                            search_again_btn.click()
                            self.logger.info("Clicked 'Search Again' button")
                            
                            # Wait for navigation back to search page
                            WebDriverWait(self.driver, 10).until(
                                lambda driver: "MGSTSearch" in driver.current_url or "Search" in driver.title
                            )
                            self.logger.info("Successfully navigated back to search page")
                            break
                        except TimeoutException:
                            continue
                        except Exception as e:
                            self.logger.debug(f"Search Again selector failed: {e}")
                            continue
                except Exception as e:
                    self.logger.warning(f"Could not navigate back to search page: {e}")
            
            self.logger.info("Successfully navigated to IRAS website")
            return True
            
        except TimeoutException:
            self.logger.error("Timeout while loading IRAS website")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to IRAS website: {str(e)}")
            return False
    
    def solve_recaptcha(self) -> bool:
        """Solve ReCAPTCHA v2 with advanced anti-detection measures.
        
        Returns:
            True if ReCAPTCHA solved successfully, False otherwise
        """
        try:
            self.logger.info("Attempting to solve ReCAPTCHA with anti-detection")
            
            # Brief human-like delay before CAPTCHA interaction
            delay = random.uniform(2, 4)
            self.logger.info(f"Waiting {delay:.1f}s before CAPTCHA interaction...")
            time.sleep(delay)
            
            # Look for ReCAPTCHA iframe with more detailed search
            recaptcha_frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
            self.logger.info(f"Found {len(recaptcha_frames)} ReCAPTCHA iframes")
            
            # Also check for any ReCAPTCHA containers
            recaptcha_containers = self.driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha")
            self.logger.info(f"Found {len(recaptcha_containers)} ReCAPTCHA containers")
            
            if not recaptcha_frames and not recaptcha_containers:
                self.logger.info("No ReCAPTCHA found on page")
                return True
            
            if not self.config.RECAPTCHA_AUTO_SOLVE:
                self.logger.warning("ReCAPTCHA detected but auto-solving disabled. Manual intervention required.")
                return False
                
            if not self.solver:
                self.logger.error("ReCAPTCHA detected but solver not available. Install selenium-recaptcha-solver")
                return False
                
            # First, try automated checkbox click using RecaptchaSolver
            try:
                # Use the main ReCAPTCHA iframe for clicking
                main_iframe = recaptcha_frames[0] if recaptcha_frames else None
                if main_iframe:
                    self.logger.info("Using RecaptchaSolver.click_recaptcha_v2() for checkbox click")
                    self.solver.click_recaptcha_v2(iframe=main_iframe)
                    time.sleep(3)
                    
                    # Check if automated click solved it completely (no challenge appeared)
                    if self._verify_recaptcha_solved():
                        self.logger.info("ReCAPTCHA solved with automated checkbox click - no challenge appeared")
                        return True
                else:
                    self.logger.warning("No ReCAPTCHA iframe found for automated clicking")
                    # Fallback to manual click method
                    self._try_manual_recaptcha_click()
                    time.sleep(3)
                    
                    if self._verify_recaptcha_solved():
                        self.logger.info("ReCAPTCHA solved with manual click fallback - no challenge appeared")
                        return True
                        
            except Exception as e:
                self.logger.warning(f"Automated checkbox click failed: {str(e)}, falling back to manual click")
                # Fallback to manual click method
                self._try_manual_recaptcha_click()
                time.sleep(3)
                
                if self._verify_recaptcha_solved():
                    self.logger.info("ReCAPTCHA solved with manual click fallback - no challenge appeared")
                    return True
            
            # Check if image challenge appeared after clicking
            if self._detect_image_challenge():
                self.logger.info("ReCAPTCHA image challenge detected. Attempting to switch to audio challenge...")
                
                # Try to switch to audio challenge
                if self._switch_to_audio_challenge():
                    self.logger.info("Successfully switched to audio challenge")
                    # Continue with automated audio solving below
                else:
                    self.logger.warning("Could not switch to audio challenge")
                    return False
            
            # Save a screenshot for debugging before attempting to solve
            self._save_debug_screenshot("recaptcha_before_solve")
            
            # Try automated solving with selenium-recaptcha-solver (audio method)
            if self.solver:
                for attempt in range(self.config.RECAPTCHA_MAX_RETRIES):
                    try:
                        self.logger.info(f"ReCAPTCHA automated solving attempt {attempt + 1}")
                        
                        # Check if we have an image challenge and need to switch to audio
                        if self._detect_image_challenge():
                            self.logger.info("Image challenge detected, switching to audio...")
                            if not self._switch_to_audio_challenge():
                                self.logger.warning(f"Failed to switch to audio on attempt {attempt + 1}")
                                continue
                        
                        # Add randomized delay to avoid detection
                        delay = random.uniform(2, 4)
                        self.logger.info(f"Waiting {delay:.2f} seconds before solving attempt")
                        time.sleep(delay)
                        
                        # Find the appropriate iframe for solving
                        solving_iframe = None
                        # Try challenge iframe first (for audio challenges)
                        challenge_iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']")
                        if challenge_iframes:
                            solving_iframe = challenge_iframes[0]
                            self.logger.info("Using challenge iframe for solving")
                        else:
                            # Fallback to original recaptcha frame
                            solving_iframe = recaptcha_frames[0]
                            self.logger.info("Using main recaptcha iframe for solving")
                        
                        # Solve using audio method with iframe parameter
                        self.logger.info("Calling automated ReCAPTCHA solver...")
                        self.solver.solve_recaptcha_v2_challenge(solving_iframe)
                        self.logger.info("ReCAPTCHA solver call completed")
                        
                        # Wait and check if solved
                        wait_time = random.uniform(5, 8)  # Longer wait for audio challenges
                        self.logger.info(f"Waiting {wait_time:.2f} seconds for ReCAPTCHA to complete")
                        time.sleep(wait_time)
                        
                        # Save screenshot after solve attempt
                        self._save_debug_screenshot(f"recaptcha_after_solve_attempt_{attempt + 1}")
                        
                        # Verify ReCAPTCHA is solved
                        if self._verify_recaptcha_solved():
                            self.logger.info("ReCAPTCHA solved with automated audio solver")
                            return True
                            
                    except Exception as e:
                        self.logger.warning(f"ReCAPTCHA attempt {attempt + 1} failed: {str(e)}")
                        
                        # Save error screenshot
                        self._save_debug_screenshot(f"recaptcha_error_attempt_{attempt + 1}")
                        
                        # If Google detected automated queries, wait much longer
                        if "automated queries" in str(e).lower():
                            self.logger.info("Detected automation warning, waiting longer...")
                            time.sleep(random.uniform(15, 25))
                        else:
                            time.sleep(random.uniform(3, 6))
            
            # If we still have challenges, make one final attempt with audio
            if self._detect_image_challenge():
                self.logger.info("Final attempt: Switching remaining image challenge to audio...")
                if self._switch_to_audio_challenge():
                    try:
                        self.logger.info("Final audio challenge solving attempt...")
                        solving_iframe = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']")
                        if solving_iframe:
                            self.solver.solve_recaptcha_v2_challenge(solving_iframe[0])
                            time.sleep(6)
                            if self._verify_recaptcha_solved():
                                self.logger.info("ReCAPTCHA solved in final audio attempt")
                                return True
                    except Exception as e:
                        self.logger.error(f"Final audio attempt failed: {str(e)}")
            
            self.logger.error("All automated ReCAPTCHA solving attempts failed")
            
            self.logger.error("Failed to solve ReCAPTCHA after all attempts")
            return False
            
        except Exception as e:
            self.logger.error(f"Error solving ReCAPTCHA: {str(e)}")
            return False
    
    def _try_manual_recaptcha_click(self):
        """Try to click ReCAPTCHA checkbox manually with human-like behavior."""
        try:
            # Add random delay before interacting (human behavior)
            pre_delay = random.uniform(0.5, 2.0)
            self.logger.debug(f"Waiting {pre_delay:.2f}s before ReCAPTCHA interaction")
            time.sleep(pre_delay)
            
            # Look for the ReCAPTCHA checkbox iframe
            checkbox_iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/anchor']")
            self.logger.info(f"Found {len(checkbox_iframes)} ReCAPTCHA checkbox iframes")
            
            if checkbox_iframes:
                # Simulate human-like page interaction before clicking ReCAPTCHA
                self._simulate_human_page_interaction()
                
                self.logger.info("Attempting to switch to ReCAPTCHA checkbox iframe")
                self.driver.switch_to.frame(checkbox_iframes[0])
                try:
                    # Try multiple selectors for the checkbox
                    checkbox_selectors = [
                        ".recaptcha-checkbox-border",
                        ".recaptcha-checkbox",
                        "#recaptcha-anchor",
                        "div[role='checkbox']"
                    ]
                    
                    checkbox = None
                    for selector in checkbox_selectors:
                        try:
                            checkbox = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            self.logger.info(f"Found checkbox using selector: {selector}")
                            break
                        except TimeoutException:
                            continue
                    
                    if checkbox:
                        # Human-like click with slight delay and movement
                        self._human_like_click(checkbox)
                        self.logger.info("Successfully clicked ReCAPTCHA checkbox")
                        
                        # Random post-click delay
                        post_delay = random.uniform(1.5, 3.5)
                        time.sleep(post_delay)
                    else:
                        self.logger.warning("Could not find clickable ReCAPTCHA checkbox")
                        
                except Exception as e:
                    self.logger.debug(f"Could not click ReCAPTCHA checkbox: {str(e)}")
                finally:
                    self.driver.switch_to.default_content()
                    
        except Exception as e:
            self.logger.debug(f"Manual ReCAPTCHA click failed: {str(e)}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
    
    def _switch_to_audio_challenge(self) -> bool:
        """Switch from image challenge to audio challenge with human-like behavior.
        
        Returns:
            True if successfully switched to audio, False otherwise
        """
        try:
            # Random delay before switching (human thinking time)
            thinking_delay = random.uniform(1.0, 3.0)
            self.logger.debug(f"Waiting {thinking_delay:.2f}s before switching to audio (human thinking)")
            time.sleep(thinking_delay)
            
            # Look for challenge iframe
            challenge_iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']")
            if not challenge_iframes:
                self.logger.warning("No challenge iframe found")
                return False
            
            # Switch to challenge iframe
            self.driver.switch_to.frame(challenge_iframes[0])
            
            try:
                # Look for audio button with multiple selectors
                audio_selectors = [
                    "#recaptcha-audio-button",  # Primary audio button ID
                    "button[id*='audio']",      # Button with audio in ID
                    "button[title*='audio']",   # Button with audio in title
                    "button[aria-label*='audio']",  # Button with audio in aria-label
                    ".rc-button-audio",         # Audio button class
                    "button[class*='audio']",   # Button with audio in class name
                ]
                
                audio_button = None
                for selector in audio_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements and elements[0].is_displayed() and elements[0].is_enabled():
                            audio_button = elements[0]
                            self.logger.info(f"Found audio button using selector: {selector}")
                            break
                    except:
                        continue
                
                if audio_button:
                    # Human-like click on audio button
                    self._human_like_click(audio_button)
                    self.logger.info("Clicked audio challenge button")
                    
                    # Wait for audio challenge to load with randomization
                    load_delay = random.uniform(1.5, 3.0)
                    time.sleep(load_delay)
                    
                    # Verify audio challenge is loaded
                    audio_challenge_selectors = [
                        "audio",                    # HTML5 audio element
                        ".rc-audiochallenge",      # Audio challenge container
                        "#audio-source",           # Audio source element
                        "button[title*='Play']",   # Play button
                    ]
                    
                    for selector in audio_challenge_selectors:
                        if self.driver.find_elements(By.CSS_SELECTOR, selector):
                            self.logger.info(f"Audio challenge loaded - found: {selector}")
                            return True
                    
                    self.logger.warning("Audio challenge button clicked but audio elements not found")
                    return False
                    
                else:
                    self.logger.warning("Audio button not found in challenge iframe")
                    return False
                    
            finally:
                self.driver.switch_to.default_content()
                
        except Exception as e:
            self.logger.error(f"Error switching to audio challenge: {str(e)}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _detect_image_challenge(self) -> bool:
        """Detect if ReCAPTCHA image challenge is currently shown.
        
        Returns:
            True if image challenge is visible, False otherwise
        """
        try:
            # Look for image challenge iframes
            challenge_iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']")
            if not challenge_iframes:
                return False
            
            # Switch to challenge iframe to check for images
            self.driver.switch_to.frame(challenge_iframes[0])
            try:
                # Look for common image challenge elements
                image_selectors = [
                    ".rc-imageselect-target",  # Main image selection area
                    ".rc-image-tile-wrapper",  # Individual image tiles
                    ".rc-imageselect-instructions",  # Challenge instructions
                    "table[class*='rc-imageselect']",  # Image selection table
                ]
                
                for selector in image_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.logger.info(f"Found image challenge element: {selector}")
                        return True
                
                # Also check for challenge text
                body_text = self.driver.find_elements(By.TAG_NAME, "body")
                if body_text:
                    text_content = body_text[0].text.lower()
                    challenge_keywords = ["select all", "click on", "images", "traffic lights", "crosswalks", "vehicles"]
                    if any(keyword in text_content for keyword in challenge_keywords):
                        self.logger.info(f"Found challenge text indicating image challenge")
                        return True
                
                return False
                
            finally:
                self.driver.switch_to.default_content()
                
        except Exception as e:
            self.logger.debug(f"Error detecting image challenge: {str(e)}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False

    def _verify_recaptcha_solved(self) -> bool:
        """Verify if ReCAPTCHA has been solved.
        
        Returns:
            True if ReCAPTCHA is solved, False otherwise
        """
        try:
            self.logger.info("Verifying ReCAPTCHA solution...")
            
            # Method 1: Check g-recaptcha-response token
            response_elements = self.driver.find_elements(By.NAME, "g-recaptcha-response")
            self.logger.info(f"Found {len(response_elements)} g-recaptcha-response elements")
            
            if response_elements:
                response_value = response_elements[0].get_attribute("value")
                self.logger.info(f"ReCAPTCHA response token length: {len(response_value) if response_value else 0}")
                if response_value and response_value.strip():
                    self.logger.info("✓ ReCAPTCHA token found and not empty")
                    return True
                else:
                    self.logger.info("✗ ReCAPTCHA token is empty")
            
            # Method 2: Check for ReCAPTCHA checkbox in checked state
            try:
                checkbox_iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/anchor']")
                self.logger.info(f"Found {len(checkbox_iframes)} checkbox iframes")
                
                if checkbox_iframes:
                    self.driver.switch_to.frame(checkbox_iframes[0])
                    checkboxes = self.driver.find_elements(By.CSS_SELECTOR, ".recaptcha-checkbox-checked")
                    checkboxes_checkmark = self.driver.find_elements(By.CSS_SELECTOR, ".recaptcha-checkbox-checkmark")
                    self.driver.switch_to.default_content()
                    
                    self.logger.info(f"Found {len(checkboxes)} checked checkboxes, {len(checkboxes_checkmark)} checkmarks")
                    
                    if checkboxes or checkboxes_checkmark:
                        self.logger.info("✓ ReCAPTCHA checkbox appears to be checked")
                        return True
            except Exception as iframe_error:
                self.logger.debug(f"Error checking iframe checkbox: {iframe_error}")
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass
            
            # Method 3: Look for success indicators in page source
            page_source = self.driver.page_source.lower()
            success_patterns = [
                "recaptcha-success", 
                "captcha solved", 
                "verification complete",
                "recaptcha-checkbox-checked"
            ]
            
            for pattern in success_patterns:
                if pattern in page_source:
                    self.logger.info(f"✓ Found success pattern in page source: {pattern}")
                    return True
            
            # Method 4: Check if search can proceed (try clicking search button)
            try:
                search_buttons = self.driver.find_elements(By.ID, "btnSearch")
                if search_buttons and search_buttons[0].is_enabled():
                    self.logger.info("✓ Search button is enabled - ReCAPTCHA likely solved")
                    return True
                elif search_buttons:
                    self.logger.info("✗ Search button is present but disabled")
                else:
                    self.logger.info("✗ Search button not found")
            except Exception as btn_error:
                self.logger.debug(f"Error checking search button: {btn_error}")
            
            self.logger.info("✗ ReCAPTCHA verification failed - no success indicators found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying ReCAPTCHA: {str(e)}")
            return False
    
    def search_uen(self, uen: str) -> Dict[str, Any]:
        """Search for UEN information on IRAS website.
        
        Args:
            uen: UEN number to search for
            
        Returns:
            Dictionary containing search results or error information
        """
        result = {
            "uen": uen,
            "success": False,
            "data": {},
            "error": None,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            self.logger.info(f"Searching for UEN: {uen}")
            
            # Step 1: Navigate to IRAS (CAPTCHA becomes visible)
            self.logger.info("Step 1: Navigating to IRAS website (CAPTCHA will be visible)")
            if not self.navigate_to_iras():
                result["error"] = "Failed to navigate to IRAS website"
                return result
            
            # Add debug information about the page
            debug_info = self._debug_page_elements()
            self.logger.info(f"Page debug info: {debug_info}")
            
            # Find UEN input field first
            uen_input = None
            possible_selectors = [
                (By.ID, "txtKeyword"),  # Primary IRAS selector
                (By.CSS_SELECTOR, "input[name*='txtKeyword']"),  # ASP.NET fallback
                (By.CSS_SELECTOR, "input[placeholder*='UEN']"),  # Generic fallback
            ]
            
            for selector_type, selector_value in possible_selectors:
                try:
                    uen_input = self.wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    self.logger.info(f"Found UEN input field using selector: {selector_type}={selector_value}")
                    break
                except TimeoutException:
                    continue
            
            if not uen_input:
                result["error"] = "Could not find UEN input field on the page"
                return result
            
            # Step 2: Enter UEN
            self.logger.info(f"Entering UEN: {uen}")
            uen_input.clear()
            uen_input.send_keys(uen)
            
            # Step 3: Solve ReCAPTCHA (after UEN is entered, before clicking search)
            self.logger.info("Solving ReCAPTCHA after entering UEN...")
            if not self.solve_recaptcha():
                result["error"] = "Failed to solve ReCAPTCHA"
                return result
            
            # Find search button (after CAPTCHA is solved)
            search_button = None
            search_selectors = [
                (By.ID, "btnSearch"),  # Primary IRAS selector
                (By.CSS_SELECTOR, "input[value*='SEARCH']"),  # Value-based fallback
                (By.CSS_SELECTOR, "input[type='submit']"),  # Generic submit button
            ]
            
            for selector_type, selector_value in search_selectors:
                try:
                    search_button = self.driver.find_element(selector_type, selector_value)
                    self.logger.info(f"Found search button using selector: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            if not search_button:
                result["error"] = "Could not find search button on the page"
                return result

            # Step 4: Click search button (JavaScript click bypasses overlays)
            self.logger.info("Step 4: Clicking search button to submit query...")
            try:
                self.driver.execute_script("arguments[0].click();", search_button)
                self.logger.info("Successfully clicked search button")
            except Exception as e:
                # Fallback to regular click
                try:
                    search_button.click()
                    self.logger.info("Successfully clicked search button with fallback method")
                except Exception as fallback_error:
                    result["error"] = f"Could not click search button: {str(e)}"
                    return result            # Wait for results page to load
            time.sleep(3)
            
            # Check for "No records found" message
            page_text = self.driver.page_source.lower()
            if "no records found" in page_text or "record not found" in page_text:
                result["success"] = True
                result["data"] = {"status": "No records found"}
                self.logger.info(f"No records found for UEN: {uen}")
                return result
            
            # Try to extract result data
            extracted_data = self._extract_search_results()
            
            if extracted_data:
                result["success"] = True
                result["data"] = extracted_data
                self.logger.info(f"Successfully retrieved data for UEN: {uen}")
            else:
                result["error"] = "Could not extract data from results page"
            
        except TimeoutException:
            error_msg = f"Timeout while searching for UEN: {uen}"
            self.logger.error(error_msg)
            result["error"] = error_msg
            
        except Exception as e:
            error_msg = f"Error searching for UEN {uen}: {str(e)}"
            self.logger.error(error_msg)
            result["error"] = error_msg
        
        # Add random delay between requests
        self._add_random_delay()
        
        return result
    
    def _extract_search_results(self) -> Dict[str, str]:
        """Extract search results from the page.
        
        Returns:
            Dictionary containing extracted data
        """
        data = {}
        
        try:
            # Wait for results table/container to load
            time.sleep(2)
            
            # Try to find results table or data container
            results_container = None
            container_selectors = [
                (By.ID, "dgResults"),  # Primary IRAS results table
                (By.CSS_SELECTOR, "table[id*='result']"),  # Generic results table
                (By.TAG_NAME, "table"),  # Any table fallback
            ]
            
            for selector_type, selector_value in container_selectors:
                try:
                    results_container = self.driver.find_element(selector_type, selector_value)
                    self.logger.info(f"Found results container using: {selector_type}={selector_value}")
                    break
                except:
                    continue
            
            if results_container:
                # Extract all visible text from the results area
                results_text = results_container.text.strip()
                data["raw_results"] = results_text
                
                # Extract key IRAS fields
                field_mappings = {
                    "uen": ["uen"],
                    "status": ["status"],
                    "gst_registration": ["gst"],
                }
                
                # Try to extract structured data from table rows
                try:
                    rows = results_container.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            field_name = cells[0].text.strip().lower()
                            field_value = cells[1].text.strip()
                            
                            # Map field names to our standard names
                            for standard_name, possible_names in field_mappings.items():
                                for possible_name in possible_names:
                                    if possible_name in field_name:
                                        data[standard_name] = field_value
                                        break
                except Exception as e:
                    self.logger.debug(f"Could not extract structured table data: {str(e)}")
                
                # Simple pattern matching for key fields
                if not any(key != "raw_results" for key in data.keys()):
                    lines = results_text.split('\n')
                    for line in lines:
                        if "not registered" in line.lower():
                            data["gst_registration"] = "Not registered"
                        elif "registered" in line.lower() and "from" in line.lower():
                            data["gst_registration"] = "Registered"
            
            # Mark extraction status
            if len(data) > 0:
                data["extraction_status"] = "success"
            else:
                data["extraction_status"] = "no_data_found"
                    
        except Exception as e:
            self.logger.warning(f"Error extracting data fields: {str(e)}")
            data["extraction_error"] = str(e)
            
            # Fallback: get page title and some content
            try:
                data["page_title"] = self.driver.title
                data["page_url"] = self.driver.current_url
            except:
                pass
        
        return data
    
    def _add_random_delay(self):
        """Add random delay between requests to avoid detection."""
        delay_min, delay_max = self.config.RANDOM_DELAY_RANGE
        delay = random.uniform(delay_min, delay_max)
        self.logger.debug(f"Adding random delay of {delay:.2f} seconds")
        time.sleep(delay)
    
    def _save_debug_screenshot(self, filename_suffix: str):
        """Save a debug screenshot."""
        try:
            import os
            os.makedirs("logs/screenshots", exist_ok=True)
            timestamp = int(time.time())
            filename = f"logs/screenshots/{filename_suffix}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            self.logger.debug(f"Debug screenshot saved: {filename}")
        except Exception as e:
            self.logger.debug(f"Could not save debug screenshot: {str(e)}")
    
    def _debug_page_elements(self) -> Dict[str, Any]:
        """Debug helper to inspect page elements."""
        try:
            return {
                "page_title": self.driver.title,
                "page_url": self.driver.current_url,
                "has_txtKeyword": bool(self.driver.find_elements(By.ID, "txtKeyword")),
                "has_btnSearch": bool(self.driver.find_elements(By.ID, "btnSearch")),
                "has_recaptcha_frames": len(self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")),
                "has_recaptcha_containers": len(self.driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha"))
            }
        except Exception as e:
            return {"debug_error": str(e)}
    
    def scrape_multiple_uens(self, uens: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple UENs with optimized session reuse.
        
        Args:
            uens: List of UEN numbers to scrape
            
        Returns:
            List of results for each UEN
        """
        results = []
        session_initialized = False
        
        try:
            self.start_session()
            session_initialized = True
            
            # Navigate to IRAS once and reuse the session
            if not self.navigate_to_iras():
                self.logger.error("Failed to navigate to IRAS website")
                return results
            
            # CAPTCHA will be solved per-UEN as needed (not upfront)
            
            for i, uen in enumerate(uens, 1):
                self.logger.info(f"Processing UEN {i}/{len(uens)}: {uen}")
                
                result = self.search_uen(uen)
                results.append(result)
                
                # Log progress
                if result["success"]:
                    self.logger.info(f"✓ UEN {uen} processed successfully")
                else:
                    self.logger.warning(f"✗ UEN {uen} failed: {result['error']}")
                
                # Minimal delay between UENs for speed
                if i < len(uens):  # Don't delay after the last UEN
                    time.sleep(self.config.REQUEST_DELAY)
            
        except Exception as e:
            self.logger.error(f"Error in batch scraping: {str(e)}")
        
        finally:
            if session_initialized:
                self.close_session()
        
        return results