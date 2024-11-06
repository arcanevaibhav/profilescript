import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from fake_useragent import UserAgent

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Load config
config = load_config()
profile_paths = config["profile_paths"]
extension_ids = config["extension_ids"]
proxies = config["proxies"]

ua = UserAgent()

def create_driver(profile_path, extension_id, proxy):
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    chrome_options.add_argument(f"--load-extension={extension_id}")
    chrome_options.add_argument(f"--proxy-server=http://{proxy}")

    user_agent = ua.random
    chrome_options.add_argument(f"user-agent={user_agent}")

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Use Service to specify the path to chromedriver
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    set_fingerprint(driver)
    return driver

def set_fingerprint(driver):
    script = """
    Intl.DateTimeFormat = function() { return { resolvedOptions: () => ({ timeZone: 'America/New_York' }) }; };
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter(parameter);
    };
    Object.defineProperty(window, 'screen', {
        value: { width: 1366, height: 768, availWidth: 1366, availHeight: 768 }
    });
    """
    driver.execute_script(script)

drivers = []
try:
    for profile, extension_id, proxy in zip(profile_paths, extension_ids.values(), proxies):
        driver = create_driver(profile, extension_id, proxy)
        drivers.append(driver)
        driver.get(f"chrome-extension://{extension_id}/path/to/mining_page.html")
        time.sleep(2)
        
    while True:
        time.sleep(60)
finally:
    for driver in drivers:
        driver.quit()
