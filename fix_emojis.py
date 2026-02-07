#!/usr/bin/env python3
"""
Remove emoji characters from Python files for Windows compatibility
"""

import re

def remove_emojis_from_file(file_path):
    """Remove emoji characters from a file"""
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace common emojis with text alternatives
    emoji_replacements = {
        '🎨': '[ART]',
        '🔑': '[KEY]',
        '🔍': '[SEARCH]',
        '📝': '[NOTE]',
        '📐': '[RATIO]',
        '🎭': '[STYLE]',
        '⭐': '[QUALITY]',
        '🚀': '[LAUNCH]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⏳': '[WAIT]',
        '🌐': '[WEB]',
        '🖼️': '[IMAGE]',
        '✨': '[SPARKLE]',
        '👋': '[BYE]',
        '🔄': '[RELOAD]',
        '📤': '[SEND]',
        '📡': '[RECEIVE]',
        '🏠': '[HOME]',
        '🎯': '[TARGET]',
        '🔧': '[TOOLS]',
        '📊': '[DATA]',
        '⏰': '[TIME]',
        '🗂️': '[FOLDER]'
    }
    
    # Replace emojis
    new_content = content
    for emoji, replacement in emoji_replacements.items():
        new_content = new_content.replace(emoji, replacement)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed emojis in {file_path}")

def main():
    """Fix emojis in all Python files"""
    files_to_fix = [
        'modern_generators.py',
        'app.py'
    ]
    
    for file_path in files_to_fix:
        try:
            remove_emojis_from_file(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")

if __name__ == "__main__":
    main()
