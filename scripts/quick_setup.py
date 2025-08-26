#!/usr/bin/env python3
"""
Quick Setup for Credential-Based Automation

This sets up the lowest-friction automation approach:
- Uses your credentials stored in .env file
- Runs headless by default
- Handles CAPTCHA gracefully when it happens
"""

import os
import getpass
from pathlib import Path

def main():
    print("=== Quick Setup: Credential-Based Automation ===")
    print("This setup uses your login credentials for fully automated transfers.")
    print("Pros: Zero friction, runs in background, no browser interference")
    print("Cons: Stores credentials in file, may hit CAPTCHA occasionally\n")
    
    # Get project directory
    project_dir = Path(__file__).parent.parent
    env_file = project_dir / ".env"
    
    print(f"Setting up: {env_file}")
    
    # Get credentials
    print("\n🔐 Enter your Poshmark credentials:")
    email = input("Email: ").strip()
    
    # Hide password input
    password = getpass.getpass("Password: ")
    
    # Get minimum transfer amount
    min_transfer = input(f"\nMinimum transfer amount (default $5.00): ").strip()
    if not min_transfer:
        min_transfer = "5.00"
    
    # Create .env file
    env_content = f"""# Poshmark Automation Configuration
# SECURITY: Keep this file private - contains your login credentials

# Your Poshmark login credentials
POSH_EMAIL={email}
POSH_PASS={password}

# Chrome profile directory (separate from your daily browsing)
POSH_USER_DATA_DIR=~/posh-bot-profile

# Minimum balance to trigger transfer
POSH_MIN_TRANSFER={min_transfer}

# Run in headless mode (1=background, 0=visible)
HEADLESS=1

# Directory for logs and screenshots
LOG_DIR=./logs

# Optional: Notification settings
# NOTIFICATION_EMAIL=your_email@example.com
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
"""
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Set proper permissions (readable only by user)
    os.chmod(env_file, 0o600)
    
    print(f"\n✅ Configuration saved to: {env_file}")
    print("📁 File permissions set to user-only read/write")
    
    # Test the setup
    print("\n🧪 Testing the setup...")
    
    try:
        # Test that we can load the environment
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        test_email = os.getenv("POSH_EMAIL")
        if test_email == email:
            print("✅ Environment variables loaded correctly")
        else:
            print("⚠️  Environment loading issue")
            
    except ImportError:
        print("📦 Installing python-dotenv for environment variables...")
        import subprocess
        subprocess.run(["pip", "install", "python-dotenv"], check=True)
        print("✅ python-dotenv installed")
    
    print(f"\n🎉 Quick setup complete!")
    print(f"\nNext steps:")
    print(f"1. Test: python run.py test")
    print(f"2. Run once: python run.py run")
    print(f"3. Check balance: python scripts/notification_reminder.py")
    print(f"4. Install daily automation: python run.py install")
    
    print(f"\n🔒 Security Notes:")
    print(f"- Your credentials are stored in {env_file}")
    print(f"- File is set to user-only permissions")
    print(f"- Never share this file or commit it to version control")
    print(f"- If you get CAPTCHA challenges, the script will notify you")

if __name__ == "__main__":
    main()