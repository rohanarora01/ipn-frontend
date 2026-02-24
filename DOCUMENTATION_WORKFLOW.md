# 📚 Documentation Auto-Update Workflow Guide

This guide explains how the automatic documentation regeneration works when you push changes to GitHub.

## What Happens When You Push?

```
┌─────────────────────────────────────────────────────────────────────────┐
│  YOU PUSH CHANGES                                                       │
│  (e.g., modify public/docs/_docker_Dockerfile.md)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS TRIGGERED                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ 1. Detect       │→│ 2. Regenerate   │→│ 3. Build &      │         │
│  │    Changes      │  │    docs         │  │    Deploy       │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option A: Full Auto (Recommended)

Enable auto-commit so GitHub Actions commits regenerated files back to your repo:

1. **Go to**: `GitHub Repo` → `Settings` → `Actions` → `General`
2. **Under "Workflow permissions"**: Select ✅ `Read and write permissions`
3. **Save** changes
4. **Edit** `.github/workflows/main_ipnsvrweb.yml`:
   ```yaml
   permissions:
     contents: write
   ```
5. **Uncomment** the "Commit and push changes" step in the workflow

### Option B: Build-Time Only (Default)

Documentation is regenerated during build but NOT committed back:

- ✅ Works immediately (no settings changes needed)
- ⚠️ Changes exist only in the deployed build, not in git
- ⚠️ Repository `documentation.json` stays unchanged

---

## How It Works

### 1. Change Detection

The workflow checks which files changed in your push:

```bash
# This command runs automatically
git diff --name-only HEAD~1 HEAD | grep '^public/docs/.*\.md$'
```

**If you modified:** `public/docs/_docker_Dockerfile.md`  
**Then:** Documentation regeneration triggers

### 2. Documentation Regeneration

The script `scripts/ci_update_docs.py`:

1. Parses `SUMMARY.md` to get the documentation structure
2. Generates new `documentation.json` with:
   - Updated file list
   - Categories (backend/frontend/other)
   - Search index
   - Statistics
3. Saves to:
   - `src/data/documentation.json` (for the app)
   - `public/data/documentation.json` (for runtime access)

### 3. Auto-Commit (Optional)

If enabled, the workflow commits changes:

```bash
git add src/data/documentation.json public/data/documentation.json
git commit -m "🤖 Auto-regenerate documentation [skip ci]"
git push
```

The `[skip ci]` tag prevents infinite loops (the commit won't trigger another workflow).

---

## Local Development

### Check what changed (without regenerating):

```bash
npm run ci-update-docs:check
```

### Regenerate based on changed files:

```bash
npm run ci-update-docs
```

### Force regenerate all documentation:

```bash
npm run ci-update-docs:all
```

### Traditional method (always works):

```bash
npm run generate-docs
```

---

## Workflow File Structure

```yaml
.github/workflows/main_ipnsvrweb.yml
├── Job 1: update-docs
│   ├── Detect changed .md files
│   ├── Run ci_update_docs.py
│   └── Commit changes (optional)
│
├── Job 2: build
│   ├── npm install
│   ├── npm run generate-docs
│   └── npm run build
│
└── Job 3: deploy
    └── Deploy to Azure
```

---

## Troubleshooting

### "No changes detected" but I modified a file!

Make sure you modified files in `public/docs/` with `.md` extension:

```bash
# This WILL trigger regeneration
public/docs/_docker_Dockerfile.md
public/docs/src_Api_Controller_User_php.md

# This will NOT trigger
README.md
SUMMARY.md
docs/other-file.md
```

### Changes not being committed

Check workflow permissions:

1. Go to `Settings` → `Actions` → `General`
2. Verify `Workflow permissions` is set to `Read and write permissions`
3. Check the workflow has the `permissions:` block uncommented

### Infinite loop of commits

The `[skip ci]` in the commit message prevents this. If it happens:

1. Cancel the running workflow
2. Add `[skip ci]` to your commit messages temporarily
3. Fix the workflow file

### "Error: Permission denied" during push

Your `GITHUB_TOKEN` doesn't have write permissions:

1. Go to `Settings` → `Actions` → `General`
2. Change `Workflow permissions` to `Read and write permissions`
3. Save and re-run the workflow

---

## File Reference

| File | Purpose |
|------|---------|
| `public/docs/*.md` | Documentation source files |
| `SUMMARY.md` | Index file defining documentation structure |
| `src/data/documentation.json` | Generated index (used by app) |
| `public/data/documentation.json` | Generated index (runtime access) |
| `scripts/ci_update_docs.py` | CI helper for doc regeneration |
| `scripts/generateDocsData.js` | Node.js doc generator |

---

## Example: Making a Change

```bash
# 1. Edit a documentation file
echo "# Updated Docker Info" > ipn-frontend/public/docs/_docker_Dockerfile.md

# 2. Commit and push
git add ipn-frontend/public/docs/_docker_Dockerfile.md
git commit -m "Update Docker documentation"
git push origin main

# 3. GitHub Actions automatically:
#    - Detects the change
#    - Regenerates documentation.json
#    - Commits the regenerated files (if auto-commit enabled)
#    - Builds and deploys to Azure
```

---

## Need Help?

1. Check the workflow run logs: `Actions` tab → Click on the run
2. Run locally first: `npm run ci-update-docs`
3. Verify `SUMMARY.md` is correct (the generator depends on it)
