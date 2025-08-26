#!/usr/bin/env python3
"""
Poshmark Balance Notification & Quick Run

This script checks if you have a redeemable balance and gives you
a one-click option to transfer it.

Usage:
    python scripts/notification_reminder.py
"""

import os
import sys
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import re
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from posh_autoredeem import (
    USER_DATA_DIR, LOG_DIR, POSH_EMAIL, POSH_PASS, MIN_TRANSFER,
    log, take_screenshot, wait_for_page_load, parse_money
)

def send_notification(title, message):
    """Send macOS notification"""
    try:
        cmd = f'osascript -e \'display notification "{message}" with title "{title}"\''
        subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        print(f"Notification failed: {e}")

def check_balance_only():
    """Check balance without transferring"""
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=True,  # Always headless for balance check
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
            log("Checking Poshmark balance...")
            page.goto("https://poshmark.com/account/payout-options", timeout=60000)
            
            if not wait_for_page_load(page):
                raise Exception("Page failed to load")
            
            # Check if login is needed
            current_url = page.url.lower()
            if "login" in current_url:
                if not POSH_EMAIL or not POSH_PASS:
                    log("ERROR: Login required but no credentials provided")
                    return None, "LOGIN_REQUIRED"
                
                # Attempt login
                log("Logging in...")
                try:
                    page.get_by_label(re.compile("email", re.I)).fill(POSH_EMAIL)
                    page.get_by_label(re.compile("password", re.I)).fill(POSH_PASS)
                    page.get_by_role("button", name=re.compile("log in|sign in", re.I)).click()
                    
                    if not wait_for_page_load(page):
                        return None, "LOGIN_FAILED"
                        
                    # Navigate back to payout page after login
                    page.goto("https://poshmark.com/account/payout-options", timeout=60000)
                    wait_for_page_load(page)
                    
                except Exception as e:
                    log(f"Login failed: {e}")
                    return None, "LOGIN_FAILED"
            
            # Check for balance
            page_text = page.content()
            balance = parse_money(page_text)
            
            if balance is None:
                return 0.0, "NO_BALANCE_DETECTED"
            
            return balance, "SUCCESS"
            
        except Exception as e:
            log(f"Error checking balance: {e}")
            return None, "ERROR"
            
        finally:
            context.close()

def main():
    print("=== Poshmark Balance Checker ===")
    
    # Check balance
    balance, status = check_balance_only()
    
    if status == "LOGIN_REQUIRED":
        print("❌ Login required but no credentials set")
        print("Please set POSH_EMAIL and POSH_PASS in your .env file")
        return
    
    if status == "LOGIN_FAILED":
        print("❌ Login failed - check your credentials")
        send_notification("Poshmark Balance Check", "Login failed - check credentials")
        return
    
    if status == "ERROR" or balance is None:
        print("❌ Error checking balance")
        send_notification("Poshmark Balance Check", "Error checking balance")
        return
    
    if balance < MIN_TRANSFER:
        print(f"💰 Balance: ${balance:.2f} (below ${MIN_TRANSFER:.2f} threshold)")
        log(f"Balance ${balance:.2f} below threshold - no action needed")
        return
    
    # Balance is above threshold!
    print(f"💰 Balance Available: ${balance:.2f}")
    print(f"💰 Above threshold: ${MIN_TRANSFER:.2f}")
    
    # Send notification
    send_notification(
        "Poshmark Balance Available!", 
        f"${balance:.2f} ready to transfer"
    )
    
    # Offer quick transfer
    print("\n🚀 Ready to transfer?")
    print("1. Yes - Transfer now")
    print("2. No - Just remind me later")
    print("3. Show me the page first")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("🚀 Starting transfer...")
        # Run the main automation
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent.parent / "posh_autoredeem.py")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Transfer completed successfully!")
            send_notification("Poshmark Transfer", f"${balance:.2f} transfer completed!")
        else:
            print("❌ Transfer failed - check logs")
            send_notification("Poshmark Transfer", "Transfer failed - check logs")
        
    elif choice == "3":
        print("🌐 Opening Poshmark payout page...")
        subprocess.run(["open", "https://poshmark.com/account/payout-options"])
        print("You can transfer manually or run: python run.py run")
        
    else:
        print("👍 Reminder noted - no action taken")

if __name__ == "__main__":
    main()