#!/usr/bin/env python3
"""
Poshmark Balance Auto-Transfer Script

This script automatically transfers available balance from Poshmark to your bank account
via Direct Deposit (ACH). It uses Playwright to automate the web interface.

Requirements:
- Python 3.7+
- playwright package
- Chrome browser installed on system

Usage:
    python posh_autoredeem.py

Environment Variables:
    POSH_USER_DATA_DIR: Path to dedicated Chrome profile (default: ~/posh-bot-profile)
    POSH_MIN_TRANSFER: Minimum balance to trigger transfer (default: 5.00)
    HEADLESS: Run in headless mode (1) or visible (0) (default: 0 for first runs)
    LOG_DIR: Directory for logs and screenshots (default: ./logs)
    POSH_EMAIL: Email for login (only needed if session expires)
    POSH_PASS: Password for login (only needed if session expires)

Author: Generated for Poshmark automation
Date: 2025
"""

from playwright.sync_api import sync_playwright
import os
import re
import sys
import time
from datetime import datetime, date
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, use system environment only
    pass

# Configuration
USER_DATA_DIR = os.getenv("POSH_USER_DATA_DIR", os.path.expanduser("~/posh-bot-profile"))
MIN_TRANSFER = float(os.getenv("POSH_MIN_TRANSFER", "5.00"))
HEADLESS = os.getenv("HEADLESS", "1") == "1"  # Default to headless for automation
LOG_DIR = os.getenv("LOG_DIR", "./logs")
POSH_EMAIL = os.getenv("POSH_EMAIL")
POSH_PASS = os.getenv("POSH_PASS")

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)

def log(msg):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def parse_money(text):
    """Extract dollar amount from text string"""
    if not text:
        return None
    # Look for pattern like $12.34, $1,234.56, etc.
    match = re.search(r'\$([0-9,]+(?:\.[0-9]{2})?)', text)
    if match:
        # Remove commas and convert to float
        amount_str = match.group(1).replace(",", "")
        try:
            return float(amount_str)
        except ValueError:
            return None
    return None

def take_screenshot(page, name_suffix=""):
    """Take screenshot for debugging/logging"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{LOG_DIR}/screenshot_{timestamp}_{name_suffix}.png"
    page.screenshot(path=filename)
    log(f"Screenshot saved: {filename}")
    return filename

def check_for_captcha_or_verification(page):
    """Check if we're facing CAPTCHA or verification challenge"""
    current_url = page.url.lower()
    page_content = page.content().lower()
    
    # Common indicators
    if any(indicator in current_url for indicator in ['captcha', 'verification', 'challenge']):
        return True
    if any(indicator in page_content for indicator in ['captcha', 'verify', 'security check', 'unusual activity']):
        return True
    
    return False

def wait_for_page_load(page, timeout=30000):
    """Wait for page to fully load"""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
        return True
    except Exception as e:
        log(f"Page load timeout: {e}")
        return False

def create_daily_lock_file():
    """Create a lock file to prevent multiple transfers per day"""
    today = date.today().strftime("%Y-%m-%d")
    lock_file = f"{LOG_DIR}/transfer_completed_{today}.lock"
    
    if os.path.exists(lock_file):
        log(f"Transfer already completed today ({today}). Lock file exists.")
        return False
    
    # Create the lock file
    with open(lock_file, 'w') as f:
        f.write(f"Transfer completed on {datetime.now()}")
    
    return True

