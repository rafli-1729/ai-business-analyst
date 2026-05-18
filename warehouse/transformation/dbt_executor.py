import subprocess
import logging

logger = logging.getLogger(__name__)

def run_dbt_tests():
    logger.info("Running dbt tests...")
    try:
        # Menjalankan dbt test. Pastikan dbt terkonfigurasi di env.
        result = subprocess.run(["dbt", "test"], capture_output=True, text=True, check=True)
        logger.info(f"dbt test results: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"dbt tests failed: {e.stderr}")
        return False
