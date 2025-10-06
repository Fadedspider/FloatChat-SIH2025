import sys
import os
sys.path.append(os.path.dirname(__file__))

from query_engine import create_query_engine

def test_nlp_engine():
    # Replace with your actual database URL
    # For testing without DB, we'll just test SQL generation
    engine = create_query_engine("sqlite:///test.db")  # Use SQLite for testing
    
    test_questions = [
        "What is average temperature in 2020?",
        "Show me salinity values",
        "List all float positions",
        "Temperature at surface level"
    ]
    
    for question in test_questions:
        print(f"\n🔍 Question: {question}")
        try:
            # Just test SQL generation for now
            sql = engine.generate_sql(question)
            print(f"📝 Generated SQL: {sql}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 50)

if __name__ == "__main__":
    test_nlp_engine()
