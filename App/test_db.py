import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()

TZ_INFO = os.getenv("TZ", "Europe/London")
tz = ZoneInfo(TZ_INFO)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "mental_health"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        print("Database connection successful")
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

def save_conversation(conversation_id, question, answer_data, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)
    
    print(f"\nAttempting to save conversation:")
    print(f"Conversation ID: {conversation_id}")
    print(f"Question: {question}")
    print(f"Timestamp: {timestamp}")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO conversations 
                (id, question, answer, timestamp)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """
            print(f"Executing query: {query}")
            print(f"With values: {(conversation_id, question, answer_data, timestamp)}")
            
            cur.execute(query, (conversation_id, question, answer_data, timestamp))
            returned_id = cur.fetchone()[0]
            conn.commit()
            print(f"Conversation saved successfully with ID: {returned_id}")
            return returned_id
            
    except Exception as e:
        conn.rollback()
        print(f"Error saving conversation: {str(e)}")
        print(f"Error type: {type(e)}")
        raise
    finally:
        conn.close()
        print("Database connection closed")

def save_feedback(conversation_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)
    
    print(f"\nAttempting to save feedback:")
    print(f"Conversation ID: {conversation_id}")
    print(f"Feedback Value: {feedback}")
    print(f"Timestamp: {timestamp}")

    conn = get_db_connection()
    
    try:
        with conn.cursor() as cur:
            # First check if the conversation exists
            cur.execute(
                "SELECT id FROM conversations WHERE id = %s",
                (conversation_id,)
            )
            conversation = cur.fetchone()
            if not conversation:
                print(f"Warning: No conversation found with ID {conversation_id}")
            
            # Try to insert the feedback
            query = """
                INSERT INTO feedback 
                (conversation_id, feedback, timestamp) 
                VALUES (%s, %s, %s)
                RETURNING id
            """
            print(f"Executing query: {query}")
            print(f"With values: {(conversation_id, feedback, timestamp)}")
            
            cur.execute(query, (conversation_id, feedback, timestamp))
            feedback_id = cur.fetchone()[0]
            conn.commit()
            print(f"Feedback saved successfully with ID: {feedback_id}")
            return feedback_id
            
    except Exception as e:
        conn.rollback()
        print(f"Error saving feedback: {str(e)}")
        print(f"Error type: {type(e)}")
        raise
    finally:
        conn.close()
        print("Database connection closed")

def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # First drop tables if they exist
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

            # Create conversations table
            cur.execute("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
            # Create feedback table
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
        conn.commit()
        print('Database tables created successfully')
    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {e}")
        raise
    finally:
        conn.close()

def check_tables():
    """Function to check if tables exist and their structure"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check tables existence
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cur.fetchall()
            print("\nExisting tables:", [table[0] for table in tables])
            
            # Check feedback table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'feedback'
            """)
            columns = cur.fetchall()
            print("\nFeedback table structure:")
            for col in columns:
                print(f"Column: {col[0]}, Type: {col[1]}, Nullable: {col[2]}")
            
            # Check conversations table structure
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'conversations'
            """)
            columns = cur.fetchall()
            print("\nConversations table structure:")
            for col in columns:
                print(f"Column: {col[0]}, Type: {col[1]}, Nullable: {col[2]}")
            
            # Check existing entries
            cur.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM feedback")
            feed_count = cur.fetchone()[0]
            print(f"\nExisting conversations: {conv_count}")
            print(f"Existing feedback entries: {feed_count}")
            
    except Exception as e:
        print(f"Error checking tables: {e}")
    finally:
        conn.close()

def list_recent_conversations():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, question, timestamp 
                FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            conversations = cur.fetchall()
            print("\nRecent conversations:")
            for conv in conversations:
                print(f"ID: {conv[0]}, Question: {conv[1]}, Time: {conv[2]}")
    except Exception as e:
        print(f"Error listing conversations: {e}")
    finally:
        conn.close()

def get_feedback_stats():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_feedback,
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            stats = cur.fetchone()
            print("\nFeedback statistics:")
            print(f"Total feedback: {stats['total_feedback']}")
            print(f"Thumbs up: {stats['thumbs_up']}")
            print(f"Thumbs down: {stats['thumbs_down']}")
            return stats
    except Exception as e:
        print(f"Error getting feedback stats: {e}")
    finally:
        conn.close()