import sqlalchemy
from datetime import datetime
from warehouse.ingestion.config import load_ingestion_config

def log_pipeline_execution(pipeline_name: str, task_name: str, status: str, rows_processed: int = 0):
    config = load_ingestion_config()
    engine = sqlalchemy.create_engine(config.database_url)
    
    with engine.begin() as conn:
        conn.execute(
            sqlalchemy.text("""
                INSERT INTO ops.run_logs (pipeline_name, task_name, start_time, end_time, rows_processed, status)
                VALUES (:pipeline, :task, :start, :end, :rows, :status)
            """),
            {
                "pipeline": pipeline_name,
                "task": task_name,
                "start": datetime.now(),
                "end": datetime.now(),
                "rows": rows_processed,
                "status": status
            }
        )
