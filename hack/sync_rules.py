import yaml
import os
from pathlib import Path

WINSURF_RULES_DIR = Path('.windsurf/rules')
CURSOR_RULES_DIR = Path('.cursor/rules')

def convert_to_mdc(yaml_path, output_dir):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Convert YAML structure to MDC format
    mdc_content = "---\n"
    mdc_content += f"description: {data.get('description', '')}\n"
    mdc_content += f"globs: \"**/*\"\n"
    mdc_content += "alwaysApply: true\n"
    mdc_content += "---\n\n"
    
    # Add rules content
    for rule in data.get('rules', []):
        mdc_content += f"## {rule['name'].replace('_', ' ').title()}\n\n"
        mdc_content += f"{rule.get('description', '')}\n\n"
        mdc_content += f"{rule.get('content', '')}\n\n"
    
    # Write to Cursor rules directory
    output_path = output_dir / f"{yaml_path.stem}.mdc"
    with open(output_path, 'w') as f:
        f.write(mdc_content)

def main():
    # Ensure Cursor rules directory exists
    os.makedirs(CURSOR_RULES_DIR, exist_ok=True)
    
    # Convert all YAML files
    for yaml_file in WINSURF_RULES_DIR.glob('*.yml'):
        if yaml_file.name != '_template.yml':  # Skip template
            convert_to_mdc(yaml_file, CURSOR_RULES_DIR)

if __name__ == "__main__":
    main()