import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root1234"),
            database=os.getenv("DB_NAME", "recipe_portal"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

if __name__ == "__main__":
    conn = get_db_connection()
    if conn and conn.is_connected():
        print("Connected successfully to recipe_portal!")
        conn.close()
    else:
        print("Failed to connect.")