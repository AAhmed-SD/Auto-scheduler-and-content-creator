#!/usr/bin/env python3
"""Script to fix common style issues in Python files."""

import os

def fix_file(filepath):
    """Fix style issues in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix trailing whitespace
    lines = content.splitlines()
    lines = [line.rstrip() for line in lines]
    
    # Ensure final newline
    content = '\n'.join(lines) + '\n'
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    """Main function to fix style issues in all Python files."""
    for root, _, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                fix_file(filepath)

if __name__ == '__main__':
    main() 