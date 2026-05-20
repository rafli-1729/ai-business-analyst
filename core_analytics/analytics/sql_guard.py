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
    
    # Try to extract from markdown code blocks
    match = re.search(r"```(?:sql)?(.*?)```", cleaned_sql, re.DOTALL | re.IGNORECASE)
    if match:
        cleaned_sql = match.group(1).strip()
    # Extract if starts with SQL: prefix
    elif cleaned_sql.upper().startswith("SQL:"):
        cleaned_sql = cleaned_sql[4:].strip()
    
    # Check for forbidden keywords
    upper_sql = cleaned_sql.upper()
    for word in forbidden:
        if re.search(r'\b' + word + r'\b', upper_sql):
            raise SqlValidationError(f"Forbidden keyword '{word}' found in SQL.")
            
    if not upper_sql.startswith("SELECT") and not upper_sql.startswith("WITH"):
        raise SqlValidationError("SQL must start with SELECT or WITH.")
        
    # Check for multiple statements by counting semicolons not in quotes
    # A simple state machine approach to ignore semicolons in string literals
    statements = []
    current_stmt = []
    in_single_quote = False
    in_double_quote = False
    for char in cleaned_sql:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        
        if char == ';' and not in_single_quote and not in_double_quote:
            statements.append("".join(current_stmt).strip())
            current_stmt = []
        else:
            current_stmt.append(char)
    if "".join(current_stmt).strip():
        statements.append("".join(current_stmt).strip())
        
    statements = [s for s in statements if s]
    if len(statements) > 1:
        raise SqlValidationError("Multiple SQL statements are not allowed.")
        
    # Remove trailing semicolon
    cleaned_sql = statements[0] if statements else cleaned_sql
        
    return cleaned_sql
