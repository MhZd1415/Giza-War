#!/usr/bin/env python
"""
File Organization Script for Tank Game

This script identifies and handles files that might be in the wrong place
in the directory structure. It should be run from the root directory of the
game project.

Usage:
    python move_files.py [--dry-run]

Options:
    --dry-run   Show what files would be moved without actually moving them
"""

import os
import shutil
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("file_organizer")

# File types and their target directories
FILE_DESTINATIONS = {
    # Entity files belong in the entities directory
    'player.py': 'entities/',
    'enemy.py': 'entities/',
    'projectile.py': 'entities/',
    'bullet.py': 'entities/',
    'drop.py': 'entities/',
    
    # UI files belong in the ui directory
    'button.py': 'ui/',
    'floating_text.py': 'ui/',
    'hud.py': 'ui/',
    'shop.py': 'ui/',
    'upgrades.py': 'ui/',
    
    # World files belong in the world directory
    'world_map.py': 'world/',
    
    # Utility files belong in the utils directory
    'constants.py': 'utils/',
    'config.py': 'utils/',
    'debug.py': 'utils/',
}

# Files that should not be moved automatically
DO_NOT_MOVE = [
    'main.py',
    'game.py',
    'move_files.py',
    '__init__.py',
    'README.md',
    'LICENSE',
    '.gitignore',
]

def scan_for_misplaced_files(root_dir='.'):
    """
    Scan the project directory for misplaced files
    
    Args:
        root_dir (str): Root directory to scan
        
    Returns:
        list: List of (source_path, destination_path) tuples for misplaced files
    """
    misplaced_files = []
    
    # Check all Python files in the root directory
    for filename in os.listdir(root_dir):
        # Skip directories and non-Python files
        if os.path.isdir(os.path.join(root_dir, filename)) or not filename.endswith('.py'):
            continue
            
        # Skip files that should stay in the root
        if filename in DO_NOT_MOVE:
            continue
            
        # Check if this file has a destination
        if filename in FILE_DESTINATIONS:
            dest_dir = FILE_DESTINATIONS[filename]
            
            # Make sure the destination directory exists
            dest_dir_path = os.path.join(root_dir, dest_dir)
            if not os.path.exists(dest_dir_path):
                logger.warning(f"Destination directory {dest_dir} doesn't exist, creating it")
                os.makedirs(dest_dir_path, exist_ok=True)
                
            source_path = os.path.join(root_dir, filename)
            dest_path = os.path.join(dest_dir_path, filename)
            
            # Only mark as misplaced if the file doesn't already exist in the destination
            if not os.path.exists(dest_path):
                misplaced_files.append((source_path, dest_path))
            else:
                logger.warning(f"File {filename} exists in both root and destination!")
    
    return misplaced_files

def move_misplaced_files(misplaced_files, dry_run=False):
    """
    Move misplaced files to their correct destinations
    
    Args:
        misplaced_files (list): List of (source_path, destination_path) tuples
        dry_run (bool): If True, don't actually move files
        
    Returns:
        int: Number of files moved
    """
    moved_count = 0
    
    for source, dest in misplaced_files:
        logger.info(f"{'Would move' if dry_run else 'Moving'} {source} to {dest}")
        
        if not dry_run:
            try:
                # Create a backup of the source file with .bak extension
                backup_file = source + '.bak'
                shutil.copy2(source, backup_file)
                logger.info(f"Created backup at {backup_file}")
                
                # Add a deprecation notice to the original file
                with open(source, 'r') as f:
                    content = f.read()
                
                # Check if file already has docstring
                if content.strip().startswith('"""') or content.strip().startswith("'''"):
                    # Add warning after existing docstring
                    lines = content.split('\n')
                    docstring_end = 0
                    in_docstring = False
                    quote_style = None
                    
                    for i, line in enumerate(lines):
                        if i == 0 and (line.strip().startswith('"""') or line.strip().startswith("'''")):
                            in_docstring = True
                            quote_style = line.strip()[0:3]
                        elif in_docstring and line.strip().endswith(quote_style):
                            docstring_end = i + 1
                            break
                    
                    if docstring_end > 0:
                        warning = f"\nimport logging\nlogging.warning('This file is deprecated. Use {os.path.basename(dest)} from {os.path.dirname(dest)} instead.')\n"
                        lines.insert(docstring_end, warning)
                        content = '\n'.join(lines)
                else:
                    # Add new docstring with warning
                    filename = os.path.basename(source)
                    warning = f'"""\nDEPRECATED FILE - This file has been moved to {os.path.dirname(dest)}\n\nThis file is kept for backward compatibility only.\nYou should import from {os.path.splitext(filename)[0]} instead.\n"""\n\n'
                    content = warning + content
                
                with open(source, 'w') as f:
                    f.write(content)
                
                # Copy to destination
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(source, dest)
                moved_count += 1
                
            except Exception as e:
                logger.error(f"Error moving {source} to {dest}: {e}")
    
    return moved_count

def main():
    parser = argparse.ArgumentParser(description="Organize the project file structure")
    parser.add_argument('--dry-run', action='store_true', 
                      help="Show what files would be moved without making changes")
    args = parser.parse_args()
    
    logger.info(f"Scanning project for misplaced files {'(dry run)' if args.dry_run else ''}")
    
    misplaced_files = scan_for_misplaced_files()
    
    if not misplaced_files:
        logger.info("No misplaced files found!")
        return
        
    logger.info(f"Found {len(misplaced_files)} misplaced files")
    
    moved_count = move_misplaced_files(misplaced_files, args.dry_run)
    
    if args.dry_run:
        logger.info(f"Would have moved {moved_count} files")
    else:
        logger.info(f"Successfully moved {moved_count} files")
        logger.info("Original files have been kept with deprecation notices")
    
if __name__ == "__main__":
    main() 