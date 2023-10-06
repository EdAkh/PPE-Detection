#Import the SQLite library
import sqlite3

#Function to fetch the latest image from the 'images' table in the database
def fetch_image():
    try:
        #Connect to the 'image_database.db' file
        conn = sqlite3.connect('image_database.db')
        
        #Create a cursor object to execute SQL commands
        cursor = conn.cursor()
        
        #Find the latest image by selecting the row with the maximum 'id' (assuming 'id' is auto-incremented)
        cursor.execute('SELECT MAX(id) FROM images')
        image_id = cursor.fetchone()[0]
        
        #Retrieve the image name and data from the 'images' table based on the found 'id'
        cursor.execute('SELECT image_name, image_data FROM images WHERE id = ?', (image_id,))
        image_name, image_data = cursor.fetchone()
        
        #Close the database connection
        conn.close()

        #Return a tuple containing the image name and image data
        return (image_name, image_data)

    except Exception as e:
        #Return an error message and status code 500 (Internal Server Error) in case of an exception
        return str(e), 500
