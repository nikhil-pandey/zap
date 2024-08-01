#!/bin/bash
set -e

# Extract the current version
current_version=$(python setup.py --version)

# Increment the version (simple approach: increase the patch number)
IFS='.' read -r -a version_parts <<< "$current_version"
version_parts[2]=$((version_parts[2] + 1))
new_version="${version_parts[0]}.${version_parts[1]}.${version_parts[2]}"

# Update the version in setup.py
sed -i "s/version='$current_version'/version='$new_version'/" setup.py

# Commit the changes and push
git add setup.py
git commit -m "Bump version to $new_version"
git tag "v$new_version"
git push origin main --tags