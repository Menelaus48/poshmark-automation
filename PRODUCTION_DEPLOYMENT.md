# 🚀 Production Deployment Guide

## 🔒 Improved Lock File Strategy

### Current Issue
Lock files are created at start, not at success, causing false "already completed" messages when scripts fail.

### Solution: Process Lock + Success Lock
```python
import fcntl
import tempfile
from pathlib import Path

def create_process_lock():
    """Prevent multiple instances from running simultaneously"""
    lock_file = tempfile.gettempdir() + '/poshmark_automation.lock'
    lock_handle = open(lock_file, 'w')
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_handle
    except IOError:
        log("Another instance is already running")
        sys.exit(9)

def create_success_lock():
    """Mark successful completion only after transfer succeeds"""
    today = date.today().strftime("%Y-%m-%d")
    lock_file = f"{LOG_DIR}/transfer_completed_{today}.lock"
    
    with open(lock_file, 'w') as f:
        f.write(f"Transfer completed successfully on {datetime.now()}\n")
        f.write(f"Amount: ${amount}\n")
        f.write(f"Bank: {bank_details}\n")
```

## 📧 Email Notification System

### Daily Success/Failure Reports
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_daily_report(status, amount=None, error=None, screenshot_path=None):
    """Send daily automation report via email"""
    
    # Email configuration
    smtp_server = "smtp.gmail.com"  # or your email provider
    smtp_port = 587
    sender_email = os.getenv('NOTIFICATION_EMAIL')
    sender_password = os.getenv('EMAIL_APP_PASSWORD')  # Use app password
    recipient = os.getenv('RECIPIENT_EMAIL')
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = f"Poshmark Automation Report - {status.upper()}"
    
    if status == "success":
        body = f"""
        ✅ Poshmark Transfer Successful
        
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Amount Transferred: ${amount}
        Method: Bank Direct Deposit
        Status: Transfer initiated successfully
        
        Next transfer: Tomorrow at 6:05 AM
        """
    else:
        body = f"""
        ❌ Poshmark Transfer Failed
        
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Error: {error}
        
        Action Required:
        1. Check attached screenshot for debugging
        2. Review logs: tail -f /path/to/logs/automation.log
        3. Test manually: HEADLESS=0 python run.py run
        
        The automation will retry tomorrow at 6:05 AM.
        """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach screenshot if available
    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, 'rb') as f:
            img = MIMEMultipart()
            img.attach(MIMEText(f.read(), 'base64'))
            msg.attach(img)
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        log("Email notification sent successfully")
    except Exception as e:
        log(f"Failed to send email: {e}")
