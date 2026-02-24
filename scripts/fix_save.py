#!/usr/bin/env python3
"""
FIXED: Save edited and original versions correctly
Usage: python scripts/fix_save.py <filename>
Example: python scripts/fix_save.py _docker_Dockerfile.md
"""

import sys
import os
import shutil
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return result.returncode == 0, result.stdout, result.stderr

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/fix_save.py <filename>")
        print("Example: python scripts/fix_save.py _docker_Dockerfile.md")
        return
    
    filename = sys.argv[1]
    filepath = f"public/docs/{filename}"
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    print("=" * 60)
    print(f"  Processing: {filename}")
    print("=" * 60)
    
    # Create folders
    os.makedirs("public/docs/edited", exist_ok=True)
    os.makedirs("public/docs/original", exist_ok=True)
    
    # STEP 1: Read CURRENT file (user's edited version) and save to edited/
    print("\n[1/3] Saving EDITED version...")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            edited_content = f.read()
        
        edited_path = f"public/docs/edited/{filename}"
        with open(edited_path, 'w', encoding='utf-8') as f:
            f.write(edited_content)
        print(f"      Saved to: edited/{filename}")
    except Exception as e:
        print(f"      Error: {e}")
        return
    
    # STEP 2: Find clean original from git (look deeper in history)
    print("\n[2/3] Finding clean ORIGINAL version...")
    
    original_content = None
    # Try HEAD~3 to HEAD~10 to find a version with actual content
    for i in range(3, 15):
        success, content, _ = run_cmd(f'git show HEAD~{i}:"{filepath}" 2>nul')
        if success:
            # Check if it has meaningful content (more than 200 chars and has "Summary")
            if len(content) > 200 and "Summary" in content:
                original_content = content
                print(f"      Found clean original at HEAD~{i}")
                break
    
    if not original_content:
        print("      WARNING: Could not find clean original")
        print("      Using current file as original")
        original_content = edited_content
    
    # STEP 3: Save original to docs/ folder (main location)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"      Restored to: docs/{filename}")
    except Exception as e:
        print(f"      Error: {e}")
        return
    
    # STEP 4: Save to original/ folder too
    original_path = f"public/docs/original/{filename}"
    try:
        with open(original_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"      Saved to: original/{filename}")
    except Exception as e:
        print(f"      Error: {e}")
        return
    
    # STEP 5: Commit and push
    print("\n[3/3] Committing and pushing...")
    run_cmd("git add public/docs/")
    run_cmd(f'git commit -m "Save edited and original: {filename} [skip ci]"')
    run_cmd("git pull origin main --no-edit")
    success, _, _ = run_cmd("git push origin main")
    
    if success:
        print("\n" + "=" * 60)
        print("  SUCCESS!")
        print("=" * 60)
        print(f"\nFile: {filename}")
        print(f"  edited/{filename}    -> YOUR CHANGES")
        print(f"  docs/{filename}      -> ORIGINAL (clean)")
        print(f"  original/{filename}  -> ORIGINAL (backup)")
    else:
        print("\nPush failed. Try running manually:")
        print("  git pull origin main --no-edit")
        print("  git push origin main")

if __name__ == "__main__":
    main()
