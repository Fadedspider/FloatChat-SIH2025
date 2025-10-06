import json

# Pre-defined queries that work with your database schema
QUERY_TEMPLATES = {
    "average temperature": "SELECT AVG(temperature) as avg_temp FROM argo_profiles WHERE temperature IS NOT NULL",
    "temperature data": "SELECT time, temperature, lat, lon FROM argo_profiles WHERE temperature IS NOT NULL ORDER BY time DESC LIMIT 10",
    "salinity data": "SELECT time, salinity, lat, lon FROM argo_profiles WHERE salinity IS NOT NULL ORDER BY time DESC LIMIT 10",
    "float positions": "SELECT DISTINCT float_id, AVG(lat) as avg_lat, AVG(lon) as avg_lon FROM argo_profiles GROUP BY float_id LIMIT 10",
    "temperature over time": "SELECT DATE(time) as date, AVG(temperature) as avg_temp FROM argo_profiles WHERE temperature IS NOT NULL GROUP BY DATE(time) ORDER BY date DESC LIMIT 10",
    "deep ocean data": "SELECT * FROM argo_profiles WHERE pressure > 100 ORDER BY pressure DESC LIMIT 5",
    "surface data": "SELECT * FROM argo_profiles WHERE pressure < 10 ORDER BY time DESC LIMIT 5",
    "all floats": "SELECT COUNT(DISTINCT float_id) as total_floats FROM argo_profiles",
    "recent data": "SELECT * FROM argo_profiles ORDER BY time DESC LIMIT 5",
    "pressure data": "SELECT time, pressure, lat, lon FROM argo_profiles WHERE pressure IS NOT NULL ORDER BY time DESC LIMIT 10",
    "high salinity": "SELECT * FROM argo_profiles WHERE salinity > 35 ORDER BY salinity DESC LIMIT 5",
    "cold water": "SELECT * FROM argo_profiles WHERE temperature < 5 ORDER BY temperature ASC LIMIT 5"
}

def find_best_query(question):
    """Find the best matching query template based on keywords"""
    question_lower = question.lower()
    
    # Enhanced keyword matching
    if "average" in question_lower and "temperature" in question_lower:
        return QUERY_TEMPLATES["average temperature"]
    elif "temperature" in question_lower and ("time" in question_lower or "over" in question_lower):
        return QUERY_TEMPLATES["temperature over time"]
    elif "cold" in question_lower or ("temperature" in question_lower and "low" in question_lower):
        return QUERY_TEMPLATES["cold water"]
    elif "temperature" in question_lower:
        return QUERY_TEMPLATES["temperature data"]
    elif "salinity" in question_lower and ("high" in question_lower or "salty" in question_lower):
        return QUERY_TEMPLATES["high salinity"]
    elif "salinity" in question_lower:
        return QUERY_TEMPLATES["salinity data"]
    elif "pressure" in question_lower:
        return QUERY_TEMPLATES["pressure data"]
    elif "float" in question_lower and ("position" in question_lower or "location" in question_lower):
        return QUERY_TEMPLATES["float positions"]
    elif "deep" in question_lower or "depth" in question_lower:
        return QUERY_TEMPLATES["deep ocean data"]
    elif "surface" in question_lower:
        return QUERY_TEMPLATES["surface data"]
    elif "how many" in question_lower or "count" in question_lower or "total" in question_lower:
        return QUERY_TEMPLATES["all floats"]
    elif "recent" in question_lower or "latest" in question_lower:
        return QUERY_TEMPLATES["recent data"]
    else:
        return QUERY_TEMPLATES["temperature data"]  # Default

def query_database_with_connection(question, db_connection):
    """Main function - converts question to SQL and executes with database connection"""
    
    # Get the SQL query
    sql_query = find_best_query(question)
    
    result = {
        "question": question,
        "sql": sql_query,
        "success": True,
        "data": [],
        "row_count": 0
    }
    
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql_query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            result["data"] = [dict(zip(columns, row)) for row in rows]
            result["row_count"] = len(rows)
            
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["data"] = []
    
    return result

# For testing without database connection
def query_database(question, db_connection=None):
    """Test function - just returns SQL without execution"""
    sql_query = find_best_query(question)
    
    return {
        "question": question,
        "sql": sql_query,
        "success": True,
        "data": [],
        "row_count": 0
    }

# Test function
def test_queries():
    test_questions = [
        "What is the average temperature?",
        "Show me salinity data",
        "Where are the float positions?",
        "Give me temperature over time",
        "Show deep ocean data",
        "Recent observations",
        "How many floats do we have?",
        "Show me cold water",
        "High salinity areas",
        "Pressure readings"
    ]
    
    print("🚀 Testing Smart Query Engine")
    print("=" * 50)
    
    for question in test_questions:
        result = query_database(question)
        print(f"\n🔍 Question: {question}")
        print(f"📝 SQL: {result['sql']}")
        print(f"✅ Success: {result['success']}")
        print("-" * 40)

if __name__ == "__main__":
    test_queries()
