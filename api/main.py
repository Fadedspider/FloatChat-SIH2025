from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware  # ADD THIS
from database import get_db_connection
from typing import Optional, List, Dict, Any
import json
import sys
import os

app = FastAPI(
    title="ARGO Ocean Data API",
    description="API for accessing ARGO float oceanographic data",
    version="1.0.0"
)

# ADD CORS MIDDLEWARE - THIS IS CRITICAL FOR REACT CONNECTION!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """AI endpoint - processes natural language questions and returns natural language answers"""
    
    question = question_data.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    def generate_natural_language_response(question, data, sql):
        """Convert SQL results into natural language responses"""
        
        question_lower = question.lower()
        
        if not data:
            return "I couldn't find any data matching your question."
        
        # Generate responses based on question type and data
        if "average" in question_lower and "temperature" in question_lower:
            temp = data[0].get('average_temperature', 0)
            return f"The average ocean temperature from ARGO float data is {temp:.2f}°C."
            
        elif "how many" in question_lower or "count" in question_lower:
            count = data[0].get('total_floats', 0)
            return f"There are {count} ARGO floats in the database."
            
        elif "float" in question_lower and ("position" in question_lower or "location" in question_lower):
            if len(data) > 1:
                return f"I found {len(data)} ARGO float positions. The data shows floats distributed across various ocean locations with coordinates ranging from the first few entries."
            else:
                return "I found one float position in the data."
                
        elif "temperature" in question_lower:
            if len(data) > 1:
                return f"I found {len(data)} temperature readings. The most recent measurements show temperatures ranging across different ocean depths and locations."
            elif len(data) == 1:
                temp = data[0].get('temperature')
                time = data[0].get('time', 'unknown time')
                return f"The temperature reading is {temp}°C recorded at {time}."
            
        elif "salinity" in question_lower:
            if len(data) > 1:
                return f"I found {len(data)} salinity measurements from the ARGO float network, showing the salt content distribution across different ocean areas."
            elif len(data) == 1:
                sal = data[0].get('salinity')
                return f"The salinity measurement is {sal} PSU (Practical Salinity Units)."
                
        elif "pressure" in question_lower:
            if len(data) > 1:
                return f"I retrieved {len(data)} pressure readings, which indicate depth measurements at various ocean locations."
            elif len(data) == 1:
                press = data[0].get('pressure')
                return f"The pressure reading is {press} dbar, indicating ocean depth."
                
        elif "recent" in question_lower or "latest" in question_lower:
            return f"Here are the {len(data)} most recent observations from the ARGO float database, showing the latest oceanographic measurements."
            
        elif "deep" in question_lower:
            return f"I found {len(data)} deep ocean measurements (pressure > 100 dbar), representing data from deeper water levels."
            
        elif "surface" in question_lower:
            return f"I found {len(data)} surface-level measurements (pressure < 10 dbar), representing near-surface ocean conditions."
            
        else:
            return f"I found {len(data)} records matching your question. The data includes various oceanographic measurements from ARGO floats."
    
    def process_nlp_query(question, db_connection):
        """Process NLP query and return results with natural language response"""
        
        question_lower = question.lower()
        
        # SQL mapping logic
        if "average" in question_lower and "temperature" in question_lower:
            sql = "SELECT AVG(temperature) as average_temperature FROM argo_profiles WHERE temperature IS NOT NULL"
        elif "temperature" in question_lower and ("time" in question_lower or "over" in question_lower):
            sql = "SELECT DATE(time) as date, AVG(temperature) as avg_temp FROM argo_profiles WHERE temperature IS NOT NULL GROUP BY DATE(time) ORDER BY date DESC LIMIT 10"
        elif "temperature" in question_lower:
            sql = "SELECT time, temperature, lat, lon FROM argo_profiles WHERE temperature IS NOT NULL ORDER BY time DESC LIMIT 10"
        elif "salinity" in question_lower:
            sql = "SELECT time, salinity, lat, lon FROM argo_profiles WHERE salinity IS NOT NULL ORDER BY time DESC LIMIT 10"
        elif "float" in question_lower and ("position" in question_lower or "location" in question_lower):
            sql = "SELECT DISTINCT float_id, AVG(lat) as avg_lat, AVG(lon) as avg_lon FROM argo_profiles GROUP BY float_id LIMIT 10"
        elif "pressure" in question_lower:
            sql = "SELECT time, pressure, lat, lon FROM argo_profiles WHERE pressure IS NOT NULL ORDER BY time DESC LIMIT 10"
        elif "deep" in question_lower or "depth" in question_lower:
            sql = "SELECT * FROM argo_profiles WHERE pressure > 100 ORDER BY pressure DESC LIMIT 10"
        elif "surface" in question_lower:
            sql = "SELECT * FROM argo_profiles WHERE pressure < 10 ORDER BY time DESC LIMIT 10"
        elif "how many" in question_lower or "count" in question_lower:
            sql = "SELECT COUNT(DISTINCT float_id) as total_floats FROM argo_profiles"
        elif "recent" in question_lower or "latest" in question_lower:
            sql = "SELECT * FROM argo_profiles ORDER BY time DESC LIMIT 10"
        else:
            sql = "SELECT * FROM argo_profiles ORDER BY time DESC LIMIT 5"
        
        try:
            from psycopg2.extras import RealDictCursor
            
            with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                data = [dict(row) for row in rows] if rows else []
                
                # Generate natural language response
                natural_response = generate_natural_language_response(question, data, sql)
                
                return {
                    "question": question,
                    "sql": sql,
                    "data": data,
                    "success": True,
                    "row_count": len(data),
                    "natural_language_response": natural_response
                }
        except Exception as e:
            return {
                "question": question,
                "sql": sql,
                "data": [],
                "success": False,
                "error": str(e),
                "natural_language_response": f"I encountered an error while processing your question: {str(e)}"
            }
    
    try:
        with get_db_connection() as conn:
            result = process_nlp_query(question, conn)
            return result
            
    except Exception as e:
        return {
            "question": question,
            "response": f"Error: {str(e)}",
            "sql": "SELECT 'Error' as message",
            "data": [{"error": str(e)}],
            "success": False,
            "natural_language_response": f"I'm sorry, I encountered a technical error: {str(e)}"
        }

@app.get("/ask/test")
async def test_nlp_endpoint():
    """Test the NLP functionality with sample questions"""
    
    test_questions = [
        "What is the average temperature?",
        "Show me float positions",
        "Give me salinity data",
        "Show me recent observations",
        "How many floats do we have?"
    ]
    
    results = []
    
    for question in test_questions:
        try:
            result = await ask_question({"question": question})
            results.append(result)
        except Exception as e:
            results.append({
                "question": question,
                "error": str(e),
                "success": False
            })
    
    return {"test_results": results}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify database connection"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM argo_profiles")
                count = cur.fetchone()[0]  # Fixed: use [0] instead of ['count']
                return {
                    "status": "healthy",
                    "database": "connected", 
                    "total_records": count,
                    "nlp_status": "integrated"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "nlp_status": "unknown"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
