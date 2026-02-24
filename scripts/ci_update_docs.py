#!/usr/bin/env python3
"""
ci_update_docs.py
-----------------
GitHub Actions helper for detecting and regenerating documentation.

This script:
1. Detects which .md files changed in the last commit
2. Regenerates documentation.json using the Node.js generator
3. Can be used in GitHub Actions or locally

Usage:
    python scripts/ci_update_docs.py              # Detect and regenerate
    python scripts/ci_update_docs.py --check      # Only check, don't regenerate
    python scripts/ci_update_docs.py --all        # Regenerate all docs
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

DOCS_DIR = Path("public/docs")
OUTPUT_SRC = Path("src/data/documentation.json")
OUTPUT_PUBLIC = Path("public/data/documentation.json")
SUMMARY_FILE = Path("SUMMARY.md")


# ═══════════════════════════════════════════════════════════════════════════════
# Git Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def get_changed_files():
    """Get list of .md files changed in the last commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        all_changed = result.stdout.strip().split("\n")
        
        # Filter only .md files in public/docs/
        docs_changed = [
            f for f in all_changed 
            if f.startswith("public/docs/") and f.endswith(".md")
        ]
        
        # Also check if SUMMARY.md changed
        summary_changed = SUMMARY_FILE.name in [Path(f).name for f in all_changed]
        
        return docs_changed, summary_changed
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git error: {e}")
        # If we can't get git diff (e.g., first commit), return all docs
        return get_all_doc_files(), True


def get_all_doc_files():
    """Get all .md files in public/docs/."""
    if not DOCS_DIR.exists():
        return []
    return [str(f) for f in DOCS_DIR.glob("*.md")]


