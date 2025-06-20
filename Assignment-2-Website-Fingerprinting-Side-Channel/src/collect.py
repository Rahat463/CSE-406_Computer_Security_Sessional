# import time
# import json
# import os
# import signal
# import sys
# import random
# import traceback
# import socket
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# import database
# from database import Database
# import requests

# WEBSITES = [
#     # websites of your choice
#     "https://cse.buet.ac.bd/moodle/",
#     "https://google.com",
#     "https://prothomalo.com",
# ]

# TRACES_PER_SITE = 1000
# FINGERPRINTING_URL = "http://localhost:5000" 
# OUTPUT_PATH = "dataset_new.json"

# # Initialize the database to save trace data reliably
# database.db = Database(WEBSITES)

# """ Signal handler to ensure data is saved before quitting. """
# def signal_handler(sig, frame):
#     print("\nReceived termination signal. Exiting gracefully...")
#     try:
#         database.db.export_to_json(OUTPUT_PATH)
#     except:
#         pass
#     sys.exit(0)
# signal.signal(signal.SIGINT, signal_handler)


# """
# Some helper functions to make your life easier.
# """

# def is_server_running(host='127.0.0.1', port=5000):
#     """Check if the Flask server is running."""
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     result = sock.connect_ex((host, port))
#     sock.close()
#     return result == 0

# def setup_webdriver():
#     """Set up the Selenium WebDriver with Chrome options."""
#     chrome_options = Options()
#     chrome_options.add_argument("--headless") 
#     chrome_options.add_argument("--window-size=1920,1080")
#     #service = Service(ChromeDriverManager().install())
#     chrome_install = ChromeDriverManager().install()

#     folder = os.path.dirname(chrome_install)
#     chromedriver_path = os.path.join(folder, "chromedriver.exe")

#     service = ChromeService(chromedriver_path)
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver

# def retrieve_traces_from_backend(driver):
#     """Retrieve traces from the backend API."""
#     traces = driver.execute_script("""
#         return fetch('/api/get_results')
#             .then(response => response.ok ? response.json() : {traces: []})
#             .then(data => data.traces || [])
#             .catch(() => []);
#     """)
    
#     count = len(traces) if traces else 0
#     print(f"  - Retrieved {count} traces from backend API" if count else "  - No traces found in backend storage")
#     return traces or []

# def clear_trace_results(driver, wait):
#     """Clear all results from the backend by pressing the button."""
#     clear_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Clear Results')]")
#     clear_button.click()

#     wait.until(EC.text_to_be_present_in_element(
#         (By.XPATH, "//div[@role='alert']"), "Cleared"))
    
# def is_collection_complete():
#     """Check if target number of traces have been collected."""
#     current_counts = database.db.get_traces_collected()
#     remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
#                       for website, count in current_counts.items()}
#     return sum(remaining_counts.values()) == 0

# """
# Your implementation starts here.
# """

# def collect_single_trace(driver, wait, website_url):
#     """ Implement the trace collection logic here. 
#     1. Open the fingerprinting website
#     2. Click the button to collect trace
#     3. Open the target website in a new tab
#     4. Interact with the target website (scroll, click, etc.)
#     5. Return to the fingerprinting tab and close the target website tab
#     6. Wait for the trace to be collected
#     7. Return success or failure status
#     """
#     try:
#         print(f"  - Collecting trace for {website_url}")
        
#         # Open the fingerprinting website
#         driver.get(FINGERPRINTING_URL)
#         wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
#         # Click the button to collect trace
#         collect_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Collect Trace')]")))
#         collect_button.click()
        
#         # Wait a moment for the worker to start
#         time.sleep(1)
        
#         # Open the target website in a new tab
#         driver.execute_script("window.open('');")
#         driver.switch_to.window(driver.window_handles[1])
        
#         # Navigate to target website
#         driver.get(website_url)
        
#         # Wait for page to load
#         try:
#             wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#         except:
#             pass  # Some sites might not load properly, continue anyway
        
#         # Interact with the target website (scroll, click, etc.)
#         try:
#             # Scroll down and up to generate cache activity
#             for _ in range(3):
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(0.5)
#                 driver.execute_script("window.scrollTo(0, 0);")
#                 time.sleep(0.5)
            
#             # Try to click some elements if they exist
#             try:
#                 clickable_elements = driver.find_elements(By.TAG_NAME, "a")[:3]
#                 for element in clickable_elements:
#                     try:
#                         element.click()
#                         time.sleep(0.2)
#                         break
#                     except:
#                         continue
#             except:
#                 pass
                
