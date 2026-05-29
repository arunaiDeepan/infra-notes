#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def format_mock_file(file_path: Path):
    content = file_path.read_text(encoding='utf-8')

    # Split the document by the horizontal rules
    questions = re.split(r'\n---\n+', content)
    
    formatted_questions = []
    
    for q in questions:
        if not q.strip():
            continue
            
        # 1. Format the Question Header (e.g., "1. " -> "### Question 1")
        q = re.sub(r'^(\d+)\.\s*', r'### Question \1\n\n', q.lstrip())
        
        # 2. Format the Answer Section
        q = re.sub(r'^[ \t]*\**Ans:\**[ \t]*\n?[ \t]*', r'**Answer:**\n\n', q, flags=re.MULTILINE)
        
        # 3. Format the Overall Explanation Section
        q = re.sub(r'^[ \t]*\**Overall explanation\**[ \t]*\n?[ \t]*', r'\n**Overall Explanation:**\n\n', q, flags=re.MULTILINE|re.IGNORECASE)
        
        # 4. Format the Domain Section
        q = re.sub(r'^[ \t]*Domain\s+(.*)', r'\n**Domain:** \1', q, flags=re.MULTILINE)
        
        # 5. Clean up improper indentation (tabs and leading spaces) while preserving code blocks
        code_blocks = q.split('```')
        cleaned_blocks = []
        for i, block_content in enumerate(code_blocks):
            if i % 2 == 1:
                # Inside a code block: keep as is
                cleaned_blocks.append(block_content)
            else:
                # Outside a code block: remove leading spaces and tabs
                lines = block_content.split('\n')
                cleaned_lines = [line.lstrip(' \t') for line in lines]
                cleaned_blocks.append('\n'.join(cleaned_lines))
                
        cleaned_text = '```'.join(cleaned_blocks)
        
        # Remove consecutive blank lines
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        formatted_questions.append(cleaned_text.strip())

    # Join all formatted questions with a horizontal rule
    formatted_content = '\n\n---\n\n'.join(formatted_questions)
    
    # Save the formatted content back to the file
    file_path.write_text(formatted_content + '\n', encoding='utf-8')
    print(f"Successfully formatted {file_path.name}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python format_mock_set.py <path_to_markdown_file>")
        sys.exit(1)
        
    target_file = Path(sys.argv[1])
    if target_file.exists():
        format_mock_file(target_file)
    else:
        print(f"File not found: {target_file}")