import pandas as pd
from sqlalchemy import text
from infra.config.settings import get_settings
from infra.database.engine import create_postgres_engine

def get_table_metadata(engine, schema, table):
    # Get column info
    query = text(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = '{schema}' AND table_name = '{table}'
    """)
    with engine.connect() as conn:
        cols = pd.read_sql(query, conn)
    
    # Get sample data for examples (first 5 rows)
    data_query = text(f"SELECT * FROM {schema}.{table} LIMIT 20")
    with engine.connect() as conn:
        samples = pd.read_sql(data_query, conn)
        
    return cols, samples

def main():
    settings = get_settings()
    engine = create_postgres_engine(settings.database_url)
    tables = [
        'fact_sales_items', 
        'fact_order_fulfillment', 
        'mart_monthly_performance', 
        'mart_customer_behavior', 
        'mart_seller_performance', 
        'mart_product_performance'
    ]
    
    for table in tables:
        print(f"--- Metadata for {table} ---")
        cols, samples = get_table_metadata(engine, 'gold', table)
        print("Columns:")
        print(cols.to_string())
        print("\nCategorical Examples:")
        for col in samples.columns:
            unique_vals = samples[col].unique()
            # If string and relatively short/categorical
            if samples[col].dtype == 'object' and len(str(unique_vals[0])) < 50:
                print(f"{col}: {unique_vals[:5].tolist()}")
        print("\n")

if __name__ == "__main__":
    main()
