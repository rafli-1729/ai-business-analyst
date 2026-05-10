from services.schema_loader import load_schema_metadata, render_schema_for_prompt

SCHEMA = render_schema_for_prompt(load_schema_metadata())
