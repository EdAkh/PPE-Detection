import sqlite3

def create_database():
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            image_data BLOB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annotated_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annotated_image_name TEXT,
            annotated_image_data BLOB
        )
    ''')
    conn.commit()
    conn.close()

def store_image(image_name, image_data):
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO images (image_name, image_data) VALUES (?, ?)', (image_name, image_data))
    conn.commit()
    conn.close()

def store_annotated_image(annotated_image_name, annotated_image_data):
    conn = sqlite3.connect('image_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO annotated_images (annotated_image_name, annotated_image_data) VALUES (?, ?)', (annotated_image_name, annotated_image_data))
    conn.commit()
    conn.close()