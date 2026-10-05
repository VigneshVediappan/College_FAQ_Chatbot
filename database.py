import sqlite3


DATABASE = "chatbot.db"


def create_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_chat(user_message, bot_response):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO chat_history
        (user_message, bot_response)
        VALUES (?, ?)
    """, (user_message, bot_response))

    connection.commit()
    connection.close()


def get_chat_history():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_message, bot_response, created_at
        FROM chat_history
        ORDER BY id ASC
    """)

    chats = cursor.fetchall()

    connection.close()

    return chats
