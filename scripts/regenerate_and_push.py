#!/usr/bin/env python3
"""
Regenerate documentation files and auto-push to GitHub
Usage: python scripts/regenerate_and_push.py
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command and show output"""
    print(f"\n>> {description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def get_changed_files():
    """Get list of changed .md files from last commit"""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True, text=True
    )
    files = result.stdout.strip().split('\n')
    return [f for f in files if f.startswith('public/docs/') and f.endswith('.md') and 'original' not in f]

def regenerate_file(filepath):
    """Restore file to original version from git history"""
    print(f"\nRegenerating: {filepath}")
    
    # Get original content from previous commit
    result = subprocess.run(
        ["git", "show", f"HEAD~1:{filepath}"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"  -> File is new, no original to restore")
        return False
    
    # Write original content back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    
    print(f"  -> Restored to original version")
    return True

def main():
    print("=" * 60)
    print("  REGENERATE AND PUSH DOCUMENTATION")
    print("=" * 60)
    
    # Step 1: Detect changed files
    print("\n[1/4] Detecting changed files...")
    changed = get_changed_files()
    
    if not changed:
        print("No .md files changed in last commit")
        return
    
    print(f"Found {len(changed)} file(s) to regenerate:")
    for f in changed:
        print(f"   - {f}")
    
    # Step 2: Regenerate files
    print("\n[2/4] Regenerating files to original...")
    regenerated = []
    for filepath in changed:
        if regenerate_file(filepath):
            regenerated.append(filepath)
    
    if not regenerated:
        print("No files were regenerated")
        return
    
    # Step 3: Git add
    print("\n[3/4] Adding files to git...")
    if not run_command("git add public/docs/", "Adding regenerated files"):
        print("ERROR: Failed to add files")
        return
    
    # Step 4: Commit and push
    print("\n[4/4] Committing and pushing...")
    commit_msg = "Regenerated original documentation files"
    
    if not run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
        print("ERROR: Failed to commit")
        return
    
    if not run_command("git push origin main", "Pushing to GitHub"):
        print("ERROR: Failed to push")
        return
    
    print("\n" + "=" * 60)
    print("  SUCCESS! Files regenerated and pushed!")
    print("=" * 60)
    print(f"\nRegenerated files: {len(regenerated)}")
    for f in regenerated:
        print(f"  -> {f}")
    print("\nBoth versions now on GitHub:")
    print("  - public/docs/<file>.md (original regenerated)")
    print("  - Your edited version was in previous commit")

if __name__ == "__main__":
    main()
