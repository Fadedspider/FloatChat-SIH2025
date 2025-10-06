from fastapi import FastAPI, HTTPException, Query
from database import get_db_connection
from typing import Optional, List, Dict, Any
import json

app = FastAPI(
    title="ARGO Ocean Data API",
    description="API for accessing ARGO float oceanographic data",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "ARGO Ocean Data API", "status": "running"}

@app.get("/daily-avg")
async def get_daily_averages(
    var: str = Query(..., description="Variable: temperature, salinity, or pressure"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get daily averages for temperature, salinity, or pressure"""
    
    # Map variable to view name
    view_mapping = {
        "temperature": "daily_avg_temperature",
        "salinity": "daily_avg_salinity", 
        "pressure": "daily_avg_pressure"
    }
    
    if var not in view_mapping:
        raise HTTPException(status_code=400, detail="Variable must be temperature, salinity, or pressure")
    
    view_name = view_mapping[var]
    
    # Build query with optional date filters
    query = f"SELECT day, avg_value, num_observations FROM {view_name}"
    params = []
    
    if start_date or end_date:
        query += " WHERE"
        conditions = []
        if start_date:
            conditions.append(" day >= %s")
            params.append(start_date)
        if end_date:
            conditions.append(" day <= %s")
            params.append(end_date)
        query += " AND".join(conditions)
    
    query += " ORDER BY day"
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                results = cur.fetchall()
                return {"variable": var, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/profile")
async def get_float_profile(
    float_id: str = Query(..., description="Float ID"),
    cycle: Optional[int] = Query(None, description="Specific cycle number"),
    limit: int = Query(100, description="Maximum number of records")
):
    """Get profile data for a specific float"""
    
    query = """
    SELECT float_id, cycle, time, lat, lon, pressure, temperature, salinity
    FROM argo_profiles 
    WHERE float_id = %s
    """
    params = [float_id]
    
    if cycle:
        query += " AND cycle = %s"
        params.append(cycle)
    
    query += " ORDER BY pressure ASC LIMIT %s"
    params.append(limit)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                results = cur.fetchall()
                if not results:
                    raise HTTPException(status_code=404, detail="Float not found")
                return {"float_id": float_id, "cycle": cycle, "profile": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/floats")
async def get_floats_list(
    lat_min: Optional[float] = Query(None, description="Minimum latitude"),
    lat_max: Optional[float] = Query(None, description="Maximum latitude"),
    lon_min: Optional[float] = Query(None, description="Minimum longitude"), 
    lon_max: Optional[float] = Query(None, description="Maximum longitude"),
    limit: int = Query(50, description="Maximum number of floats")
):
    """Get list of available floats, optionally filtered by geographic bounds"""
    
    query = """
    SELECT DISTINCT float_id, 
           MIN(time) as first_observation,
           MAX(time) as last_observation,
           COUNT(*) as total_observations,
           AVG(lat) as avg_lat,
           AVG(lon) as avg_lon
    FROM argo_profiles
    """
    
    conditions = []
    params = []
    
    # Add geographic filters if provided
    if lat_min is not None:
        conditions.append("lat >= %s")
        params.append(lat_min)
    if lat_max is not None:
        conditions.append("lat <= %s") 
        params.append(lat_max)
    if lon_min is not None:
        conditions.append("lon >= %s")
        params.append(lon_min)
    if lon_max is not None:
        conditions.append("lon <= %s")
        params.append(lon_max)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """ 
    GROUP BY float_id 
    ORDER BY first_observation DESC 
    LIMIT %s
    """
    params.append(limit)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                results = cur.fetchall()
                return {"floats": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(question_data: dict):
    """AI endpoint - processes natural language questions about ocean data"""
    
    question = question_data.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    # This will integrate with the AI teammate's nlp module
    # For now, return a placeholder response
    try:
        # TODO: Import and use nlp.query_engine.query_db(question)
        # from nlp.query_engine import query_db
        # result = query_db(question)
        
        # Placeholder response until AI teammate completes their module
        return {
            "question": question,
            "response": "AI integration pending - this endpoint will connect to the NLP query engine",
            "sql": "-- SQL will be generated by AI teammate",
            "data": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint to verify database connection"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM argo_profiles")
                count = cur.fetchone()['count']
                return {
                    "status": "healthy",
                    "database": "connected", 
                    "total_records": count
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/ask")
async def ask_question(question_data: dict):
    """AI endpoint - processes natural language questions about ocean data"""
    
    question = question_data.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    # This will integrate with the AI teammate's nlp module
    # For now, return a placeholder response
    try:
        # TODO: Import and use nlp.query_engine.query_db(question)
        # from nlp.query_engine import query_db
        # result = query_db(question)
        
        # Placeholder response until AI teammate completes their module
        return {
            "question": question,
            "response": "AI integration pending - this endpoint will connect to the NLP query engine",
            "sql": "-- SQL will be generated by AI teammate",
            "data": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint to verify database connection"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM argo_profiles")
                count = cur.fetchone()['count']
                return {
                    "status": "healthy",
                    "database": "connected", 
                    "total_records": count
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

