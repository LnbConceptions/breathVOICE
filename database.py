import sqlite3
import json

class CharacterDatabase:
    def __init__(self, db_name='voice_pack_workflow.db'):
        self.db_name = db_name
        self.initialize_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def initialize_database(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            # Create characters table
            c.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    avatar_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add missing columns to existing characters table if they don't exist
            try:
                c.execute("ALTER TABLE characters ADD COLUMN description TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                c.execute("ALTER TABLE characters ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                c.execute("ALTER TABLE characters ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except sqlite3.OperationalError:
                pass  # Column already exists
            # Create llm_configs table with new fields
            c.execute('''
                CREATE TABLE IF NOT EXISTS llm_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    base_url TEXT,
                    api_key TEXT,
                    model TEXT,
                    system_prompt TEXT,
                    user_prompt_template TEXT,
                    generation_params TEXT -- Store as JSON string
                )
            ''')
            # Create dialogue_sets table
            c.execute('''
                CREATE TABLE IF NOT EXISTS dialogue_sets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (id)
                )
            ''')
            # Create dialogues table
            c.execute('''
                CREATE TABLE IF NOT EXISTS dialogues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    set_id INTEGER NOT NULL,
                    action_parameter TEXT NOT NULL,
                    dialogue TEXT NOT NULL,
                    FOREIGN KEY (set_id) REFERENCES dialogue_sets (id)
                )
            ''')
            conn.commit()

    # Character Management
    def create_character(self, name, description, avatar_path=None):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO characters (name, description, avatar_path) VALUES (?, ?, ?)", (name, description, avatar_path))
            conn.commit()
            return c.lastrowid

    def add_character(self, name):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO characters (name) VALUES (?)", (name,))
            conn.commit()

    def get_characters(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM characters")
            return c.fetchall()

    def get_character(self, character_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
            return c.fetchone()

    def update_character(self, character_id, new_name, description=None, avatar_path=None):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE characters SET name = ?, description = ?, avatar_path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                     (new_name, description, avatar_path, character_id))
            conn.commit()

    def delete_character(self, character_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM dialogue_sets WHERE character_id = ?", (character_id,))
            c.execute("DELETE FROM characters WHERE id = ?", (character_id,))
            conn.commit()

    # LLM Configuration Management
    def add_llm_config(self, name, base_url='', api_key='', model='', system_prompt='', user_prompt_template='', generation_params='{}'):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO llm_configs (name, base_url, api_key, model, system_prompt, user_prompt_template, generation_params) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (name, base_url, api_key, model, system_prompt, user_prompt_template, generation_params))
            conn.commit()

    def get_llm_configs(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM llm_configs")
            return c.fetchall()

    def get_llm_config(self, config_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM llm_configs WHERE id = ?", (config_id,))
            return c.fetchone()

    def update_llm_config(self, config_id, name, base_url, api_key, model, system_prompt, user_prompt_template, generation_params):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE llm_configs SET name = ?, base_url = ?, api_key = ?, model = ?, system_prompt = ?, user_prompt_template = ?, generation_params = ? WHERE id = ?",
                      (name, base_url, api_key, model, system_prompt, user_prompt_template, generation_params, config_id))
            conn.commit()

    def delete_llm_config(self, config_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM llm_configs WHERE id = ?", (config_id,))
            conn.commit()

    # Dialogue Set Management
    def add_dialogue_set(self, character_id, name, dialogues):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO dialogue_sets (character_id, name) VALUES (?, ?)", (character_id, name))
            set_id = c.lastrowid
            for action_param, dialogue in dialogues:
                c.execute("INSERT INTO dialogues (set_id, action_parameter, dialogue) VALUES (?, ?, ?)", (set_id, action_param, dialogue))
            conn.commit()

    def get_dialogue_sets(self, character_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM dialogue_sets WHERE character_id = ?", (character_id,))
            return c.fetchall()

    def get_dialogues(self, set_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT action_parameter, dialogue FROM dialogues WHERE set_id = ?", (set_id,))
            return c.fetchall()

    def delete_dialogue_set(self, set_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM dialogues WHERE set_id = ?", (set_id,))
            c.execute("DELETE FROM dialogue_sets WHERE id = ?", (set_id,))
            conn.commit()

if __name__ == '__main__':
    db = CharacterDatabase()
    print("Database initialized.")
    # You can add test data or verification steps here
    # Example: Add a character
    # db.add_character("Test Character")
    # print(db.get_characters())