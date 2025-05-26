import os
import sys
from pathlib import Path

import yaml


def load_yaml_file(file_path):
    """Safely load a YAML file with error handling."""
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return None


def clean_markdown_content(text):
    """Clean up markdown content by ensuring consistent single blank lines."""
    if not text:
        return text

    import re

    # Normalize all line endings to \n and remove trailing whitespace
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]

    # Process lines to ensure single blank lines
    cleaned_lines = []
    prev_was_blank = False

    for line in lines:
        is_blank = not line.strip()

        # Skip multiple consecutive blank lines
        if is_blank and prev_was_blank:
            continue

        cleaned_lines.append(line)
        prev_was_blank = is_blank

    # Join with single newlines and ensure exactly one at the end
    result = "\n".join(cleaned_lines).strip() + "\n"

    # Ensure exactly one blank line before headers
    result = re.sub(r"([^\n])(\n## )", r"\1\n\n## ", result)

    # Fix any double blank lines that might have been introduced
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result


def convert_rule_to_markdown(rule):
    """Convert a single rule to markdown format with clean formatting."""
    markdown = []

    # Handle rule name/header
    name = rule.get("name", "Unnamed Rule")
    if isinstance(name, str):
        markdown.append(f"## {name.replace('_', ' ').title()}")
    else:
        markdown.append("## Rule")

    # Add description if exists
    if "description" in rule and rule["description"]:
        markdown.append(rule["description"])

    # Add content if exists
    if "content" in rule and rule["content"]:
        content = rule["content"]
        if isinstance(content, str):
            markdown.append(content)
        elif isinstance(content, list):
            items = []
            for item in content:
                if isinstance(item, str):
                    items.append(f"- {item}")
                elif (
                    isinstance(item, dict) and "name" in item and "description" in item
                ):
                    items.append(f"- **{item['name']}**: {item['description']}")
                else:
                    items.append(f"- {str(item)}")
            markdown.append("\n".join(items))

    # Add applies_to if exists
    if "applies_to" in rule and rule["applies_to"]:
        markdown.append(f"**Applies to:** {rule['applies_to']}")

    # Join all non-empty parts with single newlines
    result = "\n".join(part.strip() for part in markdown if part and part.strip())

    # Clean up any remaining spacing issues
    return clean_markdown_content(result) + "\n"


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
        "alwaysApply: true",
        "---\n",
    ]

    # Handle both list and dictionary formats for rules
    rules = data.get("rules", [])
    if isinstance(rules, dict):
        rules = [{"name": k, **v} for k, v in rules.items()]
    elif not isinstance(rules, list):
        rules = []

    # Process each rule
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        mdc_content.append(convert_rule_to_markdown(rule))

    # Write to output file
    output_path = output_dir / f"{yaml_path.stem}.mdc"
    with open(output_path, "w") as f:
        f.write("\n".join(mdc_content))
    print(f"Generated: {output_path}")


def main():
    # Set up paths
    repo_root = Path(__file__).parent.parent
    windsurf_rules_dir = repo_root / ".windsurf" / "rules"
    cursor_rules_dir = repo_root / ".cursor" / "rules"

    # Ensure output directory exists
    os.makedirs(cursor_rules_dir, exist_ok=True)

    # Remove existing index.mdc if it exists
    index_mdc = cursor_rules_dir / "index.mdc"
    if index_mdc.exists():
        os.remove(index_mdc)

    # Process each YAML file except index.yml and _template.yml
    for yaml_file in windsurf_rules_dir.glob("*.yml"):
        if yaml_file.name not in ["_template.yml", "index.yml"]:
            convert_to_mdc(yaml_file, cursor_rules_dir)


if __name__ == "__main__":
    main()
