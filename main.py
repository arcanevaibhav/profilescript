from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
import time
from fake_useragent import UserAgent
import random
import logging
import json
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="bot_log.txt",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load configuration from a JSON file
def load_config(config_path="config.json"):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        logging.info("Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file {config_path} not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing the configuration file: {e}")
        raise

# Initialize user agent
ua = UserAgent()

# Load configurations
config = load_config()

profile_paths = config.get("profiles", [
    "/path/to/profile1",
    "/path/to/profile2",
    "/path/to/profile3",
])

extension_ids = config.get("extensions", {
    "dawn": "extension_id_for_dawn",
    "gradient": "extension_id_for_gradient",
    "grass": "extension_id_for_grass",
})

proxies = config.get("proxies", [
    "proxy1_ip:port",
    "proxy2_ip:port",
    "proxy3_ip:port",
])

# Path to Chromedriver
CHROMEDRIVER_PATH = config.get("chromedriver_path", "/path/to/chromedriver")

# Ensure the number of profiles, extensions, and proxies match
if not (len(profile_paths) == len(extension_ids) == len(proxies)):
    logging.warning("The number of profiles, extensions, and proxies do not match.")

def log_action(action, level="info"):
    if level == "info":
        logging.info(action)
    elif level == "error":
        logging.error(action)
    elif level == "warning":
        logging.warning(action)
    else:
        logging.debug(action)

def create_driver(profile_path, extension_id, proxy):
    try:
        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={profile_path}")
        chrome_options.add_argument(f"--load-extension={extension_id}")
        chrome_options.add_argument(f"--proxy-server=http://{proxy}")
        
        user_agent = ua.random
        chrome_options.add_argument(f"user-agent={user_agent}")

        # Hide WebDriver flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Optional: Run in headless mode
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")
        
        # Initialize WebDriver with specified Chromedriver path
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
        log_action(f"Driver created for profile: {profile_path}", "info")
        
        set_fingerprint(driver)
        return driver
    except WebDriverException as e:
        log_action(f"Error creating WebDriver instance: {e}", "error")
        return None

def set_fingerprint(driver):
    script = """
    // Spoof timezone
    Intl.DateTimeFormat = function() { 
        return { 
            resolvedOptions: () => ({ timeZone: 'America/New_York' }) 
        }; 
    };
    
    // Spoof WebGL
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter(parameter);
    };
    
    // Spoof screen dimensions
    Object.defineProperty(window, 'screen', {
        value: { width: 1366, height: 768, availWidth: 1366, availHeight: 768 }
    });
    """
    try:
        driver.execute_script(script)
        log_action("Fingerprint set successfully.", "info")
    except WebDriverException as e:
        log_action(f"Error setting fingerprint: {e}", "error")

def random_sleep(min_seconds=1, max_seconds=3):
    duration = random.uniform(min_seconds, max_seconds)
    log_action(f"Sleeping for {duration:.2f} seconds.", "info")
    time.sleep(duration)

def retry_operation(operation, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return operation()
        except (TimeoutException, WebDriverException) as e:
            log_action(f"Retrying ({attempt + 1}/{retries}) due to: {e}", "warning")
            time.sleep(delay)
    log_action("All retry attempts failed.", "error")
    return None

def run_bot(profile, extension_id, proxy):
    driver = retry_operation(lambda: create_driver(profile, extension_id, proxy))
    if driver:
        try:
            url = f"chrome-extension://{extension_id}/path/to/mining_page.html"
            driver.get(url)
            log_action(f"Navigated to {url}", "info")
            random_sleep(2, 4)
            
            # Keep the driver alive
            while True:
                random_sleep(50, 70)
        except WebDriverException as e:
            log_action(f"WebDriverException occurred: {e}", "error")
        finally:
            driver.quit()
            log_action(f"Driver for profile {profile} quit.", "info")

def main():
    threads = []
    for profile, (ext_key, extension_id), proxy in zip(profile_paths, extension_ids.items(), proxies):
        ext_name, ext_id = ext_key, extension_id
        t = Thread(target=run_bot, args=(profile, ext_id, proxy))
        t.start()
        threads.append(t)
        log_action(f"Thread started for profile: {profile}, extension: {ext_id}, proxy: {proxy}", "info")
    
    # Optionally, join threads if you want the main thread to wait
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
