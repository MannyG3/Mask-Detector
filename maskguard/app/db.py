import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from app.config import DB_PATH

def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            source TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            track_id TEXT,
            snapshot_path TEXT,
            meta TEXT
        )
    """)
    
    # Create indexes for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_source ON events(source)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_label ON events(label)
    """)
    
    conn.commit()
    conn.close()

def log_event(
    source: str,
    label: str,
    confidence: float,
    track_id: Optional[str] = None,
    snapshot_path: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> int:
    """
    Log a detection event to the database.
    
    Args:
        source: Event source (live, image, video)
        label: Detection label (MASK_ON, NO_MASK, MASK_INCORRECT)
        confidence: Prediction confidence (0.0-1.0)
        track_id: Optional track ID for live detections
        snapshot_path: Optional path to snapshot image
        meta: Optional additional metadata
    
    Returns:
        The ID of the inserted event
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    ts = datetime.utcnow().isoformat()
    meta_json = json.dumps(meta) if meta else None
    
    cursor.execute("""
        INSERT INTO events (ts, source, label, confidence, track_id, snapshot_path, meta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ts, source, label, confidence, track_id, snapshot_path, meta_json))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return event_id

def query_events(
    source: Optional[str] = None,
    label: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0
) -> list:
    """
    Query events with optional filters.
    
    Args:
        source: Filter by source
        label: Filter by label
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        limit: Maximum number of results
        offset: Result offset for pagination
    
    Returns:
        List of event dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM events WHERE 1=1"
    params = []
    
    if source:
        query += " AND source = ?"
        params.append(source)
    
    if label:
        query += " AND label = ?"
        params.append(label)
    
    if start_date:
        query += " AND ts >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND ts <= ?"
        params.append(end_date)
    
    query += " ORDER BY ts DESC"
    
    if limit:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        event = dict(row)
        if event['meta']:
            event['meta'] = json.loads(event['meta'])
        events.append(event)
    
    return events

def get_stats_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get summary statistics for events.
    
    Args:
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
    
    Returns:
        Dictionary with summary statistics
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    where_clause = "WHERE 1=1"
    params = []
    
    if start_date:
        where_clause += " AND ts >= ?"
        params.append(start_date)
    
    if end_date:
        where_clause += " AND ts <= ?"
        params.append(end_date)
    
    # Total events
    cursor.execute(f"SELECT COUNT(*) as total FROM events {where_clause}", params)
    total = cursor.fetchone()['total']
    
    # Count by label
    cursor.execute(f"""
        SELECT label, COUNT(*) as count
        FROM events
        {where_clause}
        GROUP BY label
    """, params)
    by_label = {row['label']: row['count'] for row in cursor.fetchall()}
    
    # Count by source
    cursor.execute(f"""
        SELECT source, COUNT(*) as count
        FROM events
        {where_clause}
        GROUP BY source
    """, params)
    by_source = {row['source']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        'total': total,
        'by_label': by_label,
        'by_source': by_source
    }
