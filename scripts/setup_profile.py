#!/usr/bin/env python3
"""
Setup Script for Poshmark Automation Browser Profile

This script helps set up a dedicated Chrome profile for the Poshmark automation.
Run this once to create the profile and login manually.

Usage:
    python scripts/setup_profile.py

This will:
1. Create a dedicated Chrome profile directory
2. Launch Chrome with that profile
3. Navigate to Poshmark login page
4. Allow you to login manually and complete any 2FA
5. Save the session for automated use
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Configuration
    profile_dir = os.path.expanduser("~/posh-bot-profile")
    poshmark_url = "https://poshmark.com/balance"
    
    print("=== Poshmark Automation Profile Setup ===")
    print(f"Creating dedicated Chrome profile at: {profile_dir}")
    
    # Create profile directory
    os.makedirs(profile_dir, exist_ok=True)
    
    # Determine Chrome executable path on macOS
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chrome.app/Contents/MacOS/Chrome",  # Alternative location
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        print("ERROR: Chrome not found in standard locations.")
        print("Please install Google Chrome or update the chrome_paths in this script.")
        sys.exit(1)
    
    print(f"Found Chrome at: {chrome_exe}")
    
    # Launch Chrome with dedicated profile
    chrome_args = [
        chrome_exe,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        poshmark_url
    ]
    
    print("\n🚀 Launching Chrome with dedicated profile...")
    print("📝 Please complete the following steps in the Chrome window that opens:")
    print("   1. Login to your Poshmark account")
    print("   2. Complete any 2FA if required")
    print("   3. Navigate to the Balance page if not already there")
    print("   4. Verify you can see your balance information")
    print("   5. Close Chrome when done")
    print("\n⚠️  IMPORTANT: Do not use this Chrome profile for regular browsing!")
    print("   This profile should only be used for the automation.")
    
    try:
        # Launch Chrome and wait for it to close
        process = subprocess.Popen(chrome_args)
        print(f"\n✅ Chrome launched with PID: {process.pid}")
        print("   Waiting for you to complete setup... (close Chrome when done)")
        
        # Wait for Chrome to close
        process.wait()
        
        print("\n✅ Setup completed!")
        print("   Your session has been saved to the dedicated profile.")
        print("   The automation script can now use this profile for unattended runs.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error launching Chrome: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()