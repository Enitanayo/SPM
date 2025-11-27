import streamlit as st
import os
from datetime import datetime

from database import Database
from auth import Auth
from storage import ImageStorage, LocalImageStorage

# Page configuration
st.set_page_config(
    page_title="Campus Lost & Found",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
db = Database()
auth = Auth()

# Use local storage if no API key is set
if hasattr(st.secrets, "IMGBB_API_KEY"):
    storage = ImageStorage()
    storage.api_key = st.secrets.IMGBB_API_KEY
else:
    storage = LocalImageStorage()

def init_session_state():
    """Initialize session state variables"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "login"

def login_page():
    """Login page UI"""
    st.title("🔍 Campus Lost & Found System")
    st.subheader("Login to Your Account")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                if username and password:
                    success, message, user = auth.login_user(username, password)
                    if success:
                        st.session_state.user = user
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email (optional)")
            role = st.selectbox("Role", ["student", "admin"])
            register_btn = st.form_submit_button("Register")
            
            if register_btn:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = auth.register_user(new_username, new_password, role, email)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("Please fill all required fields")

def dashboard_page():
    """Main dashboard after login"""
    st.title(f"Welcome, {st.session_state.user['username']}!")
    st.sidebar.title("Navigation")
    
    # Sidebar navigation
    pages = ["Browse Items", "My Items", "Report Item", "Messages"]
    if st.session_state.user['role'] == 'admin':
        pages.append("Admin Panel")
    
    selected_page = st.sidebar.radio("Go to", pages)
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()
    
    # Page routing
    if selected_page == "Browse Items":
        browse_items_page()
    elif selected_page == "My Items":
        my_items_page()
    elif selected_page == "Report Item":
        report_item_page()
    elif selected_page == "Messages":
        messages_page()
    elif selected_page == "Admin Panel" and st.session_state.user['role'] == 'admin':
        admin_panel_page()

def browse_items_page():
    """Browse all lost and found items"""
    st.header("Browse Lost & Found Items")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        item_type = st.selectbox("Filter by type", ["All", "lost", "found"])
    with col2:
        status = st.selectbox("Filter by status", ["active", "claimed", "resolved"])
    
    # Get items based on filters
    item_type_filter = None if item_type == "All" else item_type
    items = db.get_all_items(item_type_filter, status)
    
    if not items:
        st.info("No items found matching your criteria.")
        return
    
    # Display items in a grid
    cols = st.columns(2)
    for idx, item in enumerate(items):
        with cols[idx % 2]:
            with st.container():
                st.subheader(f"{item['item_type'].title()}: {item['title']}")
                
                if item['image_url']:
                    st.image(item['image_url'], width=300)
                
                st.write(f"**Description:** {item['description']}")
                st.write(f"**Posted by:** {item['username']}")
                st.write(f"**Status:** {item['status'].title()}")
                st.write(f"**Date:** {item['created_at'][:10]}")
                
                # Message button
                if st.session_state.user['id'] != item['user_id']:
                    with st.expander("Send Message"):
                        message = st.text_area(f"Message about {item['title']}", key=f"msg_{item['id']}")
                        if st.button("Send", key=f"send_{item['id']}"):
                            if message:
                                db.create_message(
                                    st.session_state.user['id'],
                                    item['user_id'],
                                    item['id'],
                                    message
                                )
                                st.success("Message sent!")
                
                st.markdown("---")

def my_items_page():
    """User's own items"""
    st.header("My Items")
    
    # Button to add new item
    if st.button("+ Report New Item"):
        st.session_state.page = "report_item"
        st.rerun()
    
    items = db.get_user_items(st.session_state.user['id'])
    
    if not items:
        st.info("You haven't posted any items yet.")
        return
    
    for item in items:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{item['item_type'].title()}: {item['title']}")
                if item['image_url']:
                    st.image(item['image_url'], width=200)
                st.write(f"**Description:** {item['description']}")
                st.write(f"**Status:** {item['status'].title()}")
                st.write(f"**Date:** {item['created_at'][:10]}")
            
            with col2:
                with st.form(key=f"edit_{item['id']}"):
                    new_status = st.selectbox(
                        "Status",
                        ["active", "claimed", "resolved"],
                        index=["active", "claimed", "resolved"].index(item['status']),
                        key=f"status_{item['id']}"
                    )
                    
                    if st.form_submit_button("Update"):
                        success = db.update_item(
                            item['id'],
                            item['title'],
                            item['description'],
                            new_status,
                            st.session_state.user['id']
                        )
                        if success:
                            st.success("Item updated!")
                            st.rerun()
                        else:
                            st.error("Failed to update item")
                
                if st.button("Delete", key=f"delete_{item['id']}"):
                    success = db.delete_item(item['id'], st.session_state.user['id'])
                    if success:
                        st.success("Item deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete item")
            
            st.markdown("---")

def report_item_page():
    """Report a new lost or found item"""
    st.header("Report Lost or Found Item")
    
    with st.form("item_form"):
        title = st.text_input("Item Title*")
        description = st.text_area("Description*")
        item_type = st.selectbox("Type*", ["lost", "found"])
        image_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png', 'gif'])
        
        submitted = st.form_submit_button("Submit Item")
        
        if submitted:
            if not title or not description:
                st.error("Please fill in all required fields (*)")
            else:
                image_url = None
                if image_file:
                    valid, msg = storage.validate_image(image_file)
                    if valid:
                        image_url = storage.upload_image(image_file)
                        if not image_url:
                            st.error("Failed to upload image")
                    else:
                        st.error(msg)
                
                item_id = db.create_item(
                    title, 
                    description, 
                    item_type, 
                    image_url, 
                    st.session_state.user['id']
                )
                
                if item_id:
                    st.success(f"Item reported successfully! ID: {item_id}")
                    st.session_state.page = "my_items"
                    st.rerun()
                else:
                    st.error("Failed to create item")

def messages_page():
    """User messages interface"""
    st.header("Messages")
    
    messages = db.get_user_messages(st.session_state.user['id'])
    
    if not messages:
        st.info("No messages yet.")
        return
    
    for msg in messages:
        with st.container():
            # Style based on read status and sender
            is_sent = msg['sender_id'] == st.session_state.user['id']
            bg_color = "#f0f2f6" if msg['is_read'] else "#e6f3ff"
            border_color = "#3366cc" if not msg['is_read'] else "#cccccc"
            
            st.markdown(f"""
            <div style="
                background-color: {bg_color};
                border-left: 4px solid {border_color};
                padding: 10px;
                margin: 5px 0;
                border-radius: 4px;
            ">
            """, unsafe_allow_html=True)
            
            if is_sent:
                st.write(f"**To:** {msg['receiver_username']}")
            else:
                st.write(f"**From:** {msg['sender_username']}")
                
            if msg['item_title']:
                st.write(f"**Regarding:** {msg['item_title']}")
            
            st.write(msg['message'])
            st.write(f"*{msg['created_at'][:16]}*")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Mark as read button for received messages
            if not is_sent and not msg['is_read']:
                if st.button("Mark as read", key=f"read_{msg['id']}"):
                    db.mark_message_read(msg['id'])
                    st.rerun()
            
            st.markdown("---")

def admin_panel_page():
    """Admin-only functionality"""
    st.header("Admin Panel")
    
    tab1, tab2, tab3 = st.tabs(["All Items", "All Users", "Statistics"])
    
    with tab1:
        st.subheader("Manage All Items")
        items = db.get_all_items()
        
        for item in items:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{item['item_type'].title()}:** {item['title']}")
                    st.write(f"By: {item['username']} | Status: {item['status']}")
                
                with col2:
                    if st.button("Edit", key=f"admin_edit_{item['id']}"):
                        st.session_state.editing_item = item['id']
                
                with col3:
                    if st.button("Delete", key=f"admin_delete_{item['id']}"):
                        success = db.delete_item(item['id'])
                        if success:
                            st.success("Item deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete item")
                
                # Edit form
                if hasattr(st.session_state, 'editing_item') and st.session_state.editing_item == item['id']:
                    with st.form(key=f"admin_edit_form_{item['id']}"):
                        new_title = st.text_input("Title", value=item['title'])
                        new_description = st.text_area("Description", value=item['description'])
                        new_status = st.selectbox(
                            "Status",
                            ["active", "claimed", "resolved"],
                            index=["active", "claimed", "resolved"].index(item['status'])
                        )
                        
                        if st.form_submit_button("Save"):
                            success = db.update_item(
                                item['id'], 
                                new_title, 
                                new_description, 
                                new_status
                            )
                            if success:
                                st.success("Item updated!")
                                del st.session_state.editing_item
                                st.rerun()
                            else:
                                st.error("Failed to update item")
                        
                        if st.form_submit_button("Cancel"):
                            del st.session_state.editing_item
                            st.rerun()
                
                st.markdown("---")
    
    with tab2:
        st.subheader("All Users")
        # This would require additional user management functions
        st.info("User management features can be extended here")
    
    with tab3:
        st.subheader("Statistics")
        items = db.get_all_items()
        total_items = len(items)
        lost_items = len([i for i in items if i['item_type'] == 'lost'])
        found_items = len([i for i in items if i['item_type'] == 'found'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", total_items)
        col2.metric("Lost Items", lost_items)
        col3.metric("Found Items", found_items)

def main():
    """Main application controller"""
    init_session_state()
    
    if st.session_state.user is None:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()