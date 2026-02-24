#!/usr/bin/env python3
"""
Save edited and original versions of documentation files
Usage: python scripts/save_versions.py
"""

import subprocess
import os
import shutil
import sys

def run_cmd(cmd):
    """Run command and return success, stdout, stderr"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return result.returncode == 0, result.stdout, result.stderr

def get_last_commit_files():
    """Get files from the last commit"""
    success, stdout, _ = run_cmd("git log -1 --name-only --pretty=format:")
    if not success:
        return []
    
    files = []
    for line in stdout.strip().split('\n'):
        line = line.strip()
        if line and line.startswith('public/docs/') and line.endswith('.md'):
            if '/edited/' not in line and '/original/' not in line:
                files.append(line)
    return files

def main():
    print("=" * 60)
    print("  SAVE EDITED AND ORIGINAL VERSIONS")
    print("=" * 60)
    
    # Find files
    print("\n[1/3] Finding changed files...")
    files = get_last_commit_files()
    
    if not files:
        print("No files found in last commit")
        return
    
    print(f"Found {len(files)} file(s):")
    for f in files:
        print(f"  - {os.path.basename(f)}")
    
    # Create folders
    os.makedirs("public/docs/edited", exist_ok=True)
    os.makedirs("public/docs/original", exist_ok=True)
    
    # Process files
    print("\n[2/3] Processing...")
    processed = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"\n  {filename}:")
        
        # Read current file content (edited version)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                edited_content = f.read()
        except Exception as e:
            print(f"    Error reading file: {e}")
            continue
        
        # Save to edited folder
        edited_path = f"public/docs/edited/{filename}"
        with open(edited_path, 'w', encoding='utf-8') as f:
            f.write(edited_content)
        print(f"    ✓ Saved EDITED to: edited/{filename}")
        
        # Get original from git
        # Try multiple commits back to find a clean version
        original_content = None
        for i in range(1, 10):  # Try HEAD~1 through HEAD~9
            success, content, _ = run_cmd(f'git show HEAD~{i}:"{filepath}"')
            if success and content and len(content) > 50:  # Make sure it's not empty/corrupted
                original_content = content
                break
        
        if original_content:
            # Save original to main docs folder
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"    ✓ Restored ORIGINAL to: docs/{filename}")
            
            # Save to original folder too
            original_path = f"public/docs/original/{filename}"
            with open(original_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"    ✓ Saved ORIGINAL to: original/{filename}")
            
            processed.append(filename)
        else:
            print(f"    ⚠ Could not find clean original version")
    
    if not processed:
        print("\nNo files processed successfully")
        return
    
    # Commit and push
    print("\n[3/3] Committing and pushing...")
    run_cmd("git add public/docs/")
    run_cmd('git commit -m "Save edited and original versions [skip ci]"')
    run_cmd("git pull origin main --no-edit")
    run_cmd("git push origin main")
    
    print("\n" + "=" * 60)
    print("  SUCCESS!")
    print("=" * 60)
    print(f"\nProcessed: {', '.join(processed)}")
    print("\nFile locations:")
    print("  docs/FILE.md      -> ORIGINAL")
    print("  edited/FILE.md    -> YOUR EDITS")
    print("  original/FILE.md  -> ORIGINAL (backup)")

if __name__ == "__main__":
    main()
