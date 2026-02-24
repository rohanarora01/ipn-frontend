#!/usr/bin/env python3
"""
Save edited and original versions of a file
Usage: python scripts/save_file.py <filename>
Example: python scripts/save_file.py _docker_Dockerfile.md
"""

import sys
import os
import shutil
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/save_file.py <filename>")
        print("Example: python scripts/save_file.py _docker_Dockerfile.md")
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
    
    # 1. Save current (edited) version
    edited_path = f"public/docs/edited/{filename}"
    shutil.copy2(filepath, edited_path)
    print(f"\n[1/3] Saved EDITED to: edited/{filename}")
    
    # 2. Get original from git history
    print(f"\n[2/3] Getting original version...")
    
    # Try different commits to find original
    original_content = None
    for i in range(1, 5):
        success, content, _ = run_cmd(f'git show HEAD~{i}:"{filepath}"')
        if success and len(content.strip()) > 100:
            original_content = content
            print(f"      Found original at HEAD~{i}")
            break
    
    if not original_content:
        print("      Could not find original version")
        return
    
    # 3. Save original to main docs folder
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"      Restored ORIGINAL to: docs/{filename}")
    
    # 4. Save to original folder too
    original_path = f"public/docs/original/{filename}"
    with open(original_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"      Saved ORIGINAL to: original/{filename}")
    
    # 5. Commit and push
    print(f"\n[3/3] Committing and pushing...")
    run_cmd("git add public/docs/")
    run_cmd(f'git commit -m "Save edited and original: {filename} [skip ci]"')
    run_cmd("git pull origin main --no-edit")
    run_cmd("git push origin main")
    
    print("\n" + "=" * 60)
    print("  SUCCESS!")
    print("=" * 60)
    print(f"\nSaved: {filename}")
    print(f"  edited/{filename}    <- YOUR EDITS")
    print(f"  docs/{filename}      <- ORIGINAL")
    print(f"  original/{filename}  <- ORIGINAL (backup)")

if __name__ == "__main__":
    main()
