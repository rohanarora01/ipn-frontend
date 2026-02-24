#!/usr/bin/env python3
"""
Regenerate a single documentation file after editing
Usage: python scripts/regenerate_single_file.py <filename>
Example: python scripts/regenerate_single_file.py _docker_Dockerfile.md
"""

import sys
import subprocess
import os
from pathlib import Path

def get_changed_files():
    """Get list of changed .md files from git"""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True,
        text=True
    )
    files = result.stdout.strip().split('\n')
    return [f for f in files if f.startswith('public/docs/') and f.endswith('.md')]

def regenerate_file(filepath):
    """Regenerate a single file - replace edited version with original from git"""
    print(f"🔄 Regenerating: {filepath}")
    
    # Get original content from previous commit
    result = subprocess.run(
        ["git", "show", f"HEAD~1:{filepath}"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ File didn't exist in previous commit: {filepath}")
        return False
    
    original_content = result.stdout
    
    # Write original content back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print(f"✅ Regenerated: {filepath}")
    return True

def main():
    if len(sys.argv) > 1:
        # Regenerate specific file
        filename = sys.argv[1]
        filepath = f"public/docs/{filename}"
        if os.path.exists(filepath):
            regenerate_file(filepath)
        else:
            print(f"❌ File not found: {filepath}")
    else:
        # Auto-detect changed files
        print("🔍 Detecting changed files...")
        changed = get_changed_files()
        
        if not changed:
            print("ℹ️ No .md files changed in last commit")
            return
        
        print(f"📄 Found {len(changed)} changed file(s):")
        for f in changed:
            print(f"   • {f}")
        
        print("\n🔄 Regenerating...")
        for filepath in changed:
            regenerate_file(filepath)
        
        print("\n✅ Done! Now commit the regenerated files:")
        print("   git add public/docs/")
        print("   git commit -m 'Regenerated original docs'")
        print("   git push origin main")

if __name__ == "__main__":
    main()
