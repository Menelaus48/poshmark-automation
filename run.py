#!/usr/bin/env python3
"""
Poshmark Automation - Simple Runner Script

This script provides an easy interface to run various automation commands.

Usage:
    python run.py <command>

Commands:
    quick       - Quick credential-based setup (RECOMMENDED)
    check       - Check balance and offer one-click transfer
    setup       - Set up Chrome profile for first time
    profile     - Copy your existing Chrome session to automation
    test        - Test the automation setup
    step        - Step-by-step interactive test
    run         - Run the automation once
    install     - Install daily cron job
    logs        - Show recent logs
    help        - Show this help

Examples:
    python run.py quick      # Credential-based setup (RECOMMENDED)
    python run.py check      # Check balance with one-click transfer
    python run.py run        # Run automation once
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd_list, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(cmd_list, cwd=Path(__file__).parent, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {' '.join(cmd_list)}")
        return False

def setup_profile():
    """Set up Chrome profile"""
    print("🚀 Setting up Chrome profile for Poshmark automation...")
    return run_command([sys.executable, "scripts/setup_profile.py"], "Opening Chrome for profile setup")

def quick_setup():
    """Quick credential-based setup"""
    print("🚀 Quick credential-based setup...")
    return run_command([sys.executable, "scripts/quick_setup.py"], "Setting up credential-based automation")

def check_balance():
    """Check balance and offer transfer"""
    print("💰 Checking balance...")
    return run_command([sys.executable, "scripts/notification_reminder.py"], "Checking balance and offering transfer")

def copy_profile():
    """Copy existing Chrome profile"""
    print("📋 Copying your existing Chrome session...")
    return run_command([sys.executable, "scripts/find_chrome_profile.py"], "Finding and copying Chrome profile")

def test_setup():
    """Test the automation setup"""
    print("🧪 Testing automation setup...")
    return run_command([sys.executable, "scripts/test_setup.py"], "Running setup tests")

def step_by_step_test():
    """Run step-by-step interactive test"""
    print("👣 Running step-by-step test...")
    return run_command([sys.executable, "scripts/step_by_step_test.py"], "Running interactive step test")

def run_automation():
    """Run the automation once"""
    print("⚡ Running Poshmark automation...")
    return run_command([sys.executable, "posh_autoredeem.py"], "Executing balance transfer automation")

def install_cron():
    """Install cron job"""
    print("📅 Installing daily cron job...")
    return run_command(["bash", "scripts/install_cron.sh"], "Setting up cron job")

def show_logs():
    """Show recent logs"""
    log_files = [
        "logs/automation.log",
        "logs/posh_autoredeem.log"
    ]
    
    print("📋 Recent logs:")
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n--- {log_file} (last 20 lines) ---")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
        else:
            print(f"📁 {log_file} - not found")
    
    # Also show recent screenshots
    logs_dir = Path("logs")
    if logs_dir.exists():
        screenshots = sorted(logs_dir.glob("screenshot_*.png"))[-5:]  # Last 5 screenshots
        if screenshots:
            print(f"\n📷 Recent screenshots:")
            for screenshot in screenshots:
                print(f"   {screenshot}")

def show_help():
    """Show help information"""
    print(__doc__)

def main():
    if len(sys.argv) != 2:
        print("❌ Please specify a command")
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'quick': quick_setup,
        'check': check_balance,
        'setup': setup_profile,
        'profile': copy_profile,
        'test': test_setup,
        'step': step_by_step_test,
        'run': run_automation,
        'install': install_cron,
        'logs': show_logs,
        'help': show_help,
    }
    
    if command not in commands:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)
    
    # Make sure we're in the right directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run the command
    success = commands[command]()
    
    if success is False:
        sys.exit(1)
    
    print(f"✅ Command '{command}' completed successfully!")

if __name__ == "__main__":
    main()