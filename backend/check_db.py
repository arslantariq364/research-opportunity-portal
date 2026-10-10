"""
Database connectivity verification script.
Tests MySQL connection and table availability using configured environment variables.
"""
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import Config
import pymysql

def test_connection():
    print("=" * 60)
    print("University Research Opportunity Portal - Database Connectivity Check")
    print("=" * 60)
    print(f"Host:     {Config.DB_HOST}")
    print(f"Port:     {Config.DB_PORT}")
    print(f"User:     {Config.DB_USER}")
    print(f"Database: {Config.DB_NAME}")
    print("-" * 60)
    
    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=int(Config.DB_PORT),
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version;")
            result = cursor.fetchone()
            print(f"[SUCCESS] Connected to MySQL successfully! Version: {result.get('version')}")
            
            cursor.execute("SHOW TABLES LIKE 'research_opportunities';")
            table = cursor.fetchone()
            if table:
                print("[SUCCESS] Table 'research_opportunities' exists in database.")
            else:
                print("[WARNING] Database exists, but 'research_opportunities' table was not found.")
                print("           Run database/schema.sql to create the required tables.")
        connection.close()
        print("=" * 60)
        return True
    except pymysql.MySQLError as e:
        print(f"[ERROR] Failed to connect to MySQL: {e}")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
