#!/usr/bin/env python3
"""
Quick DB connectivity test. Set DB_URL env var to test alternate credentials.
"""
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:mysecret@localhost:5432/floatchat")

engine = create_engine(DB_URL, pool_pre_ping=True, echo=False)

def try_connect(tries=5, delay=2):
    for i in range(1, tries+1):
        try:
            with engine.connect() as conn:
                v = conn.execute(text("SELECT version()")).scalar()
                print("✅ Connected to DB. Postgres version:", v)
                return True
        except OperationalError as e:
            print(f"Attempt {i}/{tries} failed: {e}")
            time.sleep(delay)
    print("❌ Could not connect to DB. Check container and DB_URL.")
    return False

if __name__ == "__main__":
    try_connect()
