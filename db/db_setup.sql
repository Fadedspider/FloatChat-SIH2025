CREATE TABLE IF NOT EXISTS observations (
    id SERIAL PRIMARY KEY,
    float_id VARCHAR(50),
    cycle INT,
    obs_time TIMESTAMP,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    depth DOUBLE PRECISION,
    temperature DOUBLE PRECISION,
    temp_qc VARCHAR(5),
    salinity DOUBLE PRECISION,
    salinity_qc VARCHAR(5),
    geom GEOMETRY(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lon, lat), 4326)) STORED
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_obs_time ON observations (obs_time);
CREATE INDEX IF NOT EXISTS idx_obs_geom ON observations USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_obs_float ON observations (float_id);
