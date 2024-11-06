from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from fake_useragent import UserAgent

profile_paths = [
    "/path/to/profile1",
    "/path/to/profile2",
    "/path/to/profile3",
]

extension_ids = {
    "dawn": "extension_id_for_dawn",
    "gradient": "extension_id_for_gradient",
    "grass": "extension_id_for_grass",
}

proxies = [
    "proxy1_ip:port",
    "proxy2_ip:port",
    "proxy3_ip:port",
]

ua = UserAgent()

def create_driver(profile_path, extension_id, proxy):
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    chrome_options.add_argument(f"--load-extension={extension_id}")
    chrome_options.add_argument(f"--proxy-server=http://{proxy}")
    
    user_agent = ua.random
    chrome_options.add_argument(f"user-agent={user_agent}")

    # Hide WebDriver flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=chrome_options)
    set_fingerprint(driver)  # Set custom fingerprint settings
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

