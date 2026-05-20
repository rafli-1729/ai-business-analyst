from sqlalchemy import text
from typing import List, Dict, Any


def list_tables(engine, schema_names: List[str] = ["gold", "silver"]) -> List[Dict[str, str]]:
    """Lists all tables and views in the specified schemas including their descriptions."""
    query = text(
        """
        SELECT 
            t.table_schema, 
            t.table_name, 
            t.table_type,
            obj_description(c.oid, 'pg_class') as description
        FROM information_schema.tables t
        JOIN pg_class c ON c.relname = t.table_name
        JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.table_schema
        WHERE t.table_schema IN :schemas
        ORDER BY t.table_schema, t.table_name
        """
    )
    with engine.connect() as conn:
        result = conn.execute(query, {"schemas": tuple(schema_names)})
        return [
            {"schema": row[0], "table": row[1], "type": row[2], "description": row[3] or ""} 
            for row in result
        ]


def describe_table(engine, schema_name: str, table_name: str) -> Dict[str, Any]:
    """Provides a detailed description of a table including columns (with comments), PKs, and FKs."""
    
    # Get columns with descriptions
    cols_query = text(
        """
        SELECT 
            cols.column_name, 
            cols.data_type, 
            cols.is_nullable,
            col_description(c.oid, cols.ordinal_position) as description
        FROM information_schema.columns cols
        JOIN pg_class c ON c.relname = :table
        JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = :schema
        WHERE cols.table_schema = :schema AND cols.table_name = :table
        ORDER BY cols.ordinal_position
        """
    )
    
    # Get Primary Keys
    pk_query = text(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = :schema
          AND tc.table_name = :table
        """
    )

    # Get Foreign Keys
    fk_query = text(
        """
        SELECT
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = :schema
          AND tc.table_name = :table
        """
    )

    with engine.connect() as conn:
        cols = conn.execute(cols_query, {"schema": schema_name, "table": table_name}).fetchall()
        pks = conn.execute(pk_query, {"schema": schema_name, "table": table_name}).fetchall()
        fks = conn.execute(fk_query, {"schema": schema_name, "table": table_name}).fetchall()
        
        return {
            "schema": schema_name,
            "table": table_name,
            "columns": [
                {"name": row[0], "type": row[1], "nullable": row[2], "description": row[3] or ""} 
                for row in cols
            ],
            "primary_keys": [r[0] for r in pks],
            "foreign_keys": [
                {"column": r[0], "ref_schema": r[1], "ref_table": r[2], "ref_column": r[3]}
                for r in fks
            ]
        }


def table_exists(engine, schema_name: str, table_name: str) -> bool:
    query = text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = :s AND table_name = :t)"
    )
    with engine.connect() as conn:
        return bool(conn.execute(query, {"s": schema_name, "t": table_name}).scalar())
