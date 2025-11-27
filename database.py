
import sqlite3
import hashlib
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="database/campus_lost_found.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                item_type TEXT NOT NULL CHECK(item_type IN ('lost', 'found')),
                image_url TEXT,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'claimed', 'resolved')),
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                item_id INTEGER,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id),
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role, email)
            VALUES (?, ?, ?, ?)
        ''', ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin', 'admin@campus.edu'))
        
        conn.commit()
        conn.close()
    
    # User CRUD operations
    def create_user(self, username, password_hash, role, email):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, email)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, role, email))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    # Item CRUD operations
    def create_item(self, title, description, item_type, image_url, user_id):
        """Create a new lost/found item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO items (title, description, item_type, image_url, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, item_type, image_url, user_id))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id
    
    def get_all_items(self, item_type=None, status='Active'):
        """Get all items with optional filtering"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT i.*, u.username 
            FROM items i 
            JOIN users u ON i.user_id = u.id
            WHERE i.status = ?
        '''
        params = [status]
        
        if item_type:
            query += ' AND i.item_type = ?'
            params.append(item_type)
        
        query += ' ORDER BY i.created_at DESC'
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        conn.close()
        return items
    
    def get_user_items(self, user_id):
        """Get items belonging to a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM items 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        items = cursor.fetchall()
        conn.close()
        return items
    
    def update_item(self, item_id, title, description, status, user_id=None):
        """Update an item - user_id is for permission check"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:  # Student can only update their own items
            cursor.execute('''
                UPDATE items 
                SET title = ?, description = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (title, description, status, item_id, user_id))
        else:  # Admin can update any item
            cursor.execute('''
                UPDATE items 
                SET title = ?, description = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (title, description, status, item_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_item(self, item_id, user_id=None):
        """Delete an item - user_id is for permission check"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:  # Student can only delete their own items
            cursor.execute('DELETE FROM items WHERE id = ? AND user_id = ?', (item_id, user_id))
        else:  # Admin can delete any item
            cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    # Message operations
    def create_message(self, sender_id, receiver_id, item_id, message):
        """Create a new message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (sender_id, receiver_id, item_id, message)
            VALUES (?, ?, ?, ?)
        ''', (sender_id, receiver_id, item_id, message))
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        return message_id
    
    def get_user_messages(self, user_id):
        """Get messages for a user (both sent and received)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, 
                   s.username as sender_username,
                   r.username as receiver_username,
                   i.title as item_title
            FROM messages m
            JOIN users s ON m.sender_id = s.id
            JOIN users r ON m.receiver_id = r.id
            LEFT JOIN items i ON m.item_id = i.id
            WHERE m.sender_id = ? OR m.receiver_id = ?
            ORDER BY m.created_at DESC
        ''', (user_id, user_id))
        messages = cursor.fetchall()
        conn.close()
        return messages
    
    def mark_message_read(self, message_id):
        """Mark a message as read"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE messages SET is_read = TRUE WHERE id = ?', (message_id,))
        conn.commit()
        conn.close()