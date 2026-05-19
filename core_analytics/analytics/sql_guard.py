import re

class SqlValidationError(Exception):
    """Raised when SQL fails validation."""
    pass

def validate_sql_is_read_only(sql: str) -> str:
    """
    Very basic check to ensure SQL is read-only.
    """
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
    
    cleaned_sql = sql.strip()
    # Remove markdown code blocks if present
    if cleaned_sql.startswith("```"):
        cleaned_sql = re.sub(r"```(sql)?", "", cleaned_sql).strip()
        cleaned_sql = cleaned_sql.strip("`").strip()
    
    # Simple extraction if SQL starts with text
    if "SELECT" in cleaned_sql.upper():
        start_idx = cleaned_sql.upper().find("SELECT")
        cleaned_sql = cleaned_sql[start_idx:]
    
    # Check for forbidden keywords
    upper_sql = cleaned_sql.upper()
    for word in forbidden:
        if re.search(r'\b' + word + r'\b', upper_sql):
            raise SqlValidationError(f"Forbidden keyword '{word}' found in SQL.")
            
    if not upper_sql.startswith("SELECT") and not upper_sql.startswith("WITH"):
        raise SqlValidationError("SQL must start with SELECT or WITH.")
        
    # Remove trailing semicolon
    cleaned_sql = cleaned_sql.rstrip(";")
        
    return cleaned_sql
