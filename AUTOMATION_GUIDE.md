# 🤖 Poshmark Automation - Senior Developer's Guide

## 🎯 **The Problem**
Manual daily balance transfers from Poshmark to bank account. Time-consuming, easy to forget, no native automation available.

## 💡 **The Solution**
Playwright-based browser automation with multiple deployment strategies optimized for reliability and minimal maintenance.

---

## 🏗️ **Architecture Overview**

### **Core Components**
```
poshmark-automation/
├── posh_autoredeem.py          # Main automation engine
├── run.py                      # CLI interface
├── poshmark                    # Shell launcher
├── requirements.txt            # Python dependencies
├── .env.example               # Configuration template
├── scripts/
│   ├── quick_setup.py         # Credential-based setup
│   ├── notification_reminder.py # Balance checker + one-click transfer
│   ├── step_by_step_test.py   # Interactive testing
│   ├── find_chrome_profile.py # Session migration tool
│   └── install_cron.sh        # Cron job installer
└── logs/                      # Screenshots + logs
```

### **Technology Stack**
- **Browser Automation**: Playwright (Chrome channel)
- **Language**: Python 3.9+
- **Session Persistence**: Chrome profile isolation
- **Configuration**: python-dotenv
- **Scheduling**: macOS cron
- **Notifications**: macOS native notifications

---

## 🚀 **Deployment Strategies**

### **Strategy 1: Credential-Based Headless (Recommended for Seniors)**

**Best for**: Set-it-and-forget-it automation

```bash
# One-time setup (60 seconds)
python run.py quick

# Install daily automation
python run.py install

# Monitor with logs
tail -f logs/automation.log
```

**Pros**:
- Zero daily friction
- Runs in background
- No browser interference
- Handles login automatically

**Cons**:
- Stores credentials in file
- May hit CAPTCHA occasionally

**CAPTCHA Handling**:
- Script detects challenge, stops gracefully
- Takes screenshot, logs event
- Sends notification to resolve
- Next run works after manual resolution

---

### **Strategy 2: Session-Based Profile Copy**

**Best for**: Maximum security, minimal CAPTCHA risk

```bash
# Copy existing Chrome session
python run.py profile

# Test with visible browser
HEADLESS=0 python run.py run

# Install automation
python run.py install
```

**Pros**:
- Uses existing session trust
- Minimal CAPTCHA risk
- No credential storage

**Cons**:
- Initial setup more complex
- Session may expire

---

### **Strategy 3: Interactive Balance Checker**

**Best for**: Manual control with automation assist

```bash
# Check balance when convenient
python run.py check

# One-click transfer when ready
# (Prompts: 1=Transfer, 2=Remind Later, 3=Show Page)
```

**Pros**:
- Full control over transfers
- Safe testing
- No unattended automation

**Cons**:
- Requires daily interaction

---

## ⚙️ **Automation Cadence & Best Practices**

### **Cron Job Configuration**

**Default Schedule**: Daily at 6:05 AM
```bash
5 6 * * * /Users/username/Projects/poshmark-automation/scripts/run_automation.sh
```

**Why 6:05 AM?**
- After daily Poshmark processing (typically midnight-6am)
- Before business hours
- Consistent timing reduces bot detection
- Allows time for manual resolution if issues arise

**Alternative Schedules**:
```bash
# Weekdays only
5 6 * * 1-5 /path/to/run_automation.sh

# Multiple times (if first fails)
5 6 * * * /path/to/run_automation.sh
5 12 * * * /path/to/run_automation.sh

# Check balance only (no auto-transfer)
0 6 * * * /path/to/check_balance_only.sh
```

### **Senior Developer Best Practices**

#### **1. Environment Isolation**
```bash
# Dedicated virtual environment
python3 -m venv venv
source venv/bin/activate

# Locked dependencies
pip install -r requirements.txt
```

#### **2. Configuration Management**
```bash
# Environment-specific configs
cp .env.example .env.production
cp .env.example .env.development

# Secure credential storage
chmod 600 .env*
```

