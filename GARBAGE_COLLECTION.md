# 🗑️ Garbage Collection Strategy

## 📋 **Overview**

The automation system includes intelligent garbage collection to prevent unlimited log/screenshot accumulation while preserving debugging capabilities.

## 🧠 **Retention Logic (Intelligence-Based)**

### **File Categories & Retention:**

```python
ERROR_SCREENSHOTS:     30 days    # High debugging value - keep longer
SUCCESS_SCREENSHOTS:   10 count   # Proof only - keep recent few
OTHER_SCREENSHOTS:     7 days     # General debugging - moderate retention  
LOG_FILES:            30 days     # Text logs are small - keep longer
LOCK_FILES:           7 days      # Should only exist for current day
```

### **Why This Logic:**

1. **Error Screenshots (30 days)**:
   - **High debugging value** when automation fails
   - Help identify UI changes, CAPTCHA challenges, network issues
   - Essential for troubleshooting and updating selectors
   - Examples: `screenshot_*error*.png`, `*failed*.png`, `*not_found*.png`

2. **Success Screenshots (10 count)**:
   - **Low debugging value** - just proof transfers worked
   - Keep 10 most recent for audit trails
   - Beyond 10, they're redundant (all look the same)
   - Examples: `screenshot_*completed*.png`, `*success*.png`

3. **Other Screenshots (7 days)**:
   - **Moderate debugging value** - page state captures
   - Help understand automation flow
   - Examples: `payout_options_page.png`, `confirmation_page.png`

4. **Log Files (30 days)**:
   - **Small size, high value** - text logs take minimal space
   - Essential for debugging patterns and performance analysis
   - Examples: `automation.log`, `posh_autoredeem.log`

5. **Lock Files (7 days)**:
   - **Should only exist for current day** - anything older is stale
   - Examples: `transfer_completed_2025-08-26.lock`

## 🏗️ **Architecture Approaches**

### **Option 1: Integrated Cleanup (✅ IMPLEMENTED)**

```python
# In posh_autoredeem.py main():
cleanup_old_logs()  # Runs every time automation runs
```

**Pros:**
- ✅ **Automatic** - happens every automation run
- ✅ **Lightweight** - minimal performance impact (~100ms)
- ✅ **No dependencies** - uses only standard library
- ✅ **Fail-safe** - cleanup failures don't break automation

**Cons:**
- ❌ **Limited features** - basic cleanup only
- ❌ **Fixed schedule** - only runs when automation runs

### **Option 2: Standalone Cleanup Script (✅ ALSO AVAILABLE)**

```bash
python run.py cleanup        # Manual execution
python run.py cleanup --dry-run  # See what would be deleted
```

**Pros:**
- ✅ **Full features** - comprehensive analysis and reporting
- ✅ **Manual control** - run when needed
- ✅ **Detailed logging** - verbose output and statistics
- ✅ **Dry-run mode** - preview before deletion

**Cons:**
- ❌ **Manual** - requires remembering to run
- ❌ **More complex** - additional dependencies

### **Option 3: Cron-Based Cleanup (Future Enhancement)**

```bash
# Weekly cleanup via cron
0 2 * * 0 /path/to/automation/run.py cleanup
```

**Pros:**
- ✅ **Scheduled** - runs automatically on schedule
- ✅ **Independent** - doesn't affect automation performance
- ✅ **Flexible timing** - run during low-usage hours

## 📊 **Storage Impact Analysis**

### **Without Garbage Collection:**
```
Daily screenshots: ~10 files × 200KB = 2MB/day
Monthly growth: 60MB/month  
Annual growth: 720MB/year
Plus log files: +50MB/year
Total: ~770MB/year
```

### **With Intelligent Garbage Collection:**
```
Error screenshots: 30 days × 2 files/day × 200KB = 12MB
Success screenshots: 10 files × 200KB = 2MB  
Other screenshots: 7 days × 8 files/day × 200KB = 11MB
Log files: 30 days × 100KB = 3MB
Total steady state: ~28MB (96% reduction)
```

