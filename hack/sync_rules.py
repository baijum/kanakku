import yaml
import os
import sys
from pathlib import Path

def load_yaml_file(file_path):
    """Safely load a YAML file with error handling."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return None

def convert_rule_to_markdown(rule):
    """Convert a single rule to markdown format."""
    markdown = []
    
    # Handle rule name/header
    name = rule.get('name', 'Unnamed Rule')
    if isinstance(name, str):
        markdown.append(f"## {name.replace('_', ' ').title()}")
    else:
        markdown.append("## Rule")
    
    # Add description if exists
    if 'description' in rule and rule['description']:
        markdown.append(f"\n{rule['description']}\n")
    
    # Add content if exists
    if 'content' in rule and rule['content']:
        content = rule['content']
        if isinstance(content, str):
            markdown.append(f"{content}\n")
        elif isinstance(content, list):
            markdown.append('\n'.join(f"- {item}" if isinstance(item, str) else str(item) 
                                     for item in content) + '\n')
    
    # Add applies_to if exists
    if 'applies_to' in rule and rule['applies_to']:
        markdown.append(f"\n**Applies to:** {rule['applies_to']}\n")
    
    return '\n'.join(markdown) + '\n\n'

def convert_to_mdc(yaml_path, output_dir):
    """Convert a YAML rules file to MDC format."""
    data = load_yaml_file(yaml_path)
    if not data:
        print(f"Skipping {yaml_path} due to load error")
        return
    
    # Convert YAML structure to MDC format
    mdc_content = [
        "---",
        f"description: {data.get('description', '')}",
        'globs: "**/*"',
        'alwaysApply: true',
        '---\n'
    ]
    
    # Handle both list and dictionary formats for rules
    rules = data.get('rules', [])
    if isinstance(rules, dict):
        rules = [{'name': k, **v} for k, v in rules.items()]
    elif not isinstance(rules, list):
        rules = []
    
    # Process each rule
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        mdc_content.append(convert_rule_to_markdown(rule))
    
    # Write to output file
    output_path = output_dir / f"{yaml_path.stem}.mdc"
    with open(output_path, 'w') as f:
        f.write('\n'.join(mdc_content))
    print(f"Generated: {output_path}")

def main():
    # Set up paths
    repo_root = Path(__file__).parent.parent
    windsurf_rules_dir = repo_root / '.windsurf' / 'rules'
    cursor_rules_dir = repo_root / '.cursor' / 'rules'
    
    # Ensure output directory exists
    os.makedirs(cursor_rules_dir, exist_ok=True)
    
    # Process each YAML file
    for yaml_file in windsurf_rules_dir.glob('*.yml'):
        if yaml_file.name != '_template.yml':
            convert_to_mdc(yaml_file, cursor_rules_dir)

if __name__ == "__main__":
    main()