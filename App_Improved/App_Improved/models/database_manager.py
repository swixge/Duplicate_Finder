import sqlite3
from datetime import datetime


class DatabaseManager:
    """Model for managing SQLite database operations"""
    
    def __init__(self, db_name="duplicates.db"):
        self.db_name = db_name
        self.conn = None
        self.connect()
        self.init_db()

    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        except sqlite3.Error as e:
            raise RuntimeError(f"Помилка підключення до бази даних: {str(e)}")

    def init_db(self):
        """Initialize database tables"""
        if not self.conn:
            raise RuntimeError("Немає підключення до бази даних")
        
        c = self.conn.cursor()
        
        # Create files table
        c.execute('''CREATE TABLE IF NOT EXISTS [files] (
            [id] INTEGER PRIMARY KEY AUTOINCREMENT,
            [path] TEXT NOT NULL,
            [user] TEXT NOT NULL,
            [date] TEXT NOT NULL,
            [char_count] INTEGER,
            [word_count] INTEGER,
            [unique_words] INTEGER,
            [avg_word_length] REAL,
            [longest_word] TEXT,
            [shortest_word] TEXT,
            [highlighted_file] TEXT
        )''')
        
        # Create results table
        c.execute('''CREATE TABLE IF NOT EXISTS [results] (
            [id] INTEGER PRIMARY KEY AUTOINCREMENT,
            [file_id] INTEGER NOT NULL,
            [algorithm] TEXT NOT NULL,
            [duplicates] INTEGER NOT NULL,
            [unique_count] INTEGER NOT NULL,
            [frequency] INTEGER NOT NULL,
            [time] REAL NOT NULL,
            [top_phrases] TEXT,
            [repeat_percentage] REAL,
            FOREIGN KEY ([file_id]) REFERENCES [files]([id])
        )''')
        
        self.conn.commit()
        self._add_missing_columns()

    def _add_missing_columns(self):
        """Add missing columns to existing tables"""
        c = self.conn.cursor()
        
        # Check and add missing columns to files table
        c.execute("PRAGMA table_info(files)")
        columns = [col[1] for col in c.fetchall()]
        new_columns = [
            ("char_count", "INTEGER"),
            ("word_count", "INTEGER"),
            ("unique_words", "INTEGER"),
            ("avg_word_length", "REAL"),
            ("longest_word", "TEXT"),
            ("shortest_word", "TEXT"),
            ("highlighted_file", "TEXT")
        ]
        for col_name, col_type in new_columns:
            if col_name not in columns:
                c.execute(f"ALTER TABLE [files] ADD COLUMN [{col_name}] {col_type}")
        
        # Check and add missing columns to results table
        c.execute("PRAGMA table_info(results)")
        columns = [col[1] for col in c.fetchall()]
        if "top_phrases" not in columns:
            c.execute("ALTER TABLE [results] ADD COLUMN [top_phrases] TEXT")
        if "repeat_percentage" not in columns:
            c.execute("ALTER TABLE [results] ADD COLUMN [repeat_percentage] REAL")
        
        self.conn.commit()

    def save_file(self, file_path, user, text_stats, highlighted_file=None):
        """Save file information to database"""
        c = self.conn.cursor()
        c.execute('''INSERT INTO [files] (
            [path], [user], [date], [char_count], [word_count], [unique_words], 
            [avg_word_length], [longest_word], [shortest_word], [highlighted_file]
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (file_path, user, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   text_stats["char_count"], text_stats["word_count"], text_stats["unique_words"],
                   text_stats["avg_word_length"], text_stats["longest_word"], 
                   text_stats["shortest_word"], highlighted_file))
        self.conn.commit()
        return c.lastrowid

    def save_results(self, file_id, results):
        """Save analysis results to database"""
        c = self.conn.cursor()
        for algo, data in results.items():
            try:
                # Handle top_phrases - ensure it's a list of tuples
                top_phrases_list = data.get("top_phrases", [])
                if top_phrases_list:
                    top_phrases_str = "; ".join([f"{phrase}: {count}" for phrase, count in top_phrases_list])
                else:
                    top_phrases_str = ""
                
                c.execute('''INSERT INTO [results] (
                    [file_id], [algorithm], [duplicates], [unique_count], [frequency], 
                    [time], [top_phrases], [repeat_percentage]
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (file_id, algo, data["duplicates"], data["unique_count"], 
                           data["frequency"], data["time"], top_phrases_str, data["repeat_percentage"]))
            except Exception as e:
                print(f"Помилка при збереженні результатів для {algo}: {e}")
                continue
        self.conn.commit()

    def get_stats(self, file_id):
        """Get analysis statistics for a file"""
        c = self.conn.cursor()
        c.execute('''SELECT [algorithm], [duplicates], [unique_count], [frequency], 
                     [time], [top_phrases], [repeat_percentage]
                     FROM [results] WHERE [file_id] = ?''', (file_id,))
        stats = {}
        rows = c.fetchall()
        print(f"get_stats для file_id={file_id}: знайдено {len(rows)} рядків в БД")
        for algo, dups, uniq, freq, t, top_phrases, repeat_percentage in rows:
            top_phrases_list = []
            if top_phrases:
                for phrase_count in top_phrases.split("; "):
                    if ": " in phrase_count:
                        try:
                            phrase, count = phrase_count.split(": ", 1)
                            top_phrases_list.append((phrase, int(count)))
                        except ValueError as e:
                            print(f"Помилка при розборі фрази '{phrase_count}': {e}")
                            continue
            stats[algo] = {
                "duplicates": dups,
                "unique_count": uniq,
                "frequency": freq,
                "time": t,
                "top_phrases": top_phrases_list,
                "repeat_percentage": repeat_percentage
            }
            print(f"  Алгоритм {algo}: {len(top_phrases_list)} фраз")
        print(f"get_stats для file_id={file_id}: повернуто {len(stats)} алгоритмів")
        return stats if stats else None  # Return None if no stats found

    def get_all_files(self):
        """Get all files from database"""
        c = self.conn.cursor()
        c.execute('''SELECT [id], [path], [user], [date], [char_count], [word_count], 
                     [unique_words], [avg_word_length], [longest_word], [shortest_word], 
                     [highlighted_file]
                     FROM [files] LIMIT 100''')
        return c.fetchall()

    def get_file_stats(self, file_id):
        """Get statistics for a specific file"""
        return self.get_stats(file_id)

    def get_file_info(self, file_id):
        """Get file information"""
        c = self.conn.cursor()
        c.execute('''SELECT [char_count], [word_count], [unique_words], [avg_word_length], 
                     [longest_word], [shortest_word], [highlighted_file]
                     FROM [files] WHERE [id] = ?''', (file_id,))
        result = c.fetchone()
        if result:
            return {
                "char_count": result[0],
                "word_count": result[1],
                "unique_words": result[2],
                "avg_word_length": result[3],
                "longest_word": result[4],
                "shortest_word": result[5],
                "highlighted_file": result[6]
            }
        return None

    def delete_file(self, file_id):
        """Delete file and its results from database"""
        c = self.conn.cursor()
        c.execute("DELETE FROM [results] WHERE [file_id] = ?", (file_id,))
        c.execute("DELETE FROM [files] WHERE [id] = ?", (file_id,))
        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
