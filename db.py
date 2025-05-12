import sqlite3
import os

def create_database():
    # Check if database already exists
    if os.path.exists('bab.db'):
        print("Database already exists.")
        return
    
    # Connect to database (will create if it doesn't exist)
    conn = sqlite3.connect('bab.db')
    cursor = conn.cursor()
    
    # Create restaurant table
    cursor.execute('''
    CREATE TABLE restaurants (
        place_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        business_hours TEXT,
        phone TEXT,
        menu TEXT,
        description TEXT,
        theme TEXT,
        review_summary TEXT
    )
    ''')
    
    # Create review table
    cursor.execute('''
    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_id INTEGER,
        reviewer_name TEXT,
        review_text TEXT,
        FOREIGN KEY (place_id) REFERENCES restaurants (place_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database 'bab.db' created successfully with tables 'restaurants' and 'reviews'.")

def save_restaurant(place_id, name=None, address=None, business_hours=None, 
                   phone=None, menu=None, description=None, theme=None, review_summary=None, line_num=None):
    conn = sqlite3.connect('bab.db')
    cursor = conn.cursor()
    
    # Check if restaurant with this place_id already exists
    cursor.execute("SELECT place_id FROM restaurants WHERE place_id = ?", (place_id,))
    exists = cursor.fetchone()
    
    if exists:
        # Update existing restaurant
        cursor.execute('''
        UPDATE restaurants SET 
            name = COALESCE(?, name),
            address = COALESCE(?, address),
            business_hours = COALESCE(?, business_hours),
            phone = COALESCE(?, phone),
            menu = COALESCE(?, menu),
            description = COALESCE(?, description),
            theme = COALESCE(?, theme),
            review_summary = COALESCE(?, review_summary),
            line_num = COALESCE(?, line_num)
        WHERE place_id = ?
        ''', (name, address, business_hours, phone, menu, description, theme, review_summary, line_num, place_id))
        print(f"Updated restaurant with place_id {place_id}")
    else:
        # Insert new restaurant
        cursor.execute('''
        INSERT INTO restaurants (place_id, name, address, business_hours, phone, menu, description, theme, review_summary, line_num)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (place_id, name or "Unknown", address, business_hours, phone, menu, description, theme, review_summary, line_num))
        print(f"Added new restaurant with place_id {place_id}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
