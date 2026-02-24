#!/usr/bin/env python3
"""
FINAL VERSION: Save edited and original files automatically
Usage: python scripts/final_save_versions.py
"""

import subprocess
import os
import shutil
import sys

def run_cmd(cmd):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def get_files_from_last_commit():
    """Get all .md files changed in the last commit"""
    success, stdout, _ = run_cmd("git diff-tree --no-commit-id --name-only -r HEAD")
    if not success:
        return []
    
    files = []
    for line in stdout.strip().split('\n'):
        line = line.strip()
        if line.startswith('public/docs/') and line.endswith('.md'):
            # Skip if it's in edited or original subfolders
            if '/edited/' not in line and '/original/' not in line:
                files.append(line)
    return files

def main():
    print("=" * 60)
    print("  FINAL VERSION SAVER")
    print("=" * 60)
    
    # Get files from last commit
    print("\n[1/4] Finding files from last commit...")
    files = get_files_from_last_commit()
    
    if not files:
        print("No .md files found in last commit")
        return
    
    print(f"Found {len(files)} file(s):")
    for f in files:
        print(f"  - {os.path.basename(f)}")
    
    # Create folders
    print("\n[2/4] Creating folders...")
    os.makedirs("public/docs/edited", exist_ok=True)
    os.makedirs("public/docs/original", exist_ok=True)
    
    # Process each file
    print("\n[3/4] Processing files...")
    saved_files = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"\n  Processing: {filename}")
        
        # 1. Save current (edited) version to edited/ folder
        edited_path = f"public/docs/edited/{filename}"
        shutil.copy2(filepath, edited_path)
        print(f"    ✓ Saved EDITED version to: edited/{filename}")
        
        # 2. Get original from git (before last commit)
        success, original_content, _ = run_cmd(f'git show HEAD~1:"{filepath}"')
        
        if success:
            # Restore original to main docs folder
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"    ✓ Restored ORIGINAL to: docs/{filename}")
            
            # Also save to original folder
            original_path = f"public/docs/original/{filename}"
            with open(original_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"    ✓ Saved ORIGINAL to: original/{filename}")
            
            saved_files.append(filename)
        else:
            print(f"    ⚠ Could not get original version")
    
    if not saved_files:
        print("\nNo files were saved")
        return
    
    # Commit and push
    print("\n[4/4] Committing and pushing...")
    
    run_cmd("git add public/docs/")
    run_cmd('git commit -m "Saved edited and original versions [skip ci]"')
    run_cmd("git pull origin main --no-edit")
    run_cmd("git push origin main")
    
    print("\n" + "=" * 60)
    print("  SUCCESS!")
    print("=" * 60)
    print(f"\nSaved {len(saved_files)} file(s):")
    for f in saved_files:
        print(f"  ✓ {f}")
    
    print("\nOn GitHub:")
    print("  📄 docs/FILE.md         -> ORIGINAL")
    print("  ✏️  edited/FILE.md       -> YOUR EDITS")
    print("  📋 original/FILE.md      -> ORIGINAL (backup)")

if __name__ == "__main__":
    main()
