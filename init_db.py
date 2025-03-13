# init_db.py
from db import get_db_connection

def initialize_database():
    # SQL commands to create the database and tables
    sql_commands = [
        """
        CREATE DATABASE IF NOT EXISTS file_manager;
        """,
        """
        USE file_manager;
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('viewer', 'creator', 'manager', 'admin') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) UNIQUE NOT NULL,
            original_name VARCHAR(255) NOT NULL,
            uploader VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    # Execute the SQL commands
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for command in sql_commands:
            cursor.execute(command)
        conn.commit()
        print("Database and tables initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    initialize_database()