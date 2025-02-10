import sqlite3
from datetime import datetime
import os

DB_NAME = "chat_storage.db"  

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  
    return conn

def create_application_logs():
    """Creates the application_logs table if it does not exist."""
    conn = get_db_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         session_id TEXT,
                         user_query TEXT,
                         gpt_response TEXT,
                         model TEXT,
                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        print("application_logs table created.")  
    except sqlite3.Error as e:
        print(f"Error creating application_logs table: {e}")
    finally:
        conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    """Inserts a new log entry into the application_logs table."""
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)',
                     (session_id, user_query, gpt_response, model))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting log: {e}")
    finally:
        conn.close()

def get_chat_history(session_id):
    """Fetches chat history for a given session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', 
                       (session_id,))
        messages = []
        for row in cursor.fetchall():
            messages.extend([{"role": "human", "content": row['user_query']},
                             {"role": "ai", "content": row['gpt_response']}])
        return messages
    except sqlite3.Error as e:
        print(f"Error fetching chat history: {e}")
        return []
    finally:
        conn.close()

def create_document_store():
    """Creates the document_store table if it does not exist."""
    conn = get_db_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS document_store
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         filename TEXT,
                         upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        print("document_store table created.")  
    except sqlite3.Error as e:
        print(f"Error creating document_store table: {e}")
    finally:
        conn.close()

def insert_document_record(filename):
    """Inserts a new document record and returns the document ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO document_store (filename) VALUES (?)', (filename,))
        file_id = cursor.lastrowid  
        conn.commit()
        return file_id
    except sqlite3.Error as e:
        print(f"Error inserting document record: {e}")
        return None
    finally:
        conn.close()

def delete_document_record(file_id):
    """Deletes a document record by file ID."""
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM document_store WHERE id = ?', (file_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error deleting document record: {e}")
        return False
    finally:
        conn.close()

def get_all_documents():
    """Fetches all stored documents."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC')
        documents = cursor.fetchall()
        return [dict(doc) for doc in documents]
    except sqlite3.Error as e:
        print(f"Error fetching documents: {e}")
        return []
    finally:
        conn.close()

def initialize_database():
    """Initializes the database tables."""
    create_application_logs()
    create_document_store()

if __name__ == "__main__":
    initialize_database()
