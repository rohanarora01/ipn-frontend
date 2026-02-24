#!/usr/bin/env python3
"""
Save BOTH edited and original versions
Usage: python scripts/save_both_versions.py <filename>
Example: python scripts/save_both_versions.py _docker_Dockerfile.md
"""

import sys
import os
import subprocess
import shutil

def run_command(cmd, description=""):
    """Run a command and show output"""
    if description:
        print(f">> {description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/save_both_versions.py <filename>")
        print("Example: python scripts/save_both_versions.py _docker_Dockerfile.md")
        return
    
    filename = sys.argv[1]
    filepath = f"public/docs/{filename}"
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    print("=" * 60)
    print("  SAVE BOTH EDITED AND ORIGINAL VERSIONS")
    print("=" * 60)
    
    # Step 1: Create folders
    os.makedirs("public/docs/edited", exist_ok=True)
    os.makedirs("public/docs/original", exist_ok=True)
    
    # Step 2: Copy current (edited) version to edited folder
    edited_path = f"public/docs/edited/{filename}"
    shutil.copy2(filepath, edited_path)
    print(f"\n[1/4] Saved EDITED version to: {edited_path}")
    
    # Step 3: Get original version from git and save to main folder
    print(f"\n[2/4] Restoring ORIGINAL version...")
    
    # Try to get original from git history
    result = subprocess.run(
        ["git", "show", f"HEAD~2:{filepath}"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        # Try HEAD~1
        result = subprocess.run(
            ["git", "show", f"HEAD~1:{filepath}"],
            capture_output=True, text=True
        )
    
    if result.returncode == 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        print(f"  -> Original restored to: {filepath}")
    else:
        print(f"  -> Could not find original in git history")
        return
    
    # Step 4: Also save original to original folder
    original_path = f"public/docs/original/{filename}"
    shutil.copy2(filepath, original_path)
    print(f"\n[3/4] Saved ORIGINAL version to: {original_path}")
    
    # Step 5: Git add, commit, push
    print(f"\n[4/4] Committing and pushing...")
    
    run_command("git add public/docs/", "Adding files")
    run_command('git commit -m "Saved edited and original versions [skip ci]"', "Committing")
    run_command("git pull origin main --no-edit", "Pulling latest")
    run_command("git push origin main", "Pushing to GitHub")
    
    print("\n" + "=" * 60)
    print("  SUCCESS!")
    print("=" * 60)
    print(f"\nYou now have:")
    print(f"  - public/docs/{filename}           <- ORIGINAL")
    print(f"  - public/docs/edited/{filename}    <- EDITED (your changes)")
    print(f"  - public/docs/original/{filename}  <- ORIGINAL (backup)")
    print(f"\nAll versions saved on GitHub!")

if __name__ == "__main__":
    main()
