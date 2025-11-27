import hashlib
import streamlit as st
from database import Database

class Auth:
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, role, email):
        """Register a new user"""
        if not username or not password:
            return False, "Username and password are required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if role not in ['student', 'admin']:
            return False, "Invalid role"
        
        password_hash = self.hash_password(password)
        success = self.db.create_user(username, password_hash, role, email)
        
        if success:
            return True, "Registration successful"
        else:
            return False, "Username already exists"
    
    def login_user(self, username, password):
        """Authenticate user"""
        user = self.db.get_user_by_username(username)
        if not user:
            return False, "User not found", None
        
        password_hash = self.hash_password(password)
        if user['password_hash'] == password_hash:
            user_dict = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'email': user['email']
            }
            return True, "Login successful", user_dict
        else:
            return False, "Invalid password", None
    
    def check_permissions(self, user, item_user_id=None):
        """Check if user has permission to modify an item"""
        if user['role'] == 'admin':
            return True
        if item_user_id and user['id'] == item_user_id:
            return True
        return False