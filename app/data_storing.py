#Import the SQLite library
import sqlite3

#Function to create the SQLite database and tables if they don't exist
def create_database():
    #Connect to the 'image_database.db' file or create it if it doesn't exist
    conn = sqlite3.connect('image_database.db')
    
    #Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    #Create the 'images' table with columns for image information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            image_data BLOB
        )
    ''')
    
    #Create the 'annotated_images' table with columns for annotated image information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annotated_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annotated_image_name TEXT,
            annotated_image_data BLOB
        )
    ''')
    
    #Commit the changes to the database
    conn.commit()
    
    #Close the database connection
    conn.close()

#Function to store image data in the 'images' table
def store_image(image_name, image_data):
    #Connect to the 'image_database.db' file
    conn = sqlite3.connect('image_database.db')
    
    #Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    #Insert the image name and data into the 'images' table
    cursor.execute('INSERT INTO images (image_name, image_data) VALUES (?, ?)', (image_name, image_data))
    
    #Commit the changes to the database
    conn.commit()
    
    #Close the database connection
    conn.close()

#Function to store annotated image data in the 'annotated_images' table
def store_annotated_image(annotated_image_name, annotated_image_data):
    #Connect to the 'image_database.db' file
    conn = sqlite3.connect('image_database.db')
    
    #Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    #Insert the annotated image name and data into the 'annotated_images' table
    cursor.execute('INSERT INTO annotated_images (annotated_image_name, annotated_image_data) VALUES (?, ?)', (annotated_image_name, annotated_image_data))
    
    #Commit the changes to the database
    conn.commit()
    
    #Close the database connection
    conn.close()
