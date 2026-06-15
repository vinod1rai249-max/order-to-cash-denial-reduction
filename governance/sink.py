import logging
import datetime
import json
import os
from dotenv import load_dotenv

# Load config
load_dotenv()

logger = logging.getLogger(__name__)

# Config
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET")
TABLE_ID = os.getenv("BQ_TABLE")

# Global variables
LOG_HISTORY = []
_bq_client = None

def _get_bq_client():
    """Lazy initialization of BigQuery client."""
    global _bq_client
    if _bq_client is None:
        try:
            from google.cloud import bigquery
            _bq_client = bigquery.Client(project=PROJECT_ID)
            logger.info(f"BigQuery Client initialized.")
        except Exception as e:
            logger.warning(f"BigQuery initialization failed: {str(e)}. Using local logs only.")
            _bq_client = False # Use False to indicate failed attempt
    return _bq_client if _bq_client is not False else None

def log_to_governance_sink(agent: str, action: str, details: str, confidence: float, payload: dict):
    """
    Streams decision logs directly to Google BigQuery.
    """
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "agent": agent,
        "action": action,
        "details": details,
        "confidence": confidence,
        "payload": json.dumps(payload)
    }
    
    # 1. Store locally for tests and immediate dashboard feedback
    LOG_HISTORY.append(log_entry)
    logger.info(f"GOVERNANCE_SINK_LOG: {agent} -> {action}: {details}")

    # 2. Stream to real BigQuery if available
    client = _get_bq_client()
    if client:
        try:
            full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
            client.insert_rows_json(full_table_id, [log_entry])
        except Exception as e:
            logger.error(f"Failed to stream to BigQuery: {str(e)}")
    
    return True

def get_logs():
    """
    Returns latest logs. Prefers local cache for demo performance.
    """
    return list(reversed(LOG_HISTORY))[:50]
