import os
import yaml
from pathlib import Path

def load_all_semantic_definitions() -> str:
    # Changed path from core_analytics/semantic/schemas to contracts/schemas
    definitions_dir = Path("contracts/schemas")
    if not definitions_dir.exists():
        return "Error: Schema definitions directory not found at " + str(definitions_dir.absolute())
        
    context = "Available Tables and Columns:\n"
    
    found_files = list(definitions_dir.glob("*_semantic.yml"))
    if not found_files:
        return "Error: No schema files found."

    for yaml_file in found_files:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
            table_name = data.get('table', 'unknown')
            context += f"\nTable: {table_name}\nColumns:\n"
            for col_name, col_meta in data.get('columns', {}).items():
                desc = col_meta.get('description', '')
                examples = col_meta.get('examples', [])
                example_str = f" | Examples: {examples}" if examples else ""
                context += f"- {col_name}: {desc}{example_str}\n"
    
    return context
