def process_question(question, db_connection):
    """Simple NLP that converts questions to SQL and executes them"""
    
    question_lower = question.lower()
    
    # Map questions to SQL queries
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
        with db_connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                "question": question,
                "sql": sql,
                "data": data,
                "success": True,
                "row_count": len(data)
            }
    except Exception as e:
        return {
            "question": question,
            "sql": sql,
            "data": [],
            "success": False,
            "error": str(e)
        }