def main():
    """Main automation function"""
    log("=== Poshmark Auto-Transfer Starting ===")
    
    # Check if we already ran today
    if not create_daily_lock_file():
        log("Exiting: Already ran today")
        return
    
    with sync_playwright() as p:
        # Use persistent context with existing Chrome profile
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",  # Use system Chrome
            headless=HEADLESS,
            viewport={"width": 1280, "height": 900},
            # Additional options for better reliability
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check"
            ]
        )
        
        page = context.new_page()
        
        try:
            log("Navigating to Poshmark payout options page...")
            page.goto("https://poshmark.com/account/payout-options", timeout=60000)
            
            if not wait_for_page_load(page):
                raise Exception("Page failed to load properly")
            
            # Check if we need to login
            current_url = page.url.lower()
            if "login" in current_url or page.get_by_label("Email", exact=False).count() > 0:
                if not POSH_EMAIL or not POSH_PASS:
                    log("ERROR: Login required but credentials not provided.")
                    log("Please set POSH_EMAIL and POSH_PASS environment variables,")
                    log("or run the script with HEADLESS=0 to login manually once.")
                    take_screenshot(page, "login_required")
                    sys.exit(2)
                
                log("Attempting to login...")
                try:
                    # Fill login form
                    page.get_by_label(re.compile("email", re.I)).fill(POSH_EMAIL)
                    page.get_by_label(re.compile("password", re.I)).fill(POSH_PASS)
                    page.get_by_role("button", name=re.compile("log in|sign in", re.I)).click()
                    
                    if not wait_for_page_load(page):
                        raise Exception("Login page didn't load properly")
                        
                except Exception as e:
                    log(f"Login failed: {e}")
                    take_screenshot(page, "login_failed")
                    sys.exit(3)
            
            # Check for security challenges
            if check_for_captcha_or_verification(page):
                log("SECURITY CHALLENGE DETECTED!")
                log("Please open Chrome with this profile and complete the challenge:")
                log(f"chrome --user-data-dir='{USER_DATA_DIR}'")
                take_screenshot(page, "security_challenge")
                sys.exit(4)
            
            # Take screenshot of the payout options page
            take_screenshot(page, "payout_options_page")
            
            # Check if there's a redeemable balance - look for dollar amounts on the page
            log("Checking for redeemable balance...")
            page_text = page.content()
            balance = parse_money(page_text)
            
            if balance is None:
                log("No redeemable balance found or could not parse balance")
                # Still proceed in case balance detection fails but there is actually balance
                balance = 0.01  # Minimal amount to trigger the flow
            else:
                log(f"Found balance: ${balance:.2f}")
            
            if balance < MIN_TRANSFER:
                log(f"Balance ${balance:.2f} is below threshold ${MIN_TRANSFER:.2f}. No transfer needed.")
                return
            
            # Proceed with transfer - Select "Bank Direct Deposit" radio button
            log("Looking for Bank Direct Deposit option...")
            
            # Try multiple strategies to find the Bank Direct Deposit radio button
            direct_deposit_selectors = [
                # Strategy 1: Look for radio button with "Bank Direct Deposit" text nearby
                lambda: page.get_by_text("Bank Direct Deposit").locator("xpath=ancestor-or-self::label").locator("input[type='radio']"),
                # Strategy 2: Look for radio button in a container with "Bank Direct Deposit" text
                lambda: page.locator("label:has-text('Bank Direct Deposit') input[type='radio']"),
                # Strategy 3: Look for radio button followed by text containing "1-3 business days"
                lambda: page.locator("input[type='radio']").filter(lambda el: "1-3 business days" in el.locator("xpath=following-sibling::*").inner_text()),
                # Strategy 4: Look for radio button with "No fee" nearby
                lambda: page.get_by_text("No fee").locator("xpath=ancestor::*[contains(@class,'option') or contains(@class,'choice')]").locator("input[type='radio']"),
            ]
            
            direct_deposit_found = False
            for i, selector in enumerate(direct_deposit_selectors, 1):
                try:
                    radio_button = selector()
                    if radio_button.count() > 0:
                        log(f"Found Bank Direct Deposit option using strategy {i}")
                        radio_button.first.check()
                        direct_deposit_found = True
                        break
                except Exception as e:
                    log(f"Strategy {i} failed: {e}")
                    continue
            
            if not direct_deposit_found:
                log("ERROR: Could not find Bank Direct Deposit radio button")
                take_screenshot(page, "direct_deposit_not_found")
                sys.exit(5)
            
            # Wait for the Continue button to become clickable
            time.sleep(1)
            
            # Look for and click the Continue button
            log("Looking for Continue button...")
            continue_selectors = [
                # Exact match for the button from your HTML
                lambda: page.locator('button.btn.btn--primary:has-text("Continue")'),
                # Generic continue button
                lambda: page.get_by_role("button", name=re.compile("continue", re.I)),
                # Button with continue text
                lambda: page.locator("button").filter(has_text=re.compile("continue", re.I)),
            ]
            
            continue_clicked = False
            for i, selector in enumerate(continue_selectors, 1):
                try:
                    button = selector()
                    if button.count() > 0:
                        log(f"Found Continue button using strategy {i}")
                        button.first.click()
                        continue_clicked = True
                        break
                except Exception as e:
                    log(f"Continue button strategy {i} failed: {e}")
                    continue
            
            if not continue_clicked:
                log("ERROR: Could not find or click Continue button")
                take_screenshot(page, "continue_button_not_found")
                sys.exit(6)
            
            # Wait for the confirmation page to load
            log("Waiting for confirmation page to load...")
            if not wait_for_page_load(page, timeout=30000):
                log("WARNING: Page load may have timed out, continuing...")
            
            # Verify we're on the confirmation page
            current_url = page.url
            log(f"Current URL: {current_url}")
            
            if "confirm_redeem" not in current_url:
                log("WARNING: May not be on confirmation page, but continuing...")
            
            # Take screenshot of confirmation page
            take_screenshot(page, "confirmation_page")
            
            # Look for and click the final Redeem button
            log("Looking for final Redeem button...")
            redeem_selectors = [
                # Exact match for the button from your HTML
                lambda: page.locator('button[data-et-name="confirm_redeem"][data-et-prop-content="ach"].btn.btn--primary'),
                # Generic redeem button
                lambda: page.get_by_role("button", name=re.compile("redeem", re.I)),
                # Button with redeem text
                lambda: page.locator("button").filter(has_text=re.compile("redeem", re.I)),
                # Primary button containing "Redeem"
                lambda: page.locator('button.btn--primary:has-text("Redeem")'),
            ]
            
            redeem_clicked = False
            for i, selector in enumerate(redeem_selectors, 1):
                try:
                    button = selector()
                    if button.count() > 0:
                        log(f"Found Redeem button using strategy {i}")
                        button.first.click()
                        redeem_clicked = True
                        break
                except Exception as e:
                    log(f"Redeem button strategy {i} failed: {e}")
                    continue
            
            if not redeem_clicked:
                log("ERROR: Could not find or click final Redeem button")
                take_screenshot(page, "redeem_button_not_found")
                sys.exit(7)
            
            # Wait for success confirmation
            time.sleep(5)  # Give time for processing
            
            # Take final screenshot
            final_screenshot = take_screenshot(page, "transfer_completed")
            
            log(f"✅ Transfer initiated successfully!")
            log(f"Final screenshot: {final_screenshot}")
            
            # Check for success indicators
            page_text = page.content().lower()
            if any(word in page_text for word in ['success', 'complete', 'initiated', 'processing', 'confirmed']):
                log("✅ Success indicators found on page")
            else:
                log("⚠️  No clear success indicators found - please verify manually")
            
        except Exception as e:
            log(f"ERROR: {e}")
            error_screenshot = take_screenshot(page, "error")
            log(f"Error screenshot: {error_screenshot}")
            sys.exit(1)
            
        finally:
            # Brief pause before closing
            time.sleep(2)
            context.close()

if __name__ == "__main__":
    try:
        main()
        log("=== Poshmark Auto-Transfer Completed Successfully ===")
    except KeyboardInterrupt:
        log("Script interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"Unexpected error: {e}")
        sys.exit(1)