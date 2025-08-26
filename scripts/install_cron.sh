#!/bin/bash

# Poshmark Automation - Cron Installation Script
# This script helps you install a daily cron job for the automation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CRON_TIME="5 6 * * *"  # Default: 6:05 AM daily

echo "=== Poshmark Automation - Cron Setup ==="
echo "Project directory: $PROJECT_DIR"

# Check if Python virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_DIR/venv"
    echo "   Please run setup first: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Create wrapper script for cron
WRAPPER_SCRIPT="$PROJECT_DIR/scripts/run_automation.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Poshmark Automation Wrapper Script for Cron
# Generated automatically - do not edit manually

cd "$PROJECT_DIR"
source venv/bin/activate

# Set environment variables
export POSH_USER_DATA_DIR="\$HOME/posh-bot-profile"
export POSH_MIN_TRANSFER="5.00"
export HEADLESS="1"
export LOG_DIR="$PROJECT_DIR/logs"

# Run the automation and log output
python posh_autoredeem.py >> "$PROJECT_DIR/logs/automation.log" 2>&1

# Log completion
echo "\$(date): Automation run completed" >> "$PROJECT_DIR/logs/automation.log"
EOF

chmod +x "$WRAPPER_SCRIPT"
echo "✅ Created wrapper script: $WRAPPER_SCRIPT"

# Create cron entry
CRON_ENTRY="$CRON_TIME $WRAPPER_SCRIPT"

echo ""
echo "=== Cron Job Installation ==="
echo "The following cron entry will be added:"
echo "  $CRON_ENTRY"
echo ""
echo "This means the automation will run:"
echo "  - Daily at 6:05 AM"
echo "  - In headless mode"
echo "  - Logs will be saved to: $PROJECT_DIR/logs/automation.log"
echo ""

read -p "Do you want to install this cron job? (y/N): " -r
if [[ ! \$REPLY =~ ^[Yy]\$ ]]; then
    echo "❌ Cron installation cancelled"
    exit 0
fi

# Backup existing crontab
echo "📋 Backing up existing crontab..."
crontab -l > "$PROJECT_DIR/logs/crontab_backup_\$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true

# Add cron entry
(crontab -l 2>/dev/null || true; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "To verify the installation:"
echo "  crontab -l"
echo ""
echo "To remove the cron job later:"
echo "  crontab -e  # and delete the line containing poshmark-automation"
echo ""
echo "To view logs:"
echo "  tail -f $PROJECT_DIR/logs/automation.log"
echo ""
echo "🎉 Setup complete! The automation will run daily at 6:05 AM."