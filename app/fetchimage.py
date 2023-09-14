import sqlite3

def fetch_image():
    try:
        conn = sqlite3.connect('image_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id) FROM images')
        image_id = cursor.fetchone()[0]
        cursor.execute('SELECT image_name, image_data FROM images WHERE id = ?', (image_id,))
        image_name, image_data = cursor.fetchone()
        conn.close()

        return (image_name, image_data)

    except Exception as e:
        return str(e), 500
