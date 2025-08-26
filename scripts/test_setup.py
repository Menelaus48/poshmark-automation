#!/usr/bin/env python3
"""
Test Script for Poshmark Automation Setup

This script tests that the automation environment is properly configured
and can access Poshmark without performing any actual transfers.

Usage:
    python scripts/test_setup.py
"""

from playwright.sync_api import sync_playwright
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from main script
sys.path.insert(0, str(Path(__file__).parent.parent))

from posh_autoredeem import (
    USER_DATA_DIR, LOG_DIR, HEADLESS, MIN_TRANSFER,
    log, take_screenshot, wait_for_page_load, check_for_captcha_or_verification
)

def test_environment():
    """Test that the environment is properly configured"""
    log("=== Testing Environment Configuration ===")
    
    print(f"Chrome Profile Directory: {USER_DATA_DIR}")
    print(f"Log Directory: {LOG_DIR}")
    print(f"Headless Mode: {HEADLESS}")
    print(f"Minimum Transfer: ${MIN_TRANSFER:.2f}")
    
    # Check if profile directory exists
    if not os.path.exists(USER_DATA_DIR):
        print("❌ Chrome profile directory doesn't exist")
        print("   Run: python scripts/setup_profile.py")
        return False
    
    # Check if log directory exists
    if not os.path.exists(LOG_DIR):
        print("❌ Log directory doesn't exist - creating it...")
        os.makedirs(LOG_DIR, exist_ok=True)
    
    print("✅ Environment configuration looks good")
    return True

def test_browser_access():
    """Test that we can launch the browser and access Poshmark"""
    log("=== Testing Browser Access ===")
    
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                channel="chrome",
                headless=False,  # Always visible for testing
                viewport={"width": 1280, "height": 900},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--no-default-browser-check"
                ]
            )
            
            page = context.new_page()
            
            log("Navigating to Poshmark balance page...")
            page.goto("https://poshmark.com/balance", timeout=60000)
            
            if not wait_for_page_load(page):
                raise Exception("Page failed to load properly")
            
            # Take a screenshot for verification
            screenshot_path = take_screenshot(page, "test_access")
            
            current_url = page.url
            log(f"Current URL: {current_url}")
            
            # Check if we're logged in
            if "login" in current_url.lower():
                log("⚠️  Not logged in - you'll need to login manually first")
                log("   Run: python scripts/setup_profile.py")
                context.close()
                return False
            
            # Check for security challenges
            if check_for_captcha_or_verification(page):
                log("⚠️  Security challenge detected")
                log("   You may need to complete verification manually")
                context.close()
                return False
            
            log("✅ Successfully accessed Poshmark balance page")
            log(f"   Screenshot saved: {screenshot_path}")
            
            # Brief pause to let user see the page
            input("Press Enter to close the test browser...")
            
            context.close()
            return True
            
        except Exception as e:
            log(f"❌ Browser test failed: {e}")
            return False

def test_playwright_installation():
    """Test that Playwright is properly installed"""
    log("=== Testing Playwright Installation ===")
    
    try:
        with sync_playwright() as p:
            log("✅ Playwright imported successfully")
            
            # Check if Chrome is available
            browser = p.chromium.launch(channel="chrome", headless=True)
            browser.close()
            log("✅ Chrome browser accessible")
            
        return True
        
    except Exception as e:
        log(f"❌ Playwright test failed: {e}")
        log("   Try running: playwright install chrome")
        return False

def main():
    """Run all tests"""
    log("=== Poshmark Automation Setup Test ===")
    
    tests = [
        ("Playwright Installation", test_playwright_installation),
        ("Environment Configuration", test_environment),
        ("Browser Access", test_browser_access),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            log(f"Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n=== Test Results ===")
    all_passed = True
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 All tests passed! The automation should work correctly.")
        print(f"   You can now run: python posh_autoredeem.py")
    else:
        print(f"\n⚠️  Some tests failed. Please fix the issues before running the automation.")
        sys.exit(1)

if __name__ == "__main__":
    main()