from sqlalchemy import text, event
from sqlalchemy.engine import Engine
import logging
import time

logger = logging.getLogger(__name__)

# ✅ Log slow queries (over 100ms)
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info["query_start_time"].pop(-1)
    if total > 0.1:  # 100ms threshold
        logger.warning(f"SLOW QUERY ({total:.3f}s): {statement[:100]}")

def get_db_stats(db):
    """Get database statistics"""
    try:
        result = db.execute(text("""
            SELECT
                schemaname,
                tablename,
                n_live_tup as row_count,
                n_dead_tup as dead_rows,
                last_vacuum,
                last_analyze
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC
        """))
        tables = []
        for row in result:
            tables.append({
                "table": row.tablename,
                "rows": row.row_count,
                "dead_rows": row.dead_rows,
            })
        return tables
    except Exception as e:
        logger.error(f"DB stats error: {e}")
        return []

def get_index_usage(db):
    """Get index usage statistics"""
    try:
        result = db.execute(text("""
            SELECT
                tablename,
                indexname,
                idx_scan as scans
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            LIMIT 10
        """))
        return [{"table": r.tablename, "index": r.indexname, "scans": r.scans}
                for r in result]
    except Exception as e:
        logger.error(f"Index stats error: {e}")
        return []