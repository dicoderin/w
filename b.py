import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from web3 import Web3
from eth_account import Account
import json
import logging
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("Private key not found in environment variables. Please add PRIVATE_KEY to .env file.")

# Initialize Web3
RPC_URL = "https://api.zan.top/node/v1/pharos/testnet/1a49bd503c164cadbe04af55f275e16d"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise ConnectionError(f"Failed to connect to RPC: {RPC_URL}")

logger.info(f"Connected to Pharos Network: {w3.is_connected()}")
logger.info(f"Chain ID: {w3.eth.chain_id}")

# Set up account
account = Account.from_key(PRIVATE_KEY)
wallet_address = account.address
logger.info(f"Using wallet address: {wallet_address}")

# Browser setup
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # Uncomment the line below if you want to run headless
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Wait for element and click
def wait_and_click(driver, by, selector, timeout=60):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(random.uniform(1, 2))
    element.click()
    return element

# Wait for element to be visible
def wait_for_element(driver, by, selector, timeout=60):
    element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )
    return element

# Connect wallet using Metamask-like extension
def connect_wallet(driver, site_url):
    logger.info(f"Navigating to {site_url}")
    driver.get(site_url)
    time.sleep(5)  # Wait for page to load
    
    try:
        # Click connect wallet button
        connect_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Connect') or contains(text(), 'connect') or contains(@class, 'connect')]")
        logger.info("Clicked connect wallet button")
        time.sleep(2)
        
        # Select wallet type (usually Metamask or similar)
        metamask_option = wait_and_click(driver, By.XPATH, "//div[contains(text(), 'MetaMask') or contains(@class, 'metamask')]")
        logger.info("Selected MetaMask")
        
        # Switch to MetaMask popup and approve connection
        original_window = driver.current_window_handle
        wait_for_new_window(driver, original_window)
        
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
                
        connect_confirm = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Connect')]")
        logger.info("Approved wallet connection")
        
        # Switch back to main window
        driver.switch_to.window(original_window)
        time.sleep(3)
        
        logger.info("Wallet connected successfully")
        return True
    except Exception as e:
        logger.error(f"Error connecting wallet: {str(e)}")
        return False

