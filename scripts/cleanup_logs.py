#!/usr/bin/env python3
"""
Log and Screenshot Cleanup Utility

Manages log file and screenshot retention with configurable policies.
Automatically removes old files while preserving recent important data.

Usage:
    python cleanup_logs.py [--dry-run] [--verbose]
    
Environment Variables:
    LOG_RETENTION_DAYS: Days to keep log files (default: 30)
    SCREENSHOT_RETENTION_DAYS: Days to keep screenshots (default: 7)
    ERROR_RETENTION_DAYS: Days to keep error screenshots (default: 30)
    SUCCESS_RETENTION_COUNT: Number of recent successful transfers to keep (default: 10)
"""

import os
import sys
import glob
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re

# Configuration from environment or defaults
LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 30))
SCREENSHOT_RETENTION_DAYS = int(os.getenv('SCREENSHOT_RETENTION_DAYS', 7))
ERROR_RETENTION_DAYS = int(os.getenv('ERROR_RETENTION_DAYS', 30))
SUCCESS_RETENTION_COUNT = int(os.getenv('SUCCESS_RETENTION_COUNT', 10))

LOG_DIR = os.getenv('LOG_DIR', './logs')

def log(message, verbose=False):
    """Print message with timestamp if verbose or always for important messages"""
    if verbose or not message.startswith('  '):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def parse_screenshot_date(filename):
    """Extract date from screenshot filename like screenshot_20250826_152726_transfer_completed.png"""
    match = re.search(r'screenshot_(\d{8})_\d{6}', filename)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y%m%d')
        except ValueError:
            pass
    return None

def categorize_files(log_dir, verbose=False):
    """Categorize files by type and importance"""
    files = {
        'error_screenshots': [],
        'success_screenshots': [],
        'other_screenshots': [],
        'log_files': [],
        'lock_files': [],
        'unknown': []
    }
    
    if not os.path.exists(log_dir):
        log(f"Log directory {log_dir} does not exist")
        return files
    
    for filepath in Path(log_dir).glob('*'):
        filename = filepath.name
        file_stat = filepath.stat()
        file_age = datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)
        
        file_info = {
            'path': filepath,
            'name': filename,
            'size': file_stat.st_size,
            'age_days': file_age.days,
            'modified': datetime.fromtimestamp(file_stat.st_mtime)
        }
        
        # Categorize by filename patterns
        if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
            if any(error_type in filename.lower() for error_type in 
                   ['error', 'failed', 'not_found', 'timeout', 'security', 'captcha']):
                files['error_screenshots'].append(file_info)
            elif any(success_type in filename.lower() for success_type in 
                     ['completed', 'success', 'confirmation']):
                files['success_screenshots'].append(file_info)
            else:
                files['other_screenshots'].append(file_info)
        elif filename.endswith('.log'):
            files['log_files'].append(file_info)
        elif filename.endswith('.lock'):
            files['lock_files'].append(file_info)
        else:
            files['unknown'].append(file_info)
    
    if verbose:
        log(f"  Found {len(files['error_screenshots'])} error screenshots")
        log(f"  Found {len(files['success_screenshots'])} success screenshots")
        log(f"  Found {len(files['other_screenshots'])} other screenshots")
        log(f"  Found {len(files['log_files'])} log files")
        log(f"  Found {len(files['lock_files'])} lock files")
    
    return files

def cleanup_by_age(file_list, retention_days, file_type, dry_run=False, verbose=False):
    """Remove files older than retention_days"""
    removed_count = 0
    removed_size = 0
    
    for file_info in file_list:
        if file_info['age_days'] > retention_days:
            if verbose:
                log(f"  Removing old {file_type}: {file_info['name']} ({file_info['age_days']} days old, {file_info['size']:,} bytes)")
            
            if not dry_run:
                try:
                    file_info['path'].unlink()
                    removed_count += 1
                    removed_size += file_info['size']
                except Exception as e:
                    log(f"  Error removing {file_info['name']}: {e}")
            else:
                removed_count += 1
                removed_size += file_info['size']
    
    return removed_count, removed_size

def cleanup_by_count(file_list, keep_count, file_type, dry_run=False, verbose=False):
    """Keep only the most recent keep_count files"""
    if len(file_list) <= keep_count:
        return 0, 0
    
    # Sort by modification time (newest first)
    sorted_files = sorted(file_list, key=lambda f: f['modified'], reverse=True)
    files_to_remove = sorted_files[keep_count:]
    
    removed_count = 0
    removed_size = 0
    
    for file_info in files_to_remove:
        if verbose:
            log(f"  Removing excess {file_type}: {file_info['name']} (keeping {keep_count} most recent)")
        
        if not dry_run:
            try:
                file_info['path'].unlink()
                removed_count += 1
                removed_size += file_info['size']
            except Exception as e:
                log(f"  Error removing {file_info['name']}: {e}")
        else:
            removed_count += 1
            removed_size += file_info['size']
    
    return removed_count, removed_size

