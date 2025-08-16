import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anpr.database_handler import DatabaseHandler

def test_connection():
    try:
        db = DatabaseHandler()
        connection = db.connect()
        print("Successfully connected to database!")
        
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM authorized_vehicles")
            results = cursor.fetchall()
            print("\nAuthorized vehicles in database:")
            for row in results:
                print(f"Plate: {row[1]}, Owner: {row[2]}")
                
        connection.close()
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection() 