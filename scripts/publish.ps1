# PowerShell script to increment the version, commit changes, and push a new tag

# Extract the current version
$current_version = python setup.py --version

# Increment the version (simple approach: increase the patch number)
$version_parts = $current_version -split '\.'
$version_parts[2] = [int]$version_parts[2] + 1
$new_version = "$($version_parts[0]).$($version_parts[1]).$($version_parts[2])"

# Update the version in setup.py
(Get-Content setup.py) -replace "version='$current_version'", "version='$new_version'" | Set-Content setup.py

# Commit the changes and push
git add setup.py
git commit -m "Bump version to $new_version"
git tag "v$new_version"
git push origin main --tags