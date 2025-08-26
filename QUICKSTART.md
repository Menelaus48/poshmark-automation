# 🚀 Poshmark Automation - Quick Start Guide

Get your Poshmark balance transfers automated in 5 minutes!

## Step 1: Navigate to Project

```bash
cd /Users/peteralfieri/Projects/poshmark-automation
```

## Step 2: Activate Environment

```bash
source venv/bin/activate
```

## Step 3: Set Up Browser Profile

```bash
python run.py setup
```

**In the Chrome window that opens:**
1. Login to Poshmark
2. Complete any 2FA
3. Go to Balance page
4. Close Chrome

## Step 4: Test Everything Works

```bash
python run.py test
```

Should show all tests passing ✅

## Step 5: Test Manual Run

```bash
python run.py run
```

This will run the automation once to verify it works.

## Step 6: Install Daily Automation

```bash
python run.py install
```

**Done!** 🎉 

Your Poshmark balance will automatically transfer daily at 6:05 AM.

## Quick Commands

```bash
python run.py logs    # View recent activity
python run.py test    # Re-test setup
python run.py setup   # Refresh browser profile
```

## Troubleshooting

**Not working?**
1. Run `python run.py test`
2. Check `python run.py logs`
3. Try `HEADLESS=0 python run.py run` to see browser

**Need to change time?**
```bash
crontab -e
# Change: 5 6 * * * (6:05 AM) to your preferred time
```

**Stop automation:**
```bash
crontab -e
# Delete the line containing poshmark-automation
```

---
**That's it!** Check the full README.md for advanced configuration.