def get_file_content(filepath):
    """Read file content safely."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return ""


# ═══════════════════════════════════════════════════════════════════════════════
# Documentation Generator
# ═══════════════════════════════════════════════════════════════════════════════

def parse_markdown_link(line):
    """Parse a markdown link like [Name](file.md)."""
    match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', line.strip())
    if match:
        return match.group(1), match.group(2)
    return None, None


def parse_summary():
    """Parse SUMMARY.md to extract documentation structure."""
    if not SUMMARY_FILE.exists():
        print(f"⚠️ {SUMMARY_FILE} not found")
        return []
    
    content = get_file_content(SUMMARY_FILE)
    files = []
    current_section = None
    subsection_stack = []  # Track nested subsections
    
    for line_num, line in enumerate(content.split('\n'), 1):
        line = line.rstrip()
        if not line:
            continue
        
        # Skip the main title
        if line.startswith('# ') and 'Documentation' in line:
            continue
            
        # Section header (## Section)
        if line.startswith('## '):
            current_section = line.replace('## ', '').strip()
            subsection_stack = []
            print(f"  📁 Section: {current_section}")
            continue
        
        # Strip leading bullet and spaces for nested items
        # Handle: "- **Name**", "  - **Name**", "    - [Name](file.md)"
        stripped = line.lstrip()
        indent_level = len(line) - len(stripped)
        
        # Remove leading "- " if present
        if stripped.startswith('- '):
            stripped = stripped[2:]
        
        # Subsection (**Name**) - after stripping "- "
        if stripped.startswith('**') and stripped.endswith('**'):
            subsection_name = stripped.replace('**', '').strip()
            # Adjust stack based on indentation
            level = indent_level // 2  # Approximate nesting level
            while len(subsection_stack) >= level:
                subsection_stack.pop() if subsection_stack else None
            subsection_stack.append(subsection_name)
            current_subsection = ' > '.join(subsection_stack)
            print(f"    📂 Subsection: {current_subsection}")
            continue
        
        # File link [Name](file.md)
        if '[' in stripped and '](' in stripped:
            display_name, md_file = parse_markdown_link(stripped)
            if display_name and md_file:
                # Extract original filename from md filename
                # e.g., _docker_Dockerfile.md -> Dockerfile
                original_file = md_file.replace('.md', '').replace('_', '/')
                
                # Determine category from extension
                ext = Path(original_file).suffix.lower()
                if ext == '.php':
                    category = 'backend'
                elif ext in ['.js', '.ts', '.tsx', '.jsx', '.vue', '.json']:
                    category = 'frontend'
                else:
                    category = 'other'
                
                # Show file found
                file_path = f"public/docs/{md_file}"
                print(f"      📄 Found: {display_name} → {file_path}")
                
                files.append({
                    'id': len(files),
                    'displayName': display_name,
                    'fileName': Path(original_file).name,
                    'mdFile': md_file,
                    'path': original_file,
                    'extension': ext,
                    'category': category,
                    'section': current_section or 'Uncategorized',
                    'subsection': current_subsection or ''
                })
    
    return files


def generate_documentation_json(files):
    """Generate the documentation.json file."""
    
    # Build categories structure
    categories = {}
    for file in files:
        section = file['section']
        subsection = file['subsection']
        
        if section not in categories:
            categories[section] = {
                'name': section,
                'subsections': {},
                'fileCount': 0
            }
        
        categories[section]['fileCount'] += 1
        
        if subsection:
            sub_key = subsection
            if sub_key not in categories[section]['subsections']:
                categories[section]['subsections'][sub_key] = {
                    'name': subsection,
                    'path': [subsection],
                    'files': []
                }
            categories[section]['subsections'][sub_key]['files'].append(file['id'])
    
    # Build stats
    stats = {
        'total': len(files),
        'backend': sum(1 for f in files if f['category'] == 'backend'),
        'frontend': sum(1 for f in files if f['category'] == 'frontend'),
        'other': sum(1 for f in files if f['category'] == 'other')
    }
    
    # Build search index
    search_index = [
        {
            'id': f['id'],
            'text': f"{f['displayName']} {f['fileName']} {f['path']} {f['section']} {f['subsection']}".lower(),
            'category': f['category']
        }
        for f in files
    ]
    
    # Build output
    output = {
        'categories': categories,
        'files': files,
        'stats': stats,
        'searchIndex': search_index,
        'generatedAt': datetime.now().isoformat()
    }
    
    return output


def save_documentation_json(data):
    """Save documentation.json to both src/data and public/data."""
    
    # Ensure directories exist
    OUTPUT_SRC.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    
    # Write files
    json_str = json.dumps(data, indent=2)
    
    OUTPUT_SRC.write_text(json_str, encoding='utf-8')
    OUTPUT_PUBLIC.write_text(json_str, encoding='utf-8')
    
    print(f"  ✓ Written: {OUTPUT_SRC}")
    print(f"  ✓ Written: {OUTPUT_PUBLIC}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='CI Documentation Updater',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/ci_update_docs.py         # Update based on changed files
  python scripts/ci_update_docs.py --check # Just check what changed
  python scripts/ci_update_docs.py --all   # Regenerate all docs
        """
    )
    parser.add_argument(
        '--check', 
        action='store_true',
        help='Only check for changes, do not regenerate'
    )
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Regenerate all documentation (ignore git changes)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  📚 CI Documentation Updater")
    print("=" * 60)
    print()
    
    # Detect changed files
    if args.all:
        print("🔄 Mode: Regenerate ALL documentation")
        changed_docs = get_all_doc_files()
        summary_changed = True
    else:
        print("🔍 Checking for changed files...")
        changed_docs, summary_changed = get_changed_files()
    
    # Display results
    print()
    if changed_docs:
        print(f"📄 Changed documentation files ({len(changed_docs)}):")
        for f in changed_docs[:10]:  # Show first 10
            print(f"   • {f}")
        if len(changed_docs) > 10:
            print(f"   ... and {len(changed_docs) - 10} more")
    else:
        print("📄 No documentation files changed")
    
    if summary_changed:
        print("📝 SUMMARY.md changed - full regeneration needed")
    
    # Exit if just checking
    if args.check:
        print()
        print("✅ Check complete (no files modified)")
        return 0 if not changed_docs and not summary_changed else 1
    
    # Determine if we need to regenerate
    needs_regen = bool(changed_docs) or summary_changed or args.all
    
    if not needs_regen:
        print()
        print("✅ No changes detected - documentation is up to date")
        return 0
    
    # Regenerate documentation
    print()
    print("🔄 Regenerating documentation.json...")
    print()
    
    files = parse_summary()
    if not files:
        print("⚠️ Warning: No files found in SUMMARY.md")
        print("   Creating empty documentation structure...")
        files = []
    
    print(f"  Found {len(files)} files in SUMMARY.md")
    
    data = generate_documentation_json(files)
    save_documentation_json(data)
    
    # Print stats
    print()
    print("=" * 60)
    print("  ✅ Documentation regenerated successfully!")
    print("=" * 60)
    print()
    print("📊 Statistics:")
    print(f"   Total files: {data['stats']['total']}")
    print(f"   Backend (PHP): {data['stats']['backend']}")
    print(f"   Frontend (JS/TS): {data['stats']['frontend']}")
    print(f"   Other: {data['stats']['other']}")
    print(f"   Categories: {len(data['categories'])}")
    print()
    print(f"🕐 Generated at: {data['generatedAt']}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