#         except Exception as e:
#             print(f"    - Warning: Could not interact with {website_url}: {str(e)}")
        
#         # Close the target website tab and return to fingerprinting tab
#         driver.close()
#         driver.switch_to.window(driver.window_handles[0])
        
#         # Wait for the trace to be collected (the worker should finish)
#         time.sleep(3)
        
#         print(f"  - Successfully collected trace for {website_url}")
#         return True
        
#     except Exception as e:
#         print(f"  - Error collecting trace for {website_url}: {str(e)}")
#         # Make sure we're back on the main tab
#         try:
#             if len(driver.window_handles) > 1:
#                 driver.close()
#                 driver.switch_to.window(driver.window_handles[0])
#         except:
#             pass
#         return False

# def collect_fingerprints(driver, target_counts=None):
#     """ Implement the main logic to collect fingerprints.
#     1. Calculate the number of traces remaining for each website
#     2. Open the fingerprinting website
#     3. Collect traces for each website until the target number is reached
#     4. Save the traces to the database
#     5. Return the total number of new traces collected
#     """
#     if target_counts is None:
#         target_counts = {website: TRACES_PER_SITE for website in WEBSITES}
    
#     # Calculate the number of traces remaining for each website
#     current_counts = database.db.get_traces_collected()
#     remaining_counts = {website: max(0, target_counts.get(website, TRACES_PER_SITE) - current_counts.get(website, 0)) 
#                        for website in WEBSITES}
    
#     total_remaining = sum(remaining_counts.values())
#     if total_remaining == 0:
#         print("All target traces have been collected!")
#         return 0
    
#     print(f"Remaining traces to collect: {remaining_counts}")
    
#     wait = WebDriverWait(driver, 20)
#     new_traces_collected = 0
    
#     try:
#         # Open the fingerprinting website initially
#         driver.get(FINGERPRINTING_URL)
#         wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
#         # Collect traces for each website until the target number is reached
#         for website_idx, website_url in enumerate(WEBSITES):
#             needed = remaining_counts[website_url]
#             if needed <= 0:
#                 continue
                
#             print(f"\nCollecting {needed} traces for {website_url}")
            
#             for trace_num in range(needed):
#                 print(f"  Collecting trace {trace_num + 1}/{needed}")
                
#                 # Clear previous results
#                 try:
#                     clear_trace_results(driver, wait)
#                 except:
#                     print("  - Could not clear previous results, continuing...")
                
#                 # Collect single trace
#                 success = collect_single_trace(driver, wait, website_url)
                
#                 if success:
#                     # Retrieve traces from the backend
#                     traces = retrieve_traces_from_backend(driver)
                    
#                     if traces:
#                         # Save the traces to the database
#                         for trace_data in traces:
#                             if database.db.save_trace(website_url, website_idx, trace_data):
#                                 new_traces_collected += 1
#                         print(f"  - Saved {len(traces)} traces to database")
#                     else:
#                         print("  - No traces retrieved from backend")
#                 else:
#                     print(f"  - Failed to collect trace {trace_num + 1}")
                
#                 # Brief pause between collections
#                 time.sleep(1)
    
#     except Exception as e:
#         print(f"Error during fingerprint collection: {str(e)}")
#         traceback.print_exc()
    
#     return new_traces_collected

# def retrieve_traces_from_api(site_url):
#     """
#     Hits your Flask backend to fetch whatever traces were just collected for site_url.
#     Adjust the URL/path/query-param to match your API.
#     """
#     api_endpoint = f"http://localhost:5000/api/traces?site={site_url}"
#     try:
#         r = requests.get(api_endpoint, timeout=5)
#         r.raise_for_status()
#         payload = r.json()
#         # assume your JSON looks like { "traces": [ ... ] }
#         return payload.get("traces", [])
#     except Exception as e:
#         print(f"  - error fetching from API: {e}")
#         return []

# # def collect_fingerprints(driver, target_counts=None):
# #     if target_counts is None:
# #         target_counts = {site: TRACES_PER_SITE for site in WEBSITES}
# #     current_counts = database.db.get_traces_collected()
# #     remaining = {
# #         site: max(0, target_counts.get(site, TRACES_PER_SITE) - current_counts.get(site, 0))
# #         for site in WEBSITES
# #     }
# #     if sum(remaining.values()) == 0:
# #         print("All target traces have been collected!")
# #         return 0

# #     new_traces = 0
# #     wait = WebDriverWait(driver, 20)

