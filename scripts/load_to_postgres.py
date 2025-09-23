#!/usr/bin/env python3
"""
scripts/load_to_postgres.py

Usage:
  - Ensure Postgres/PostGIS container is running (docker compose up -d)
  - Install requirements: pip install pandas sqlalchemy psycopg2-binary
  - Optionally set environment variables:
       DB_URL  (default: postgresql+psycopg2://postgres:mysecret@localhost:5432/floatchat)
       CSV_FILE (default: data/processed/argo_profiles_final_cleaned.csv)
  - Run: python scripts/load_to_postgres.py
"""

import os
import time
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# ------------------------------------------------------------
# Config (can be overridden via environment)
# ------------------------------------------------------------
DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://postgres:mysecret@localhost:5432/floatchat"
)
CSV_FILE = os.getenv(
    "CSV_FILE",
    "data/processed/argo_profiles_final_cleaned.csv"
)

# CSV read chunk size (tune based on memory)
CHUNKSIZE = int(os.getenv("CHUNKSIZE", "5000"))

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("loader")

# ------------------------------------------------------------
# Create SQLAlchemy engine with pre-ping to avoid stale connections
# ------------------------------------------------------------
engine = create_engine(DB_URL, pool_pre_ping=True, echo=False)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def wait_for_db(max_retries=12, wait_seconds=5):
    """Wait until DB is reachable (retries)."""
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                r = conn.execute(text("SELECT 1")).scalar()
                log.info("DB reachable (attempt %d/%d).", attempt, max_retries)
                return True
        except OperationalError as e:
            log.warning("DB not reachable (attempt %d/%d): %s", attempt, max_retries, e)
            time.sleep(wait_seconds)
    log.error("DB not reachable after %d attempts.", max_retries)
    return False


# ------------------------------------------------------------
# Initialize DB: enable PostGIS, create observations table if missing
# ------------------------------------------------------------
def init_db():
    log.info("Ensuring PostGIS extension and observations table exist...")
    sql = """
    CREATE EXTENSION IF NOT EXISTS postgis;

    CREATE TABLE IF NOT EXISTS observations (
        observation_id SERIAL PRIMARY KEY,
        float_id VARCHAR(50) NOT NULL,
        cycle INT NOT NULL,
        obs_time TIMESTAMP NOT NULL,
        lat DOUBLE PRECISION NOT NULL,
        lon DOUBLE PRECISION NOT NULL,
        geom GEOMETRY(Point, 4326),
        depth DOUBLE PRECISION,
        variable VARCHAR(10) NOT NULL,  -- TEMP or PSAL
        value DOUBLE PRECISION,
        qc_flag VARCHAR(50),
        created_at TIMESTAMP DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_obs_time ON observations(obs_time);
    CREATE INDEX IF NOT EXISTS idx_obs_geom ON observations USING GIST (geom);
    CREATE INDEX IF NOT EXISTS idx_obs_float_cycle ON observations(float_id, cycle);
    """
    with engine.begin() as conn:
        conn.execute(text(sql))
    log.info("Database initialized.")


# ------------------------------------------------------------
# Create staging table (and truncate)
# ------------------------------------------------------------
def create_staging():
    sql = """
    CREATE TABLE IF NOT EXISTS observations_staging (
        float_id VARCHAR(50),
        cycle INT,
        obs_time TIMESTAMP,
        lat DOUBLE PRECISION,
        lon DOUBLE PRECISION,
        pressure DOUBLE PRECISION,
        temperature DOUBLE PRECISION,
        temp_qc VARCHAR(50),
        salinity DOUBLE PRECISION,
        salinity_qc VARCHAR(50)
    );
    TRUNCATE TABLE observations_staging;
    """
    with engine.begin() as conn:
        conn.execute(text(sql))
    log.info("Staging table created and truncated.")