```

## 🔍 Advanced Error Intelligence

### Structured Error Reporting
```python
def capture_error_intelligence(page, error_type, exception):
    """Capture comprehensive debugging information"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    intelligence = {
        "timestamp": timestamp,
        "error_type": error_type,
        "exception": str(exception),
        "current_url": page.url,
        "page_title": page.title(),
        "viewport": page.viewport_size,
        "user_agent": page.evaluate("navigator.userAgent"),
        "cookies_count": len(page.context.cookies()),
        "local_storage": page.evaluate("JSON.stringify(localStorage)"),
        "visible_text": page.inner_text("body")[:1000],  # First 1000 chars
        "form_fields": page.evaluate("""
            Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                type: el.type,
                name: el.name,
                placeholder: el.placeholder,
                visible: el.offsetParent !== null
            }))
        """),
        "buttons": page.evaluate("""
            Array.from(document.querySelectorAll('button')).map(el => ({
                text: el.innerText,
                disabled: el.disabled,
                visible: el.offsetParent !== null
            }))
        """)
    }
    
    # Save intelligence report
    intelligence_file = f"{LOG_DIR}/error_intelligence_{timestamp}.json"
    with open(intelligence_file, 'w') as f:
        json.dump(intelligence, f, indent=2)
    
    # Take multiple screenshots
    screenshots = []
    screenshots.append(take_screenshot(page, f"error_fullpage_{timestamp}"))
    
    # Try to scroll and capture more
    page.evaluate("window.scrollTo(0, 0)")
    screenshots.append(take_screenshot(page, f"error_top_{timestamp}"))
    
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  
    screenshots.append(take_screenshot(page, f"error_bottom_{timestamp}"))
    
    return intelligence_file, screenshots
```

## 🤖 Automated Issue Resolution Integration

### Claude Code API Integration (Future Enhancement)
```python
def trigger_claude_debugging(intelligence_file, screenshot_paths):
    """Send error intelligence to Claude Code for automated debugging"""
    
    debugging_context = {
        "project_path": "/path/to/poshmark-automation",
        "error_intelligence": intelligence_file,
        "screenshots": screenshot_paths,
        "task": "Analyze Poshmark automation failure and suggest fixes"
    }
    
    # This would integrate with Claude Code's API when available
    # For now, send detailed email with all debugging info
    
    send_debugging_email(debugging_context)

def send_debugging_email(context):
    """Send comprehensive debugging information via email"""
    subject = "🔧 Poshmark Automation Debug Package"
    
    body = f"""
    Automation failed and requires debugging. Here's the intelligence gathered:
    
    📁 Error Intelligence File: {context['error_intelligence']}
    📸 Screenshots: {len(context['screenshots'])} captured
    
    Next Steps:
    1. Download attached files
    2. Review error_intelligence.json for page state
    3. Examine screenshots for UI changes
    4. Run: HEADLESS=0 python run.py run for live debugging
    
    Common Fixes:
    - UI selectors changed → Update element strategies
    - New modal dialogs → Add to dismiss_modal_dialogs()
    - Login flow changed → Update login selectors
    - Network issues → Check connection, retry later
    """
    
    # Attach all debugging files
    send_email_with_attachments(subject, body, context['screenshots'] + [context['error_intelligence']])
```

## 🗄️ AWS EC2 Production Setup

### System Service (Instead of Cron)
```bash
# Create systemd service for better reliability
sudo nano /etc/systemd/system/poshmark-automation.service
```

```ini
[Unit]
Description=Poshmark Balance Transfer Automation
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/poshmark-automation
Environment=PATH=/home/ubuntu/poshmark-automation/venv/bin
ExecStart=/home/ubuntu/poshmark-automation/venv/bin/python run.py run
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Create timer for daily execution
sudo nano /etc/systemd/system/poshmark-automation.timer
```

```ini
[Unit]
Description=Run Poshmark automation daily
Requires=poshmark-automation.service

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
```

```bash
# Enable and start
sudo systemctl enable poshmark-automation.timer
sudo systemctl start poshmark-automation.timer

# Check status
sudo systemctl status poshmark-automation.timer
```

## 📊 Monitoring Dashboard

### CloudWatch Integration
```python
import boto3

def send_cloudwatch_metrics(status, amount=None, execution_time=None):
    """Send automation metrics to CloudWatch"""
    cloudwatch = boto3.client('cloudwatch')
    
    metrics = [
        {
            'MetricName': 'AutomationSuccess',
            'Value': 1 if status == 'success' else 0,
            'Unit': 'Count'
        }
    ]
    
    if amount:
        metrics.append({
            'MetricName': 'TransferAmount',
            'Value': float(amount),
            'Unit': 'Count'
        })
    
    if execution_time:
        metrics.append({
            'MetricName': 'ExecutionTime',
            'Value': execution_time,
            'Unit': 'Seconds'
        })
    
    cloudwatch.put_metric_data(
        Namespace='PoshmarkAutomation',
        MetricData=metrics
    )
```

## 🎯 Recommended Production Architecture

```
AWS EC2 Instance:
├── Poshmark Automation Service
├── CloudWatch Logging
├── Email Notifications
├── Screenshot Storage (S3)
├── Error Intelligence Reports
├── Daily Health Checks
└── Automated Recovery Attempts
```

This gives you enterprise-grade reliability with proper monitoring, alerting, and debugging capabilities.

Would you like me to help you implement any of these specific components?