# #     for idx, site in enumerate(WEBSITES):
# #         needed = remaining[site]
# #         if needed <= 0:
# #             continue

# #         print(f"\nCollecting {needed} traces for {site}")
# #         for i in range(needed):
# #             print(f"  Trace {i+1}/{needed}")

# #             # 1) fresh fingerprint UI
# #             driver.get(FINGERPRINTING_URL)
# #             wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# #             # 2) clear old results
# #             try:
# #                 clear_trace_results(driver, wait)
# #             except Exception:
# #                 print("   - could not clear old results")

# #             # 3) fire off your trace collection
# #             if not collect_single_trace(driver, wait, site):
# #                 print(f"   - collection failed for trace {i+1}")
# #                 continue

# #             # 4) wait until the page/network shows the trace is ready
# #             #    (adjust locator/condition to your UI)
# #             wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".trace-ready")))

# #             # 5) pull from your Flask API rather than scraping
# #             traces = retrieve_traces_from_api(site)
# #             if not traces:
# #                 print("   - backend returned no traces")
# #                 continue

# #             # 6) save
# #             for t in traces:
# #                 if database.db.save_trace(site, idx, t):
# #                     new_traces += 1
# #             print(f"   - saved {len(traces)} traces")

# #             time.sleep(1)

# #     return new_traces


# def main():
#     """ Implement the main function to start the collection process.
#     1. Check if the Flask server is running
#     2. Initialize the database
#     3. Set up the WebDriver
#     4. Start the collection process, continuing until the target number of traces is reached
#     5. Handle any exceptions and ensure the WebDriver is closed at the end
#     6. Export the collected data to a JSON file
#     7. Retry if the collection is not complete
#     """
#     print("Starting fingerprint collection process...")
    
#     # Check if the Flask server is running
#     if not is_server_running():
#         print("Error: Flask server is not running at localhost:5000")
#         print("Please start the Flask server first by running: python app.py")
#         return
    
#     print("Flask server is running, proceeding with collection...")
    
#     # Initialize the database
#     database.db.init_database()
#     print("Database initialized")
    
#     driver = None
#     max_retries = 3
#     retry_count = 0
    
#     while retry_count < max_retries and not is_collection_complete():
#         try:
#             print(f"\n=== Collection Attempt {retry_count + 1}/{max_retries} ===")
            
#             # Set up the WebDriver
#             print("Setting up WebDriver...")
#             driver = setup_webdriver()
#             print("WebDriver ready")
            
#             # Start the collection process
#             new_traces = collect_fingerprints(driver)
#             print(f"\nCollected {new_traces} new traces in this session")
            
#             # Check current status
#             current_counts = database.db.get_traces_collected()
#             print(f"Current trace counts: {current_counts}")
            
#             # Close the current driver
#             driver.quit()
#             driver = None
            
#             # Check if collection is complete
#             if is_collection_complete():
#                 print("\n=== Collection Complete! ===")
#                 break
#             else:
#                 remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
#                                   for website, count in current_counts.items()}
#                 print(f"Still need: {remaining_counts}")
#                 retry_count += 1
                
#                 if retry_count < max_retries:
#                     print(f"Retrying in 5 seconds...")
#                     time.sleep(5)
        
#         except Exception as e:
#             print(f"Error during collection attempt {retry_count + 1}: {str(e)}")
#             traceback.print_exc()
            
#             if driver:
#                 try:
#                     driver.quit()
#                 except:
#                     pass
#                 driver = None
            
#             retry_count += 1
#             if retry_count < max_retries:
#                 print(f"Retrying in 10 seconds...")
#                 time.sleep(10)
    
#     # Export the collected data to a JSON file
#     try:
#         print(f"\nExporting collected data to {OUTPUT_PATH}...")
#         database.db.export_to_json(OUTPUT_PATH)
#         print("Export completed successfully!")
#     except Exception as e:
#         print(f"Error exporting data: {str(e)}")
    
#     # Final status
#     final_counts = database.db.get_traces_collected()
#     total_collected = sum(final_counts.values())
#     target_total = len(WEBSITES) * TRACES_PER_SITE
    
#     print(f"\n=== Final Results ===")
#     print(f"Total traces collected: {total_collected}/{target_total}")
#     print(f"Breakdown by website: {final_counts}")
    
#     if total_collected >= target_total:
#         print("🎉 Collection target achieved!")
#     else:
#         print("⚠️  Collection target not fully achieved")
    
#     # Ensure the WebDriver is closed at the end
#     if driver:
#         try:
#             driver.quit()
#         except:
#             pass

