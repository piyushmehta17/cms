from db import get_db_connection

def initialize_database():
    # Create the database
    sql_create_db = """
    CREATE DATABASE IF NOT EXISTS file_manager;
    """
    
    conn = get_db_connection(database=None)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_create_db)
        conn.commit()
        print("Database 'file_manager' created or already exists!")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()
        conn.close()

    # Create tables
    sql_commands = [
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
        """,
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
        );
        """
    ]

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for command in sql_commands:
            cursor.execute(command)
        conn.commit()
        print("Tables initialized successfully!")
    except Exception as e:
        print(f"Error initializing tables: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    initialize_database()