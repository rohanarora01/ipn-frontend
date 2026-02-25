#!/usr/bin/env python3
"""
Save edited and original versions - PUSHES TO GITHUB
Usage: python scripts/save_to_github.py <filename>
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
        print("Usage: python scripts/save_to_github.py <filename>")
        print("Example: python scripts/save_to_github.py _docker_Dockerfile.md")
        return
    
    filename = sys.argv[1]
    filepath = f"public/docs/{filename}"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    print("=" * 70)
    print(f"  SAVING TO GITHUB: {filename}")
    print("=" * 70)
    
    # Create folders
    os.makedirs("public/docs/edited", exist_ok=True)
    os.makedirs("public/docs/original", exist_ok=True)
    print(f"\n📁 Created folders: edited/ and original/")
    
    # STEP 1: Save EDITED version
    print(f"\n[1/4] Saving EDITED version...")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        edited_content = f.read()
    
    edited_path = f"public/docs/edited/{filename}"
    with open(edited_path, 'w', encoding='utf-8') as f:
        f.write(edited_content)
    print(f"   ✅ Saved: public/docs/edited/{filename}")
    
    # STEP 2: Find and save ORIGINAL
    print(f"\n[2/4] Finding ORIGINAL version...")
    original_content = None
    
    for i in range(3, 20):
        success, content, _ = run_cmd(f'git show HEAD~{i}:"{filepath}" 2>nul')
        if success and len(content) > 200 and "Summary" in content:
            original_content = content
            print(f"   ✅ Found clean original at HEAD~{i}")
            break
    
    if not original_content:
        print(f"   ⚠️  Using current as original")
        original_content = edited_content
    
    # Save original to main docs folder
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"   ✅ Restored: public/docs/{filename}")
    
    # Save to original folder
    original_path = f"public/docs/original/{filename}"
    with open(original_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"   ✅ Saved: public/docs/original/{filename}")
    
    # STEP 3: Add to git (EXPLICITLY add subfolders)
    print(f"\n[3/4] Adding to Git...")
    run_cmd("git add public/docs/edited/")
    run_cmd("git add public/docs/original/")
    run_cmd("git add public/docs/")
    print(f"   ✅ Added to git staging")
    
    # STEP 4: Commit and push
    print(f"\n[4/4] Committing and Pushing to GitHub...")
    run_cmd(f'git commit -m "Save {filename}: edited + original versions [skip ci]"')
    
    # Pull first to avoid conflicts
    run_cmd("git pull origin main --no-edit")
    
    # Push
    success, _, stderr = run_cmd("git push origin main")
    
    if success:
        print(f"\n" + "=" * 70)
        print(f"  ✅ SUCCESS! Files pushed to GitHub!")
        print(f"=" * 70)
        print(f"\n📍 GitHub Links:")
        print(f"   Edited:   https://github.com/rohanarora01/ipn-frontend/blob/main/public/docs/edited/{filename}")
        print(f"   Original: https://github.com/rohanarora01/ipn-frontend/blob/main/public/docs/original/{filename}")
        print(f"   Main:     https://github.com/rohanarora01/ipn-frontend/blob/main/public/docs/{filename}")
        print(f"\n📂 Local folders:")
        print(f"   public/docs/edited/{filename}    <- YOUR EDITS")
        print(f"   public/docs/original/{filename}  <- ORIGINAL")
        print(f"   public/docs/{filename}           <- ORIGINAL (main)")
    else:
        print(f"\n❌ Push failed: {stderr}")
        print(f"\nTry manually:")
        print(f"   git pull origin main --no-edit")
        print(f"   git push origin main")

if __name__ == "__main__":
    main()