# ------------------------------------------------------------
# Load CSV into staging in chunks
# ------------------------------------------------------------
def load_csv_to_staging(csv_path: Path, chunksize: int = CHUNKSIZE):
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {str(csv_path)}")

    # pandas.read_csv with chunksize returns an iterator of DataFrames
    total_rows = 0
    # Try to detect 'time' column (common) or 'obs_time' already
    sample = pd.read_csv(csv_path, nrows=5)
    cols_lower = [c.lower() for c in sample.columns]
    time_col = None
    if "time" in cols_lower:
        # find original casing
        time_col = sample.columns[cols_lower.index("time")]
    elif "obs_time" in cols_lower:
        time_col = sample.columns[cols_lower.index("obs_time")]
    else:
        raise ValueError("CSV must have a 'time' or 'obs_time' column")

    usecols = None  # let pandas read all then filter; ensures we don't miss columns

    log.info("Loading CSV into staging using chunksize=%d. Detected time column: %s", chunksize, time_col)
    reader = pd.read_csv(csv_path, parse_dates=[time_col], chunksize=chunksize, iterator=True)

    for i, chunk in enumerate(reader, start=1):
        # normalize column names: ensure columns we need exist
        chunk = chunk.rename(columns={time_col: "obs_time"})
        expected = ['float_id','cycle','obs_time','lat','lon','pressure','temperature','temp_qc','salinity','salinity_qc']
        missing = [c for c in expected if c not in chunk.columns]
        if missing:
            # If some QC columns missing, create them with NaN
            for m in missing:
                chunk[m] = None

        df = chunk[expected].copy()
        # Append to staging table
        df.to_sql('observations_staging', engine, if_exists='append', index=False, method='multi', chunksize=1000)
        total_rows += len(df)
        log.info("Chunk %d: appended %d rows (total %d)", i, len(df), total_rows)

    log.info("Finished loading CSV to staging. Total rows: %d", total_rows)


# ------------------------------------------------------------
# Insert normalized rows into observations
# ------------------------------------------------------------
def insert_into_observations():
    log.info("Inserting TEMP rows into observations...")
    insert_temp = """
    INSERT INTO observations (float_id, cycle, obs_time, lat, lon, geom, depth, variable, value, qc_flag)
    SELECT float_id, cycle, obs_time, lat, lon,
           ST_SetSRID(ST_MakePoint(lon, lat), 4326),
           pressure,
           'TEMP',
           temperature,
           temp_qc
    FROM observations_staging
    WHERE temperature IS NOT NULL;
    """

    log.info("Inserting PSAL rows into observations...")
    insert_sal = """
    INSERT INTO observations (float_id, cycle, obs_time, lat, lon, geom, depth, variable, value, qc_flag)
    SELECT float_id, cycle, obs_time, lat, lon,
           ST_SetSRID(ST_MakePoint(lon, lat), 4326),
           pressure,
           'PSAL',
           salinity,
           salinity_qc
    FROM observations_staging
    WHERE salinity IS NOT NULL;
    """

    with engine.begin() as conn:
        before = conn.execute(text("SELECT COUNT(*) FROM observations")).scalar()
        conn.execute(text(insert_temp))
        conn.execute(text(insert_sal))
        after = conn.execute(text("SELECT COUNT(*) FROM observations")).scalar()
    inserted = after - before
    log.info("Inserted %d new rows into observations (before=%d, after=%d).", inserted, before, after)


# ------------------------------------------------------------
# Cleanup staging (optional)
# ------------------------------------------------------------
def cleanup_staging():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE observations_staging;"))
    log.info("Staging table truncated (clean).")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    log.info("Starting CSV -> Postgres loader")
    csv_path = Path(CSV_FILE)
    log.info("CSV path: %s", csv_path.resolve())
    log.info("DB URL: %s", DB_URL.split("@")[0] + "@<host_port>")  # don't print password

    if not wait_for_db():
        raise RuntimeError("Database not reachable. Start Postgres container or check DB_URL.")

    init_db()
    create_staging()
    load_csv_to_staging(csv_path, chunksize=CHUNKSIZE)
    insert_into_observations()
    cleanup_staging()
    log.info("All done — CSV loaded into observations.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("Loader failed: %s", e)
        raise
