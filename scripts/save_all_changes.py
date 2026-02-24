#!/usr/bin/env python3
"""
Automatically detect and save ALL changed .md files
Usage: python scripts/save_all_changes.py
"""

import subprocess
import os
import shutil

def run_command(cmd, description=""):
    """Run a command and show output"""
    if description:
        print(f">> {description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and "error" not in result.stderr.lower():
        print(result.stderr)
    return result.returncode == 0

def get_changed_files():
    """Get all changed .md files in public/docs/"""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True, text=True
    )
    files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
    # Filter for .md files in public/docs, excluding edited/ and original/
    changed = []
    for f in files:
        if (f.startswith('public/docs/') and 
            f.endswith('.md') and 
            '/edited/' not in f and 
            '/original/' not in f):
            changed.append(f)
    return changed

def main():
    print("=" * 60)
    print("  SAVE ALL CHANGED FILES - AUTO DETECT")
    print("=" * 60)
    
    # Step 1: Detect changed files
    print("\n[1/5] Detecting changed files...")
    changed_files = get_changed_files()
    
    if not changed_files:
        print("No .md files changed in last commit")
        print("Make sure you committed your changes first!")
        return
    
    print(f"Found {len(changed_files)} changed file(s):")
    for f in changed_files:
        print(f"   - {f}")
    
    # Step 2: Create folders
    print("\n[2/5] Creating folders...")
    os.makedirs("public/docs/edited", exist_ok=True)
    os.makedirs("public/docs/original", exist_ok=True)
    print("   - public/docs/edited/")
    print("   - public/docs/original/")
    
    # Step 3: Process each file
    print("\n[3/5] Processing files...")
    processed = []
    
    for filepath in changed_files:
        filename = os.path.basename(filepath)
        print(f"\n   Processing: {filename}")
        
        # Save edited version
        edited_path = f"public/docs/edited/{filename}"
        shutil.copy2(filepath, edited_path)
        print(f"      -> Saved EDITED to: edited/{filename}")
        
        # Get original from git (try HEAD~2 first, then HEAD~1)
        result = subprocess.run(
            ["git", "show", f"HEAD~2:{filepath}"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            result = subprocess.run(
                ["git", "show", f"HEAD~1:{filepath}"],
                capture_output=True, text=True
            )
        
        if result.returncode == 0:
            # Restore original to main docs folder
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print(f"      -> Restored ORIGINAL to: docs/{filename}")
            
            # Also save to original folder
            original_path = f"public/docs/original/{filename}"
            shutil.copy2(filepath, original_path)
            print(f"      -> Saved ORIGINAL to: original/{filename}")
            
            processed.append(filename)
        else:
            print(f"      -> WARNING: Could not find original")
    
    if not processed:
        print("\nNo files were processed")
        return
    
    # Step 4: Git add
    print("\n[4/5] Adding files to git...")
    run_command("git add public/docs/")
    
    # Step 5: Commit and push
    print("\n[5/5] Committing and pushing...")
    file_list = ", ".join(processed)
    commit_msg = f"Saved {len(processed)} file(s): edited + original versions"
    
    run_command(f'git commit -m "{commit_msg} [skip ci]"')
    run_command("git pull origin main --no-edit")
    run_command("git push origin main")
    
    print("\n" + "=" * 60)
    print("  SUCCESS! All files saved!")
    print("=" * 60)
    print(f"\nProcessed {len(processed)} file(s):")
    for f in processed:
        print(f"   - {f}")
    print(f"\nOn GitHub you now have:")
    print(f"   public/docs/FILE.md           -> ORIGINAL")
    print(f"   public/docs/edited/FILE.md    -> YOUR EDITS")
    print(f"   public/docs/original/FILE.md  -> ORIGINAL (backup)")

if __name__ == "__main__":
    main()