## 🔧 **Implementation Details**

### **Integrated Cleanup Function:**

```python
def cleanup_old_logs():
    """Lightweight cleanup integrated into main automation"""
    try:
        current_time = time.time()
        cleanup_count = 0
        
        # Error screenshots: 30 days retention
        error_threshold = current_time - (30 * 24 * 3600)
        for pattern in ['*error*', '*failed*', '*not_found*', '*timeout*']:
            for file in glob.glob(f"{LOG_DIR}/screenshot_*{pattern}*.png"):
                if os.path.getmtime(file) < error_threshold:
                    os.unlink(file)
                    cleanup_count += 1
        
        # Success screenshots: keep 10 most recent
        success_files = glob.glob(f"{LOG_DIR}/screenshot_*completed*.png")
        if len(success_files) > 10:
            success_files.sort(key=os.path.getmtime, reverse=True)
            for file in success_files[10:]:
                os.unlink(file)
                cleanup_count += 1
        
        # Log cleanup stats
        if cleanup_count > 0:
            log(f"Cleaned up {cleanup_count} old log files")
            
    except Exception as e:
        log(f"Warning: Log cleanup failed: {e}")
        # Never fail automation for cleanup issues
```

### **Error Handling:**

1. **Non-blocking**: Cleanup failures never stop automation
2. **Graceful degradation**: Log warnings but continue
3. **Safe deletion**: Only delete files matching specific patterns
4. **Permission handling**: Skip files that can't be deleted

## 📈 **Monitoring & Metrics**

### **Cleanup Statistics:**
- Files removed per run
- Storage space freed
- Cleanup execution time
- Error rates

### **Health Indicators:**
- Directory size growth rate
- File count trends
- Cleanup frequency effectiveness

## 🎯 **Configuration Options**

### **Environment Variables:**
```bash
LOG_RETENTION_DAYS=30           # Log file retention
SCREENSHOT_RETENTION_DAYS=7     # General screenshot retention  
ERROR_RETENTION_DAYS=30         # Error screenshot retention
SUCCESS_RETENTION_COUNT=10      # Number of success screenshots to keep
```

### **Per-Environment Settings:**
```bash
# Development: Keep more for debugging
ERROR_RETENTION_DAYS=60
SUCCESS_RETENTION_COUNT=20

# Production: Aggressive cleanup
ERROR_RETENTION_DAYS=14
SUCCESS_RETENTION_COUNT=5
```

## 🚀 **Future Enhancements**

### **1. Smart Compression:**
```python
# Compress old screenshots instead of deleting
# Keep 6 months compressed, 1 month uncompressed
```

### **2. Cloud Storage Integration:**
```python  
# Upload error screenshots to S3 before local deletion
# Infinite retention in cloud, local cleanup
```

### **3. Machine Learning Optimization:**
```python
# Analyze which screenshots are actually used for debugging
# Adjust retention based on historical debugging patterns
```

### **4. Selective Retention:**
```python
# Keep screenshots from failed automation runs longer
# Delete screenshots from successful runs faster
```

## 💡 **Best Practices**

### **For Development:**
1. **Run manual cleanup weekly**: `python run.py cleanup`
2. **Check cleanup stats**: Review logs for cleanup effectiveness
3. **Monitor disk usage**: Ensure cleanup is working properly

### **For Production:**
1. **Integrated cleanup enabled**: Automatic cleanup every run
2. **Weekly manual cleanup**: For comprehensive maintenance
3. **Monitor storage metrics**: Set up alerts for unusual growth

### **For Integration:**
1. **Docker volume limits**: Set appropriate volume sizes
2. **Container restart policies**: Handle cleanup during container restarts  
3. **Backup considerations**: Exclude logs from backups or backup selectively

---

This intelligent garbage collection system ensures **sustainable automation** while preserving **debugging capabilities** and **audit trails**.