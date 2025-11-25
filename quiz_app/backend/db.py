import psycopg2
from urllib.parse import urlparse
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/cyberquiz")

def parse_connection_string(db_url):
    """Safely parse PostgreSQL connection string with special characters in password"""
    parsed = urlparse(db_url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/')
    }

def init_db():
    try:
        conn_params = parse_connection_string(DATABASE_URL)
        conn = psycopg2.connect(**conn_params)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS attempts (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, category TEXT, score INTEGER, total INTEGER, time_taken INTEGER, date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS stats (user_id INTEGER PRIMARY KEY, total_quizzes INTEGER DEFAULT 0, total_correct INTEGER DEFAULT 0, total_questions INTEGER DEFAULT 0, avg_score REAL DEFAULT 0, favorite_category TEXT, FOREIGN KEY (user_id) REFERENCES users(id))''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database initialization warning: {e}")

def get_connection():
    """Get a new database connection"""
    conn_params = parse_connection_string(DATABASE_URL)
    return psycopg2.connect(**conn_params)

def get_or_create_user(name, email):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = %s', (email,))
    user = c.fetchone()
    if user:
        conn.close()
        return user[0]
    c.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (name, email))
    c.execute('SELECT LASTVAL()')
    user_id = c.fetchone()[0]
    c.execute('INSERT INTO stats (user_id) VALUES (%s)', (user_id,))
    conn.commit()
    conn.close()
    return user_id

def save_attempt(user_id, category, score, total, time_taken):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO attempts (user_id, category, score, total, time_taken) VALUES (%s, %s, %s, %s, %s)', (user_id, category, score, total, time_taken))
    c.execute('SELECT total_quizzes, total_correct, total_questions FROM stats WHERE user_id = %s', (user_id,))
    stats = c.fetchone()
    new_quizzes = stats[0] + 1
    new_correct = stats[1] + score
    new_questions = stats[2] + total
    avg = (new_correct / new_questions * 100) if new_questions > 0 else 0
    c.execute('UPDATE stats SET total_quizzes = %s, total_correct = %s, total_questions = %s, avg_score = %s, favorite_category = %s WHERE user_id = %s', (new_quizzes, new_correct, new_questions, avg, category, user_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT u.name, s.total_quizzes, s.total_correct, s.total_questions, s.avg_score, s.favorite_category FROM users u JOIN stats s ON u.id = s.user_id WHERE u.id = %s', (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {"name": result[0], "total_quizzes": result[1], "total_correct": result[2], "total_questions": result[3], "avg_score": round(result[4], 2), "favorite_category": result[5]}
    return None

def get_user_history(user_id, limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT category, score, total, time_taken, date_taken FROM attempts WHERE user_id = %s ORDER BY date_taken DESC LIMIT %s', (user_id, limit))
    results = c.fetchall()
    conn.close()
    return [{"category": r[0], "score": r[1], "total": r[2], "time_taken": r[3], "date_taken": str(r[4]), "percentage": round(r[1]/r[2]*100, 1) if r[2] > 0 else 0} for r in results]

def get_leaderboard(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT u.name, s.avg_score, s.total_quizzes FROM users u JOIN stats s ON u.id = s.user_id ORDER BY s.avg_score DESC LIMIT %s', (limit,))
    results = c.fetchall()
    conn.close()
    return [{"rank": i+1, "name": r[0], "avg_score": round(r[1], 1), "quizzes_taken": r[2]} for i, r in enumerate(results)]
