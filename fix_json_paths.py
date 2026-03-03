#!/usr/bin/env python3
"""
Fix all JSON files to use Windows-compatible paths in all projects.
"""

import json
import os
from pathlib import Path

def fix_paths_in_json(json_file):
    """Convert JSON file paths to Windows-compatible format."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # Recursively fix all string values that look like paths
        def fix_path_recursively(obj):
            nonlocal modified
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str):
                        # Check if it looks like a path with forward slashes
                        if '/' in value and ('Data_visualization' in value or 'data' in value or 'config' in value or 'scripts' in value):
                            # Convert to Windows path using backslashes
                            fixed_value = value.replace('/', '\\')
                            if fixed_value != value:
                                obj[key] = fixed_value
                                modified = True
                                print(f"  Fixed: {key}")
                    elif isinstance(value, (dict, list)):
                        fix_path_recursively(value)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        fix_path_recursively(item)
        
        fix_path_recursively(data)
        
        # Write back if modified
        if modified:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Fixed: {json_file}")
            return True
        else:
            print(f"  No changes needed: {json_file}")
            return False
    except Exception as e:
        print(f"ERROR processing {json_file}: {e}")
        return False

# Process Data_visualization project
print("=" * 70)
print("Fixing JSON paths in Data_visualization project")
print("=" * 70)
viz_dir = Path(r'c:\Users\haujo\projects\DEV\Data_visualization')
fixed_count = 0

for json_file in viz_dir.rglob('*.json'):
    if fix_paths_in_json(str(json_file)):
        fixed_count += 1

print(f"\nData_visualization: Fixed {fixed_count} JSON files\n")

# Process X_Monetization project
print("=" * 70)
print("Fixing JSON paths in X_Monetization project")
print("=" * 70)
monetization_dir = Path(r'c:\Users\haujo\projects\DEV\X_Monetization')
if monetization_dir.exists():
    fixed_count = 0
    for json_file in monetization_dir.rglob('*.json'):
        if fix_paths_in_json(str(json_file)):
            fixed_count += 1
    print(f"\nX_Monetization: Fixed {fixed_count} JSON files\n")
else:
    print(f"Directory not found: {monetization_dir}\n")

print("=" * 70)
print("JSON path fixing complete!")
print("=" * 70)
