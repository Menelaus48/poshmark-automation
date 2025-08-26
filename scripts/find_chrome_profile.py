#!/usr/bin/env python3
"""
Chrome Profile Finder

This script helps you find your Chrome profile directory and copy
your existing Poshmark session to the automation profile.
"""

import os
import shutil
import sqlite3
import json
from pathlib import Path

def find_chrome_profiles():
    """Find all Chrome profile directories on macOS"""
    chrome_base_dirs = [
        os.path.expanduser("~/Library/Application Support/Google/Chrome"),
        os.path.expanduser("~/Library/Application Support/Chrome")
    ]
    
    profiles = []
    
    for base_dir in chrome_base_dirs:
        if not os.path.exists(base_dir):
            continue
            
        print(f"Found Chrome directory: {base_dir}")
        
        # Look for profile directories
        for item in os.listdir(base_dir):
            profile_dir = os.path.join(base_dir, item)
            
            if os.path.isdir(profile_dir) and (item == "Default" or item.startswith("Profile ")):
                # Check if it has cookies (indicates active profile)
                cookies_file = os.path.join(profile_dir, "Cookies")
                if os.path.exists(cookies_file):
                    profiles.append({
                        'name': item,
                        'path': profile_dir,
                        'cookies': cookies_file
                    })
    
    return profiles

def check_poshmark_cookies(cookies_file):
    """Check if profile has Poshmark cookies"""
    try:
        # Copy cookies file temporarily (Chrome locks it)
        temp_cookies = "/tmp/temp_cookies.db"
        shutil.copy2(cookies_file, temp_cookies)
        
        conn = sqlite3.connect(temp_cookies)
        cursor = conn.cursor()
        
        # Look for poshmark.com cookies
        cursor.execute("""
            SELECT name, value, expires_utc 
            FROM cookies 
            WHERE host_key LIKE '%poshmark.com%'
        """)
        
        poshmark_cookies = cursor.fetchall()
        conn.close()
        
        # Clean up
        os.remove(temp_cookies)
        
        return len(poshmark_cookies) > 0, len(poshmark_cookies)
        
    except Exception as e:
        print(f"Error checking cookies: {e}")
        return False, 0

def copy_profile_to_automation(source_profile, dest_dir):
    """Copy Chrome profile to automation directory"""
    print(f"Copying profile from {source_profile} to {dest_dir}...")
    
    # Create destination directory
    os.makedirs(dest_dir, exist_ok=True)
    
    # Important files to copy for session persistence
    files_to_copy = [
        "Cookies",
        "Local Storage",
        "Session Storage", 
        "Preferences",
        "Local State",
        "Login Data",
        "Web Data"
    ]
    
    copied_files = []
    
    for file_name in files_to_copy:
        source_file = os.path.join(source_profile, file_name)
        dest_file = os.path.join(dest_dir, file_name)
        
        try:
            if os.path.exists(source_file):
                if os.path.isdir(source_file):
                    shutil.copytree(source_file, dest_file, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_file, dest_file)
                copied_files.append(file_name)
        except Exception as e:
            print(f"Warning: Could not copy {file_name}: {e}")
    
    return copied_files

def main():
    print("=== Chrome Profile Finder for Poshmark Automation ===\n")
    
    # Find Chrome profiles
    profiles = find_chrome_profiles()
    
    if not profiles:
        print("❌ No Chrome profiles found!")
        print("Make sure Chrome is installed and you've used it before.")
        return
    
    print("Found Chrome profiles:\n")
    
    # Check each profile for Poshmark cookies
    poshmark_profiles = []
    
    for i, profile in enumerate(profiles):
        has_poshmark, cookie_count = check_poshmark_cookies(profile['cookies'])
        
        print(f"{i+1}. {profile['name']}")
        print(f"   Path: {profile['path']}")
        print(f"   Poshmark cookies: {'✅ Yes' if has_poshmark else '❌ No'} ({cookie_count} cookies)")
        
        if has_poshmark:
            poshmark_profiles.append((i, profile))
        print()
    
    if not poshmark_profiles:
        print("❌ No profiles found with Poshmark cookies!")
        print("\nSuggestions:")
        print("1. Make sure you're logged into Poshmark in Chrome")
        print("2. Visit poshmark.com in Chrome to create session cookies")
        print("3. Close Chrome completely and run this script again")
        return
    
    # If multiple profiles with Poshmark, let user choose
    if len(poshmark_profiles) == 1:
        chosen_index, chosen_profile = poshmark_profiles[0]
    else:
        print("Multiple profiles have Poshmark cookies. Which one do you use?")
        for j, (i, profile) in enumerate(poshmark_profiles):
            print(f"{j+1}. {profile['name']}")
        
        choice = input("\nEnter your choice (1-{}): ".format(len(poshmark_profiles)))
        try:
            chosen_index, chosen_profile = poshmark_profiles[int(choice)-1]
        except (ValueError, IndexError):
            print("Invalid choice!")
            return
    
    print(f"\n✅ Selected profile: {chosen_profile['name']}")
    print(f"   Path: {chosen_profile['path']}")
    
    # Copy to automation profile
    automation_profile = os.path.expanduser("~/posh-bot-profile")
    
    confirmation = input(f"\nCopy this profile to automation directory?\n   {automation_profile}\n(y/N): ")
    
    if confirmation.lower() != 'y':
        print("Cancelled.")
        return
    
    # Perform the copy
    copied_files = copy_profile_to_automation(chosen_profile['path'], automation_profile)
    
    print(f"\n✅ Profile copied successfully!")
    print(f"   Copied {len(copied_files)} items: {', '.join(copied_files)}")
    print(f"   Destination: {automation_profile}")
    
    print(f"\n🎉 Your Poshmark session should now work with the automation!")
    print(f"   Test it with: python run.py test")

if __name__ == "__main__":
    main()