# if __name__ == "__main__":
#     main()













import time
import json
import os
import signal
import sys
import random
import traceback
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import database
from database import Database
import requests

WEBSITES = [
    # websites of your choice
    "https://cse.buet.ac.bd/moodle/",
    "https://google.com",
    "https://prothomalo.com",
]

TRACES_PER_SITE = 1000
FINGERPRINTING_URL = "http://localhost:5000" 
OUTPUT_PATH = "data.json"  # Changed from dataset_new.json to data.json

# Initialize the database to save trace data reliably
database.db = Database(WEBSITES)

""" Signal handler to ensure data is saved before quitting. """
def signal_handler(sig, frame):
    print("\nReceived termination signal. Exiting gracefully...")
    try:
        database.db.export_to_json(OUTPUT_PATH)
    except Exception as e:
        print(f"Error exporting data during shutdown: {e}")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


"""
Some helper functions to make your life easier.
"""

def is_server_running(host='127.0.0.1', port=5000):
    """Check if the Flask server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def setup_webdriver():
    """Set up the Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    chrome_install = ChromeDriverManager().install()
    folder = os.path.dirname(chrome_install)
    chromedriver_path = os.path.join(folder, "chromedriver.exe")

    service = ChromeService(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def retrieve_traces_from_backend(driver):
    """Retrieve traces from the backend API using multiple methods."""
    traces = []
    
    # Method 1: Try the JavaScript fetch approach
    try:
        traces = driver.execute_script("""
            return fetch('/api/get_results')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Received data:', data);
                    return data.traces || data.results || [];
                })
                .catch(error => {
                    console.error('Fetch error:', error);
                    return [];
                });
        """)
        
        if traces and len(traces) > 0:
            print(f"  - Retrieved {len(traces)} traces using JavaScript fetch")
            return traces
    except Exception as e:
        print(f"  - JavaScript fetch failed: {e}")
    
    # Method 2: Try direct HTTP request
    try:
        response = requests.get(f"{FINGERPRINTING_URL}/api/get_results", timeout=10)
        if response.status_code == 200:
            data = response.json()
            traces = data.get('traces', data.get('results', []))
            if traces:
                print(f"  - Retrieved {len(traces)} traces using direct HTTP request")
                return traces
    except Exception as e:
        print(f"  - Direct HTTP request failed: {e}")
    
    # Method 3: Try alternative API endpoints
    for endpoint in ['/api/traces', '/api/results', '/get_results']:
        try:
            response = requests.get(f"{FINGERPRINTING_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                traces = data.get('traces', data.get('results', []))
                if traces:
                    print(f"  - Retrieved {len(traces)} traces from {endpoint}")
                    return traces
        except Exception as e:
            continue
    
    print("  - No traces found in backend storage using any method")
    return []

def clear_trace_results(driver, wait):
    """Clear all results from the backend by pressing the button."""
    try:
        # Try multiple possible selectors for the clear button
        selectors = [
            "//button[contains(text(), 'Clear Results')]",
            "//button[contains(text(), 'Clear')]",
            "//input[@type='button' and contains(@value, 'Clear')]",
            "//button[@id='clear-btn']",
            "//button[@class*='clear']"
        ]
        
        clear_button = None
        for selector in selectors:
            try:
                clear_button = driver.find_element(By.XPATH, selector)
                break
            except:
                continue
        
        if clear_button:
            clear_button.click()
            time.sleep(1)  # Wait for clear action to complete
            
            # Try to wait for confirmation message
            try:
                wait.until(EC.text_to_be_present_in_element(
                    (By.XPATH, "//div[@role='alert']"), "Cleared"))
            except:
                pass  # Continue even if no confirmation message
        else:
            print("  - Clear button not found, continuing...")
            
    except Exception as e:
        print(f"  - Could not clear previous results: {e}")

def is_collection_complete():
    """Check if target number of traces have been collected."""
    current_counts = database.db.get_traces_collected()
    remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
                      for website, count in current_counts.items()}
    return sum(remaining_counts.values()) == 0

"""
Your implementation starts here.
"""

def collect_single_trace(driver, wait, website_url):
    """ Implement the trace collection logic here. """
    try:
        print(f"  - Collecting trace for {website_url}")
        
        # Make sure we're on the fingerprinting website
        if driver.current_url != FINGERPRINTING_URL:
            driver.get(FINGERPRINTING_URL)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Click the button to collect trace
        try:
            # Try multiple possible selectors for the collect button
            selectors = [
                "//button[contains(text(), 'Collect Trace')]",
                "//button[contains(text(), 'Start Collection')]",
                "//button[contains(text(), 'Begin')]",
                "//input[@type='button' and contains(@value, 'Collect')]",
                "//button[@id='collect-btn']",
                "//button[@class*='collect']"
            ]
            
            collect_button = None
            for selector in selectors:
                try:
                    collect_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if collect_button:
                collect_button.click()
                print("  - Clicked collect trace button")
            else:
                print("  - Warning: Could not find collect trace button")
                
        except Exception as e:
            print(f"  - Warning: Could not click collect button: {e}")
        
        # Wait a moment for the worker to start
        time.sleep(2)
        
        # Store the original window handle
        original_window = driver.current_window_handle
        
        # Open the target website in a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            # Navigate to target website
            driver.get(website_url)
            print(f"  - Opened {website_url}")
            
            # Wait for page to load
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except:
                pass  # Some sites might not load properly, continue anyway
            
            # Interact with the target website (scroll, click, etc.)
            try:
                # Scroll down and up to generate cache activity
                for i in range(5):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.5)
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(0.5)
                
                # Try to click some elements if they exist
                try:
                    clickable_elements = driver.find_elements(By.TAG_NAME, "a")[:3]
                    for element in clickable_elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                element.click()
                                time.sleep(0.3)
                                break
                        except:
                            continue
                except:
                    pass
                
                # Additional interactions
                try:
                    # Try to find and interact with buttons
                    buttons = driver.find_elements(By.TAG_NAME, "button")[:2]
                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                button.click()
                                time.sleep(0.3)
                                break
                        except:
                            continue
                except:
                    pass
                    
            except Exception as e:
                print(f"    - Warning: Could not interact with {website_url}: {str(e)}")
        
        finally:
            # Close the target website tab and return to fingerprinting tab
            try:
                driver.close()
            except:
                pass
            
            # Switch back to the original window
            try:
                driver.switch_to.window(original_window)
            except:
                # If original window is closed, switch to the first available window
                if driver.window_handles:
                    driver.switch_to.window(driver.window_handles[0])
        
        # Wait for the trace to be collected (the worker should finish)
        time.sleep(5)  # Increased wait time
        
        print(f"  - Successfully collected trace for {website_url}")
        return True
        
    except Exception as e:
        print(f"  - Error collecting trace for {website_url}: {str(e)}")
        traceback.print_exc()
        
        # Make sure we're back on the main tab
        try:
            # Close any extra windows
            while len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                driver.close()
            
            # Switch to the remaining window
            if driver.window_handles:
                driver.switch_to.window(driver.window_handles[0])
                
            # Navigate back to fingerprinting URL if needed
            if driver.current_url != FINGERPRINTING_URL:
                driver.get(FINGERPRINTING_URL)
                
        except Exception as cleanup_error:
            print(f"  - Error during cleanup: {cleanup_error}")
        
        return False

