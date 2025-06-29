#!/bin/bash
# Script to add DCO sign-offs to existing git history
# Safe to run since this repo hasn't been shared publicly

set -e  # Exit on any error

echo "🔒 Adding DCO sign-offs to git history"
echo "======================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check current status
echo "📋 Current git status:"
git status --porcelain

if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes."
    echo "Please commit or stash them before running this script."
    echo ""
    echo "To stash: git stash"
    echo "To commit: git add -A && git commit -s -m 'Work in progress'"
    exit 1
fi

# Show current history
echo ""
echo "📜 Current commit history:"
git log --oneline --no-merges

echo ""
echo "🔄 Creating backup branch..."
git branch backup-before-dco-$(date +%Y%m%d-%H%M%S) || true

echo ""
echo "✍️  Adding DCO sign-offs to all commits..."
echo "   (This will open an editor - just save and exit without changes)"

# The magic command - rewrite all commits with sign-offs
git rebase -i --root --signoff

echo ""
echo "✅ DCO sign-offs added! Verifying..."
echo ""
echo "📜 Updated commit history with sign-offs:"
git log --pretty=format:"%h %s%n%b" --no-merges | head -20

echo ""
echo "🔍 Checking for DCO compliance:"
if git log --pretty=format:"%B" | grep -q "Signed-off-by:"; then
    echo "✅ DCO sign-offs found in commit messages"
else
    echo "❌ No DCO sign-offs found - something went wrong"
    exit 1
fi

echo ""
echo "🎉 Success! Your git history is now DCO compliant."
echo ""
echo "📤 Next steps:"
echo "1. Review the history: git log --show-signature"
echo "2. If you've pushed before: git push --force-with-lease origin main"
echo "3. If this is a new repo: git push origin main"
echo ""
echo "🧹 Cleanup backup branches later with: git branch -d backup-before-dco-*" 