def cleanup_lock_files(file_list, dry_run=False, verbose=False):
    """Remove lock files older than 7 days (they should only exist for current day)"""
    removed_count = 0
    removed_size = 0
    
    for file_info in file_list:
        if file_info['age_days'] > 7:  # Lock files should never be this old
            if verbose:
                log(f"  Removing stale lock file: {file_info['name']} ({file_info['age_days']} days old)")
            
            if not dry_run:
                try:
                    file_info['path'].unlink()
                    removed_count += 1
                    removed_size += file_info['size']
                except Exception as e:
                    log(f"  Error removing {file_info['name']}: {e}")
            else:
                removed_count += 1
                removed_size += file_info['size']
    
    return removed_count, removed_size

def format_size(bytes_size):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}TB"

def main():
    parser = argparse.ArgumentParser(description='Clean up automation logs and screenshots')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    parser.add_argument('--log-dir', default=LOG_DIR, help=f'Log directory to clean (default: {LOG_DIR})')
    
    args = parser.parse_args()
    
    log(f"Starting log cleanup for directory: {args.log_dir}")
    if args.dry_run:
        log("DRY RUN MODE - No files will be actually deleted")
    
    # Get current directory size
    if os.path.exists(args.log_dir):
        initial_size = sum(f.stat().st_size for f in Path(args.log_dir).glob('*') if f.is_file())
        log(f"Initial directory size: {format_size(initial_size)}")
    else:
        log(f"Directory {args.log_dir} does not exist")
        return
    
    # Categorize all files
    files = categorize_files(args.log_dir, args.verbose)
    
    total_removed_count = 0
    total_removed_size = 0
    
    # Cleanup error screenshots (keep longer for debugging)
    log(f"Cleaning error screenshots older than {ERROR_RETENTION_DAYS} days...")
    count, size = cleanup_by_age(files['error_screenshots'], ERROR_RETENTION_DAYS, 
                                 'error screenshot', args.dry_run, args.verbose)
    total_removed_count += count
    total_removed_size += size
    log(f"  Removed {count} error screenshots ({format_size(size)})")
    
    # Cleanup success screenshots (keep fewer, they're less important for debugging)
    log(f"Keeping {SUCCESS_RETENTION_COUNT} most recent successful transfer screenshots...")
    count, size = cleanup_by_count(files['success_screenshots'], SUCCESS_RETENTION_COUNT,
                                   'success screenshot', args.dry_run, args.verbose)
    total_removed_count += count
    total_removed_size += size
    log(f"  Removed {count} success screenshots ({format_size(size)})")
    
    # Cleanup other screenshots by age
    log(f"Cleaning other screenshots older than {SCREENSHOT_RETENTION_DAYS} days...")
    count, size = cleanup_by_age(files['other_screenshots'], SCREENSHOT_RETENTION_DAYS,
                                 'screenshot', args.dry_run, args.verbose)
    total_removed_count += count
    total_removed_size += size
    log(f"  Removed {count} other screenshots ({format_size(size)})")
    
    # Cleanup log files
    log(f"Cleaning log files older than {LOG_RETENTION_DAYS} days...")
    count, size = cleanup_by_age(files['log_files'], LOG_RETENTION_DAYS,
                                 'log file', args.dry_run, args.verbose)
    total_removed_count += count
    total_removed_size += size
    log(f"  Removed {count} log files ({format_size(size)})")
    
    # Cleanup stale lock files
    log("Cleaning stale lock files...")
    count, size = cleanup_lock_files(files['lock_files'], args.dry_run, args.verbose)
    total_removed_count += count
    total_removed_size += size
    log(f"  Removed {count} lock files ({format_size(size)})")
    
    # Final summary
    if os.path.exists(args.log_dir):
        final_size = sum(f.stat().st_size for f in Path(args.log_dir).glob('*') if f.is_file())
        space_freed = initial_size - final_size if not args.dry_run else total_removed_size
        
        log(f"Cleanup completed!")
        log(f"  Total files processed: {total_removed_count}")
        log(f"  Space {'would be ' if args.dry_run else ''}freed: {format_size(space_freed)}")
        log(f"  Final directory size: {format_size(final_size if not args.dry_run else initial_size)}")
    
    if args.dry_run:
        log("Run without --dry-run to actually delete files")

if __name__ == '__main__':
    main()