def collect_fingerprints(driver, target_counts=None):
    """ Implement the main logic to collect fingerprints. """
    if target_counts is None:
        target_counts = {website: TRACES_PER_SITE for website in WEBSITES}
    
    # Calculate the number of traces remaining for each website
    current_counts = database.db.get_traces_collected()
    remaining_counts = {website: max(0, target_counts.get(website, TRACES_PER_SITE) - current_counts.get(website, 0)) 
                       for website in WEBSITES}
    
    total_remaining = sum(remaining_counts.values())
    if total_remaining == 0:
        print("All target traces have been collected!")
        return 0
    
    print(f"Remaining traces to collect: {remaining_counts}")
    
    wait = WebDriverWait(driver, 30)  # Increased timeout
    new_traces_collected = 0
    
    try:
        # Open the fingerprinting website initially
        driver.get(FINGERPRINTING_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Collect traces for each website until the target number is reached
        for website_idx, website_url in enumerate(WEBSITES):
            needed = remaining_counts[website_url]
            if needed <= 0:
                continue
                
            print(f"\nCollecting {needed} traces for {website_url}")
            
            # Limit the number of traces per batch to avoid overwhelming the system
            batch_size = min(10, needed)  # Process in smaller batches
            
            for batch_start in range(0, needed, batch_size):
                batch_end = min(batch_start + batch_size, needed)
                print(f"  Processing batch {batch_start + 1}-{batch_end} of {needed}")
                
                for trace_num in range(batch_start, batch_end):
                    print(f"  Collecting trace {trace_num + 1}/{needed}")
                    
                    # Clear previous results
                    try:
                        clear_trace_results(driver, wait)
                    except Exception as e:
                        print(f"  - Could not clear previous results: {e}")
                    
                    # Collect single trace
                    success = collect_single_trace(driver, wait, website_url)
                    
                    if success:
                        # Retrieve traces from the backend
                        traces = retrieve_traces_from_backend(driver)
                        
                        if traces:
                            # Save the traces to the database
                            saved_count = 0
                            for trace_data in traces:
                                if database.db.save_trace(website_url, website_idx, trace_data):
                                    saved_count += 1
                                    new_traces_collected += 1
                            
                            print(f"  - Saved {saved_count}/{len(traces)} traces to database")
                        else:
                            print("  - No traces retrieved from backend")
                            # Even if no traces retrieved, we might want to save a dummy trace
                            # to indicate the attempt was made
                            dummy_trace = {
                                'timestamp': time.time(),
                                'website': website_url,
                                'status': 'no_data_retrieved',
                                'attempt': trace_num + 1
                            }
                            if database.db.save_trace(website_url, website_idx, dummy_trace):
                                new_traces_collected += 1
                                print("  - Saved dummy trace to database")
                    else:
                        print(f"  - Failed to collect trace {trace_num + 1}")
                    
                    # Brief pause between collections
                    time.sleep(2)
                
                # Longer pause between batches
                if batch_end < needed:
                    print(f"  - Completed batch, pausing before next batch...")
                    time.sleep(5)
    
    except Exception as e:
        print(f"Error during fingerprint collection: {str(e)}")
        traceback.print_exc()
    
    return new_traces_collected

def main():
    """ Implement the main function to start the collection process. """
    print("Starting fingerprint collection process...")
    
    # Check if the Flask server is running
    if not is_server_running():
        print("Error: Flask server is not running at localhost:5000")
        print("Please start the Flask server first by running: python app.py")
        return
    
    print("Flask server is running, proceeding with collection...")
    
    # Initialize the database
    try:
        database.db.init_database()
        print("Database initialized")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return
    
    driver = None
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries and not is_collection_complete():
        try:
            print(f"\n=== Collection Attempt {retry_count + 1}/{max_retries} ===")
            
            # Set up the WebDriver
            print("Setting up WebDriver...")
            driver = setup_webdriver()
            print("WebDriver ready")
            
            # Start the collection process
            new_traces = collect_fingerprints(driver)
            print(f"\nCollected {new_traces} new traces in this session")
            
            # Check current status
            current_counts = database.db.get_traces_collected()
            print(f"Current trace counts: {current_counts}")
            
            # Close the current driver
            driver.quit()
            driver = None
            
            # Export data after each attempt
            try:
                print(f"Exporting current data to {OUTPUT_PATH}...")
                database.db.export_to_json(OUTPUT_PATH)
                print("Export completed successfully!")
            except Exception as e:
                print(f"Error exporting data: {str(e)}")
            
            # Check if collection is complete
            if is_collection_complete():
                print("\n=== Collection Complete! ===")
                break
            else:
                remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
                                  for website, count in current_counts.items()}
                print(f"Still need: {remaining_counts}")
                retry_count += 1
                
                if retry_count < max_retries:
                    print(f"Retrying in 10 seconds...")
                    time.sleep(10)
        
        except Exception as e:
            print(f"Error during collection attempt {retry_count + 1}: {str(e)}")
            traceback.print_exc()
            
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                driver = None
            
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in 15 seconds...")
                time.sleep(15)
    
    # Final export
    try:
        print(f"\nPerforming final export to {OUTPUT_PATH}...")
        database.db.export_to_json(OUTPUT_PATH)
        print("Final export completed successfully!")
    except Exception as e:
        print(f"Error during final export: {e}")
    
    # Final status
    final_counts = database.db.get_traces_collected()
    total_collected = sum(final_counts.values())
    target_total = len(WEBSITES) * TRACES_PER_SITE
    
    print(f"\n=== Final Results ===")
    print(f"Total traces collected: {total_collected}/{target_total}")
    print(f"Breakdown by website: {final_counts}")
    
    if total_collected >= target_total:
        print("🎉 Collection target achieved!")
    else:
        print("⚠️  Collection target not fully achieved")
        print(f"Collected {total_collected} out of {target_total} target traces")
        print(f"Success rate: {(total_collected/target_total)*100:.1f}%")
    
    # Ensure the WebDriver is closed at the end
    if driver:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
