# Poshmark Balance Auto-Transfer Automation

Automatically transfer your daily Poshmark seller balance to your bank account using Playwright browser automation.

## ⚠️ Important Disclaimers

- **Terms of Service**: This automation may violate Poshmark's Terms of Service. Use at your own risk.
- **Account Safety**: Automation can trigger security reviews or account holds. Monitor your account.
- **No Warranty**: This software is provided as-is without any warranty or guarantee.
- **Security**: Never share your login credentials or browser profile with others.

## ✨ Features

- **Daily Automation**: Runs automatically via cron job
- **Smart Balance Detection**: Multiple strategies to find your redeemable balance
- **Persistent Sessions**: Uses dedicated Chrome profile to avoid repeated logins
- **Security Handling**: Detects and handles 2FA/CAPTCHA challenges gracefully
- **Comprehensive Logging**: Screenshots and logs for debugging
- **Idempotency**: Prevents multiple transfers per day
- **Configurable Thresholds**: Only transfer when balance exceeds your minimum

## 🚀 Quick Start

### 1. Initial Setup

```bash
cd /Users/peteralfieri/Projects/poshmark-automation

# Activate virtual environment
source venv/bin/activate

# Set up Chrome profile (first time only)
python run.py setup
```

This will open Chrome where you should:
- Login to your Poshmark account
- Complete any 2FA if required
- Navigate to your Balance page
- Close Chrome when done

### 2. Test the Setup

```bash
python run.py test
```

This verifies everything is working correctly.

### 3. Run Once Manually

```bash
python run.py run
```

Test the automation manually before scheduling.

### 4. Install Daily Automation

```bash
python run.py install
```

This sets up a cron job to run daily at 6:05 AM.

## 📋 Requirements

- **macOS** (tested on macOS Sonoma+)
- **Python 3.7+**
- **Google Chrome** (installed in Applications)
- **Playwright** (installed via pip)

## 📁 Project Structure

```
poshmark-automation/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── posh_autoredeem.py    # Main automation script
├── run.py                # Easy command runner
├── .env.example          # Environment variables template
├── logs/                 # Screenshots and logs
├── scripts/
│   ├── setup_profile.py  # Chrome profile setup
│   ├── test_setup.py     # Test automation setup
│   └── install_cron.sh   # Cron job installer
└── venv/                 # Python virtual environment
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Minimum balance to transfer (default: $5.00)
POSH_MIN_TRANSFER=5.00

# Run mode: 0=visible browser, 1=headless (default: 0)
HEADLESS=0

# Chrome profile location
POSH_USER_DATA_DIR=~/posh-bot-profile

# Optional: Login credentials (only if session expires)
# POSH_EMAIL=your_email@example.com
# POSH_PASS=your_password
```

### Scheduling

The automation runs daily at 6:05 AM via cron. To customize the time:

```bash
# Edit cron jobs
crontab -e

# Change the time (example: 7:30 AM)
30 7 * * * /Users/peteralfieri/Projects/poshmark-automation/scripts/run_automation.sh
```

## 📊 Monitoring

### View Logs

```bash
# Show recent logs and screenshots
python run.py logs

# Or directly view the log file
tail -f logs/automation.log
```

### Screenshots

The automation takes screenshots at key steps:
- `screenshot_*_test_access.png` - Test runs
- `screenshot_*_transfer_completed.png` - Successful transfers
- `screenshot_*_error.png` - When errors occur

## 🔧 Troubleshooting

### Common Issues

**"Login required" errors:**
- The automation uses placeholder-based selectors (`Username or Email`, `Password`)
- Run `HEADLESS=0 python run.py run` to see the login process
- Check if 2FA or security challenge is required
- Verify credentials in `.env` file

**"Balance not found" errors:**
- Balance detection uses multiple strategies and fallbacks
- Check screenshots in `logs/` folder for UI changes
- The script handles both visible balance and actual transfer amounts

**"Modal dialog" issues:**
- The automation handles 8+ types of modal dialogs automatically
- Common modals: "Got it!", "OK", "Close", "Guide for Entering Bank Details"
- If new modals appear, they'll be logged and the automation will attempt to dismiss

**"Continue button not working":**
- Usually indicates Bank Direct Deposit account not set up
- Check screenshot for error messages
- Ensure your bank account is configured in Poshmark settings

**Cron job not running:**
- Verify with `crontab -l`
- Check system logs: `tail -f /var/log/system.log | grep cron`
- Ensure paths are absolute in cron script

**Browser crashes or timeouts:**
- Run with `HEADLESS=0` to see what's happening
- The automation waits for loading spinners to disappear
- Check Chrome is updated to latest version
- Clear the profile: `rm -rf ~/posh-bot-profile` and re-setup

### Debug Mode

Run the automation with a visible browser to debug:

```bash
HEADLESS=0 python posh_autoredeem.py
```

### Updating Selectors

If Poshmark changes their UI, you may need to update element selectors in `posh_autoredeem.py`. Look for these sections:

```python
# Balance detection strategies
strategies = [
    lambda: page.get_by_text(re.compile("redeemable", re.I)).first,
    # Add new strategies here
]

# Button selectors
redeem_selectors = [
    lambda: page.get_by_role("button", name=re.compile("redeem", re.I)),
    # Add new selectors here
]
```

## 🛡️ Security Best Practices

1. **Use a Dedicated Profile**: Never use the automation profile for regular browsing
2. **Monitor Your Account**: Check for unusual activity regularly
3. **Secure Your Environment**: Don't store passwords in plain text
4. **Network Security**: Run from your home network with consistent IP
5. **Account Recovery**: Keep recovery options updated in case of issues

## 📜 Legal and Ethical Considerations

- This automation is for personal use only
- You are responsible for compliance with Poshmark's Terms of Service
- Consider the impact on Poshmark's systems and use reasonably
- Be prepared to handle account security reviews
- Keep your automation behavior human-like (daily frequency, normal hours)

## 🆘 Getting Help

1. **Check Logs**: `python run.py logs`
2. **Test Setup**: `python run.py test`
3. **Review Screenshots**: Look in `logs/` folder
4. **Run Manually**: `HEADLESS=0 python run.py run`
5. **Update Profile**: `python run.py setup`

## 🔄 Maintenance

### Regular Tasks

- **Weekly**: Check that automation is still running (`python run.py logs`)
- **Monthly**: Update Chrome and test the automation manually
- **Quarterly**: Refresh the browser profile if needed

### Updates

```bash
cd /Users/peteralfieri/Projects/poshmark-automation
source venv/bin/activate
pip install --upgrade playwright
playwright install chrome
```

## 📈 Future Enhancements

Potential improvements (not currently implemented):
- Slack/email notifications
- Multiple account support
- Balance history tracking
- Retry logic for failed transfers
- Mobile app automation
- OCR-based fallback for balance detection

---

**Happy Automating! 🤖💰**

*Remember: With great automation comes great responsibility. Use wisely!*