# Wait for new window/tab to appear
def wait_for_new_window(driver, current_handles, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if len(driver.window_handles) > len(current_handles):
            return True
        time.sleep(0.5)
    raise TimeoutError("Timed out waiting for new window")

# Function to interact with app.zentrafi.xyz
def interact_with_app_zentrafi(driver):
    try:
        # Launch Token functionality
        launch_token_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Launch Token') or contains(@class, 'launch')]")
        logger.info("Clicked Launch Token button")
        time.sleep(3)
        
        # Fill token details if needed
        # This is a placeholder - you'll need to identify the actual form fields
        token_name_field = wait_for_element(driver, By.XPATH, "//input[@name='name' or contains(@placeholder, 'name')]")
        token_name_field.send_keys("TestToken")
        
        token_symbol_field = wait_for_element(driver, By.XPATH, "//input[@name='symbol' or contains(@placeholder, 'symbol')]")
        token_symbol_field.send_keys("TTK")
        
        supply_field = wait_for_element(driver, By.XPATH, "//input[@name='supply' or contains(@placeholder, 'supply')]")
        supply_field.send_keys("1000000")
        
        # Submit token launch
        submit_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Create') or contains(@type, 'submit')]")
        logger.info("Submitted token launch")
        time.sleep(10)  # Wait for transaction to process
        
        # Try Buy/Sell
        buy_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Buy') or contains(@class, 'buy')]")
        logger.info("Clicked Buy button")
        time.sleep(2)
        
        amount_field = wait_for_element(driver, By.XPATH, "//input[@name='amount' or contains(@placeholder, 'amount')]")
        amount_field.send_keys("0.1")
        
        confirm_buy = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Swap') or contains(@type, 'submit')]")
        logger.info("Confirmed Buy transaction")
        time.sleep(10)  # Wait for transaction to process
        
        # Try selling
        sell_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Sell') or contains(@class, 'sell')]")
        logger.info("Clicked Sell button")
        time.sleep(2)
        
        sell_amount_field = wait_for_element(driver, By.XPATH, "//input[@name='amount' or contains(@placeholder, 'amount')]")
        sell_amount_field.send_keys("0.05")
        
        confirm_sell = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Swap') or contains(@type, 'submit')]")
        logger.info("Confirmed Sell transaction")
        time.sleep(10)  # Wait for transaction to process
        
        logger.info("Successfully completed app.zentrafi.xyz interactions")
        return True
    except Exception as e:
        logger.error(f"Error in app.zentrafi.xyz interaction: {str(e)}")
        return False

# Function to interact with x.zentrafi.xyz
def interact_with_x_zentrafi(driver):
    try:
        # Try Swap functionality
        swap_tab = wait_and_click(driver, By.XPATH, "//a[contains(text(), 'Swap') or contains(@class, 'swap')]")
        logger.info("Navigated to Swap tab")
        time.sleep(3)
        
        # Select from token (Pharos)
        from_token_selector = wait_and_click(driver, By.XPATH, "//div[contains(@class, 'token-select') or contains(@class, 'dropdown')]")
        pharos_option = wait_and_click(driver, By.XPATH, "//div[contains(text(), 'PHRS') or contains(text(), 'Pharos')]")
        logger.info("Selected Pharos as from token")
        
        # Enter amount to swap
        amount_field = wait_for_element(driver, By.XPATH, "//input[contains(@placeholder, 'amount') or contains(@name, 'amount')]")
        amount_field.send_keys("0.01")
        
        # Select to token (USDC/USDT/WPharos)
        to_token_selector = wait_and_click(driver, By.XPATH, "(//div[contains(@class, 'token-select') or contains(@class, 'dropdown')])[2]")
        usdc_option = wait_and_click(driver, By.XPATH, "//div[contains(text(), 'USDC')]")
        logger.info("Selected USDC as to token")
        
        # Confirm swap
        swap_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Swap') or contains(@class, 'swap-button')]")
        time.sleep(2)
        confirm_swap = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Swap')]")
        logger.info("Confirmed swap transaction")
        time.sleep(10)  # Wait for transaction to process
        
        # Try to add LP
        liquidity_tab = wait_and_click(driver, By.XPATH, "//a[contains(text(), 'Pool') or contains(text(), 'Liquidity') or contains(@class, 'liquidity')]")
        logger.info("Navigated to Liquidity/Pool tab")
        time.sleep(3)
        
        add_liquidity_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Add') or contains(@class, 'add-liquidity')]")
        logger.info("Clicked Add Liquidity button")
        time.sleep(2)
        
        # Select first token for LP
        first_token_selector = wait_and_click(driver, By.XPATH, "//div[contains(@class, 'token-select') or contains(@class, 'dropdown')]")
        phrs_option = wait_and_click(driver, By.XPATH, "//div[contains(text(), 'PHRS') or contains(text(), 'Pharos')]")
        logger.info("Selected PHRS as first token for LP")
        
        # Enter amount for first token
        first_amount_field = wait_for_element(driver, By.XPATH, "//input[contains(@placeholder, 'amount') or contains(@name, 'amount')]")
        first_amount_field.send_keys("0.5")
        
        # Select second token for LP
        second_token_selector = wait_and_click(driver, By.XPATH, "(//div[contains(@class, 'token-select') or contains(@class, 'dropdown')])[2]")
        usdc_option = wait_and_click(driver, By.XPATH, "//div[contains(text(), 'USDC')]")
        logger.info("Selected USDC as second token for LP")
        
        # Confirm adding liquidity
        supply_button = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Supply') or contains(text(), 'Add') or contains(@class, 'supply')]")
        time.sleep(2)
        confirm_supply = wait_and_click(driver, By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Supply')]")
        logger.info("Confirmed adding liquidity")
        time.sleep(10)  # Wait for transaction to process
        
        logger.info("Successfully completed x.zentrafi.xyz interactions")
        return True
    except Exception as e:
        logger.error(f"Error in x.zentrafi.xyz interaction: {str(e)}")
        return False

def main():
    driver = setup_browser()
    try:
        # Interact with app.zentrafi.xyz
        app_url = "https://app.zentrafi.xyz/"
        driver.get(app_url)
        time.sleep(5)
        
        if connect_wallet(driver, app_url):
            interact_with_app_zentrafi(driver)
            logger.info("Completed tasks on app.zentrafi.xyz")
        else:
            logger.error("Failed to connect wallet on app.zentrafi.xyz")
        
        # Interact with x.zentrafi.xyz
        x_url = "https://x.zentrafi.xyz/"
        driver.get(x_url)
        time.sleep(5)
        
        if connect_wallet(driver, x_url):
            interact_with_x_zentrafi(driver)
            logger.info("Completed tasks on x.zentrafi.xyz")
        else:
            logger.error("Failed to connect wallet on x.zentrafi.xyz")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    finally:
        logger.info("Bot execution completed")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()