#### **3. Monitoring & Observability**
```bash
# Log rotation
logrotate -f /etc/logrotate.d/poshmark-automation

# Health checks
*/15 * * * * /path/to/health_check.sh

# Notification channels
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export NOTIFICATION_EMAIL="alerts@yourcompany.com"
```

#### **4. Error Handling & Recovery**
```python
# Built-in features:
- Daily lock files (prevents double-transfers)
- Screenshot capture on errors
- Graceful CAPTCHA detection
- Automatic retry logic
- Session persistence
```

#### **5. Security Considerations**
```bash
# File permissions
chmod 600 .env
chmod 700 ~/posh-bot-profile/

# Credential rotation
# Update credentials quarterly

# Network security
# Run from trusted home network
# Consider VPN for consistency
```

---

## 🔧 **Maintenance & Operations**

### **Regular Tasks**
- **Weekly**: Check automation.log for issues
- **Monthly**: Test manual run, update Chrome if needed
- **Quarterly**: Rotate credentials, verify balance thresholds

### **Troubleshooting Runbook**

#### **Common Issues**

1. **Login failures**
   ```bash
   # Check credentials
   grep POSH_EMAIL .env
   
   # Test login manually
   HEADLESS=0 python run.py run
   ```

2. **CAPTCHA challenges**
   ```bash
   # Check for security screenshots
   ls logs/screenshot_*security*
   
   # Resolve manually
   open -a "Google Chrome" --args --user-data-dir="$HOME/posh-bot-profile"
   ```

3. **Element not found**
   ```bash
   # Poshmark UI changed
   python run.py step  # Test each element
   
   # Update selectors in posh_autoredeem.py
   ```

4. **Cron not running**
   ```bash
   # Check cron service
   sudo launchctl list | grep cron
   
   # Verify cron entry
   crontab -l | grep poshmark
   
   # Check logs
   grep CRON /var/log/system.log
   ```

### **Performance Monitoring**

```bash
# Automation success rate
grep -c "Transfer initiated successfully" logs/automation.log

# Average execution time
grep "Transfer completed" logs/automation.log | awk '{print $2}'

# Error patterns
grep ERROR logs/automation.log | sort | uniq -c
```

---

## 🎯 **Production Deployment Checklist**

### **Initial Setup**
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Configure `.env` file
- [ ] Test with `python run.py step`
- [ ] Verify balance detection
- [ ] Test transfer (small amount)

### **Automation Setup**
- [ ] Install cron job
- [ ] Test cron execution
- [ ] Configure notifications
- [ ] Set up log rotation
- [ ] Document credentials securely

### **Security Review**
- [ ] File permissions (600 for .env)
- [ ] Profile isolation verified
- [ ] Network considerations documented
- [ ] Backup & recovery plan
- [ ] Monitoring alerts configured

---

## 🔄 **Advanced Configurations**

### **Multiple Account Support**
```bash
# Separate profiles per account
POSH_USER_DATA_DIR_ACCOUNT1=~/posh-bot-profile-account1
POSH_USER_DATA_DIR_ACCOUNT2=~/posh-bot-profile-account2

# Separate cron jobs
5 6 * * * cd /path/to/automation && ACCOUNT=1 python run.py run
10 6 * * * cd /path/to/automation && ACCOUNT=2 python run.py run
```

### **Notification Integrations**
```python
# Slack integration
def send_slack_notification(message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    payload = {'text': f'Poshmark Automation: {message}'}
    requests.post(webhook_url, json=payload)

# Email integration
def send_email_notification(subject, body):
    # Implementation with smtplib
    pass
```

### **Database Logging**
```python
# Track transfer history
import sqlite3
conn = sqlite3.connect('transfer_history.db')
cursor.execute("""
    INSERT INTO transfers (date, amount, status, screenshot_path)
    VALUES (?, ?, ?, ?)
""", (datetime.now(), balance, 'success', screenshot_path))
```

---

## 📊 **Success Metrics**

- **Reliability**: >95% successful transfers
- **Speed**: <2 minutes execution time
- **Maintenance**: <1 hour per month
- **Recovery**: <15 minutes to resolve CAPTCHA
- **Security**: Zero credential exposures

---

This automation represents a production-ready solution for a recurring business process, built with senior developer standards for reliability, maintainability, and security.