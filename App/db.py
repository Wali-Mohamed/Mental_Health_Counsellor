import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

RUN_TIMEZONE_CHECK = os.getenv('RUN_TIMEZONE_CHECK', '1') == '1'
TZ_INFO = os.getenv("TZ", "Europe/London")
tz = ZoneInfo(TZ_INFO)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "mental_health"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        
        
    )


def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute("""
                CREATE TABLE conversations (
                        id TEXT PRIMARY KEY,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        response_time FLOAT NOT NULL,             
                        relevance VARCHAR(20) NOT NULL,            -- Stores relevance, e.g., 'RELEVANT', assuming a max length of 20 characters
                        relevance_explanation TEXT NOT NULL,       -- Explanation of relevance as text
                        prompt_tokens INTEGER NOT NULL,            -- Token count for prompt
                        completion_tokens INTEGER NOT NULL,        -- Token count for completion
                        total_tokens INTEGER NOT NULL,             -- Total tokens used
                        eval_prompt_tokens INTEGER NOT NULL,       -- Token count for evaluation prompt
                        eval_completion_tokens INTEGER NOT NULL,   -- Token count for evaluation completion
                        eval_total_tokens INTEGER NOT NULL,        -- Total tokens used in evaluation
                        prompt_openai_cost FLOAT NOT NULL,         -- Cost for prompt in floating-point
                        eval_openai_cost FLOAT NOT NULL,            -- Cost for evaluation in floating-point
                        
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                    )
            """)
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
        conn.commit()
        print('tables created')
    finally:
        conn.close()


def save_conversation(conversation_id, 
                    question, 
                    answer_data, 
                    response_time,
                    relevance,
                    relevance_explanation,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    eval_prompt_tokens,
                    eval_completion_tokens,
                    eval_total_tokens,
                    prompt_openai_cost,
                    eval_openai_cost,
                    timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations 
                (
                    id, 
                    question, 
                    answer, 
                    response_time, 
                    relevance, 
                    relevance_explanation, 
                    prompt_tokens, 
                    completion_tokens, 
                    total_tokens, 
                    eval_prompt_tokens, 
                    eval_completion_tokens, 
                    eval_total_tokens, 
                    prompt_openai_cost, 
                    eval_openai_cost, 
                    timestamp
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    question,
                    answer_data,
                    response_time,
                    relevance,
                    relevance_explanation,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    eval_prompt_tokens,
                    eval_completion_tokens,
                    eval_total_tokens,
                    prompt_openai_cost,
                    eval_openai_cost,
                    timestamp
                ),
            )
        conn.commit()
        print("Conversation saved successfully.")  # Success debug message
    except Exception as e:
        print(f"Error saving conversation: {e}")  # Log any errors
    finally:
        conn.close()


def save_feedback(conversation_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback 
                (conversation_id, feedback, timestamp) 
                VALUES (%s, %s, %s)
                
                """,
                (
                    conversation_id, 
                    feedback, 
                    timestamp
                    ),
            )
        conn.commit()
        print("Feedback saved successfully.")  # Success debug message
    except Exception as e:
        print(f"Error saving feedback: {e}")  # Log any errors
    finally:
        conn.close()


def get_recent_conversations(limit=5, relevance=None):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """
            if relevance:
                query += f" WHERE c.relevance = '{relevance}'"
            query += " ORDER BY c.timestamp DESC LIMIT %s"

            cur.execute(query, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_feedback_stats():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            return cur.fetchone()
    finally:
        conn.close()


def check_timezone():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW timezone;")
            db_timezone = cur.fetchone()[0]
            print(f"Database timezone: {db_timezone}")

            cur.execute("SELECT current_timestamp;")
            db_time_utc = cur.fetchone()[0]
            print(f"Database current time (UTC): {db_time_utc}")

            db_time_local = db_time_utc.astimezone(tz)
            print(f"Database current time ({TZ_INFO}): {db_time_local}")

            py_time = datetime.now(tz)
            print(f"Python current time: {py_time}")

            # Use py_time instead of tz for insertion
            cur.execute("""
                INSERT INTO conversations 
                (id, question, answer, timestamp)
                VALUES (%s, %s, %s, %s)
                RETURNING timestamp;
            """, 
            ('test', 'test question', 'test answer', 'test model', py_time))

            inserted_time = cur.fetchone()[0]
            print(f"Inserted time (UTC): {inserted_time}")
            print(f"Inserted time ({TZ_INFO}): {inserted_time.astimezone(tz)}")

            cur.execute("SELECT timestamp FROM conversations WHERE id = 'test';")
            selected_time = cur.fetchone()[0]
            print(f"Selected time (UTC): {selected_time}")
            print(f"Selected time ({TZ_INFO}): {selected_time.astimezone(tz)}")

            # Clean up the test entry
            cur.execute("DELETE FROM conversations WHERE id = 'test';")
            conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()


if RUN_TIMEZONE_CHECK:
    check_timezone()