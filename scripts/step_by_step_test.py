#!/usr/bin/env python3
"""
Step-by-Step Poshmark Automation Tester

This script walks through each step of the automation process,
pausing for your confirmation at each stage.
"""

from playwright.sync_api import sync_playwright
import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from posh_autoredeem import (
    USER_DATA_DIR, LOG_DIR, 
    log, take_screenshot, wait_for_page_load, 
    check_for_captcha_or_verification, parse_money
)

def wait_for_user(message):
    """Pause and wait for user confirmation"""
    input(f"\n👀 {message}\nPress Enter to continue...")

def main():
    print("=== Step-by-Step Poshmark Automation Test ===")
    print("This will walk through each automation step with your confirmation.")
    print("The browser will stay visible so you can see what's happening.\n")
    
    wait_for_user("Ready to start? Make sure Chrome is closed first.")
    
    with sync_playwright() as p:
        # Launch with visible browser
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
        
        try:
            # Step 1: Navigate to payout options
            log("STEP 1: Navigating to Poshmark payout options...")
            page.goto("https://poshmark.com/account/payout-options", timeout=60000)
            
            wait_for_user("STEP 1 CHECK: Can you see the Poshmark payout options page? Are you logged in?")
            
            if not wait_for_page_load(page):
                raise Exception("Page failed to load properly")
            
            # Check login status
            current_url = page.url.lower()
            if "login" in current_url:
                log("❌ Not logged in - you'll need to login manually")
                wait_for_user("Please login in the browser window, then continue")
                
                # Wait for redirect after login
                page.wait_for_url("**/account/payout-options", timeout=120000)
                log("✅ Login detected, continuing...")
            
            # Check for security challenges
            if check_for_captcha_or_verification(page):
                log("⚠️ Security challenge detected")
                wait_for_user("Please complete any security challenges in the browser, then continue")
            
            # Step 2: Take screenshot and analyze page
            log("STEP 2: Taking screenshot of payout options...")
            screenshot1 = take_screenshot(page, "step1_payout_options")
            
            # Check for balance
            page_text = page.content()
            balance = parse_money(page_text)
            if balance:
                log(f"💰 Detected balance: ${balance:.2f}")
            else:
                log("⚠️ No balance detected (may be $0 or hidden)")
            
            wait_for_user(f"STEP 2 CHECK: Screenshot saved to {screenshot1}. Can you see the payout methods?")
            
            # Step 3: Find Bank Direct Deposit radio button
            log("STEP 3: Looking for Bank Direct Deposit option...")
            
            # Try to find the radio button
            direct_deposit_found = False
            radio_button = None
            
            selectors_to_try = [
                ('Text-based', lambda: page.get_by_text("Bank Direct Deposit").locator("xpath=ancestor-or-self::label").locator("input[type='radio']")),
                ('Label selector', lambda: page.locator("label:has-text('Bank Direct Deposit') input[type='radio']")),
                ('No fee finder', lambda: page.get_by_text("No fee").locator("xpath=ancestor::*").locator("input[type='radio']").first),
            ]
            
            for name, selector in selectors_to_try:
                try:
                    radio_button = selector()
                    if radio_button.count() > 0:
                        log(f"✅ Found Bank Direct Deposit using {name}")
                        # Highlight the element
                        radio_button.first.highlight()
                        direct_deposit_found = True
                        break
                except Exception as e:
                    log(f"❌ {name} failed: {e}")
            
            if not direct_deposit_found:
                log("❌ Could not find Bank Direct Deposit radio button")
                wait_for_user("STEP 3 PROBLEM: Can you see the Bank Direct Deposit option? Check the browser.")
                context.close()
                return
            
            wait_for_user("STEP 3 CHECK: Is the Bank Direct Deposit option highlighted? Ready to select it?")
            
            # Step 4: Select the radio button
            log("STEP 4: Selecting Bank Direct Deposit...")
            radio_button.first.check()
            time.sleep(1)  # Brief pause
            
            wait_for_user("STEP 4 CHECK: Is Bank Direct Deposit selected? Is the Continue button now clickable?")
            
            # Step 5: Find Continue button
            log("STEP 5: Looking for Continue button...")
            
            continue_button = None
            continue_selectors = [
                ('Primary Continue', lambda: page.locator('button.btn.btn--primary:has-text("Continue")')),
                ('Generic Continue', lambda: page.get_by_role("button", name="Continue")),
                ('Text-based Continue', lambda: page.locator("button").filter(has_text="Continue")),
            ]
            
            for name, selector in continue_selectors:
                try:
                    continue_button = selector()
                    if continue_button.count() > 0:
                        log(f"✅ Found Continue button using {name}")
                        continue_button.first.highlight()
                        break
                except Exception as e:
                    log(f"❌ {name} failed: {e}")
            
            if not continue_button or continue_button.count() == 0:
                log("❌ Could not find Continue button")
                wait_for_user("STEP 5 PROBLEM: Can you see the Continue button? Is it enabled?")
                context.close()
                return
            
            wait_for_user("STEP 5 CHECK: Is the Continue button highlighted and clickable?")
            
            # Step 6: Click Continue
            log("STEP 6: Clicking Continue button...")
            continue_button.first.click()
            
            wait_for_user("STEP 6 CHECK: Did clicking Continue work? Should be loading the confirmation page...")
            
            # Step 7: Wait for confirmation page
            log("STEP 7: Waiting for confirmation page...")
            if not wait_for_page_load(page, timeout=30000):
                log("⚠️ Page load timeout, but continuing...")
            
            current_url = page.url
            log(f"Current URL: {current_url}")
            
            screenshot2 = take_screenshot(page, "step2_confirmation_page")
            
            wait_for_user(f"STEP 7 CHECK: Are you on the confirmation page? Screenshot: {screenshot2}")
            
            # Step 8: Find final Redeem button
            log("STEP 8: Looking for final Redeem button...")
            
            redeem_button = None
            redeem_selectors = [
                ('Exact match', lambda: page.locator('button[data-et-name="confirm_redeem"][data-et-prop-content="ach"].btn.btn--primary')),
                ('Primary Redeem', lambda: page.locator('button.btn--primary:has-text("Redeem")')),
                ('Generic Redeem', lambda: page.get_by_role("button", name="Redeem")),
                ('Text-based Redeem', lambda: page.locator("button").filter(has_text="Redeem")),
            ]
            
            for name, selector in redeem_selectors:
                try:
                    redeem_button = selector()
                    if redeem_button.count() > 0:
                        log(f"✅ Found Redeem button using {name}")
                        redeem_button.first.highlight()
                        break
                except Exception as e:
                    log(f"❌ {name} failed: {e}")
            
            if not redeem_button or redeem_button.count() == 0:
                log("❌ Could not find final Redeem button")
                wait_for_user("STEP 8 PROBLEM: Can you see the final Redeem button?")
                context.close()
                return
            
            wait_for_user("STEP 8 CHECK: Is the final Redeem button highlighted? Ready to complete the transfer?")
            
            # Step 9: Final confirmation before clicking
            final_confirm = input("\n🚨 FINAL CONFIRMATION: This will actually initiate a real money transfer!\n   Type 'YES' to proceed with the actual transfer, or anything else to stop: ")
            
            if final_confirm != "YES":
                log("❌ Transfer cancelled by user")
                log("✅ Test completed successfully - all steps work until final transfer")
                context.close()
                return
            
            # Step 10: Click final Redeem button
            log("STEP 9: Clicking final Redeem button...")
            redeem_button.first.click()
            
            # Step 11: Wait and check results
            log("STEP 10: Waiting for confirmation...")
            time.sleep(5)
            
            final_screenshot = take_screenshot(page, "step3_final_result")
            
            # Check for success indicators
            page_text = page.content().lower()
            success_found = any(word in page_text for word in ['success', 'complete', 'initiated', 'processing', 'confirmed'])
            
            if success_found:
                log("✅ SUCCESS: Transfer appears to have been initiated!")
            else:
                log("⚠️ UNCLEAR: No clear success indicators found")
            
            wait_for_user(f"FINAL CHECK: Did the transfer complete successfully? Screenshot: {final_screenshot}")
            
            log("🎉 Step-by-step test completed!")
            
        except Exception as e:
            log(f"❌ ERROR during testing: {e}")
            error_screenshot = take_screenshot(page, "step_error")
            log(f"Error screenshot: {error_screenshot}")
            
        finally:
            wait_for_user("Test finished. Press Enter to close the browser...")
            context.close()

if __name__ == "__main__":
    main()