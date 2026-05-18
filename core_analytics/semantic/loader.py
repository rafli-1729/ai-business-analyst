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
            columns = ", ".join(data.get('columns', {}).keys())
            context += f"Table: {table_name} | Columns: {columns}\n"
    
    return context
