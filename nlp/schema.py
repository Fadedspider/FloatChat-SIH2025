SCHEMA_INFO = """
Database Schema for ARGO Ocean Data:

Tables:
1. observations
   - float_id: varchar
   - obs_time: timestamp
   - latitude: float
   - longitude: float
   - depth: float
   - variable: varchar (TEMP, PSAL, PRES)
   - value: float

2. floats
   - float_id: varchar
   - avg_lat: float
   - avg_lon: float

Variables:
- TEMP: Temperature (°C)
- PSAL: Salinity (PSU) 
- PRES: Pressure (dbar)

Surface data: depth < 10
Deep data: depth > 100
"""

PROMPT_TEMPLATE = """
{schema_info}

Convert this natural language question to PostgreSQL query:
Question: {question}

Rules:
1. Return ONLY the SQL query, no explanation
2. For temperature use variable='TEMP'
3. For salinity use variable='PSAL'
4. For pressure use variable='PRES'
5. Surface means depth < 10
6. Use proper PostgreSQL syntax

SQL:
"""
