import streamlit as st

def show_browse_items(db):
    """Browse all lost and found items"""
    st.header("Browse Lost & Found Items")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search by keyword", placeholder="e.g., phone, wallet, keys...", key="search_input")
    with col2:
        item_type = st.selectbox("Filter", ["All", "Lost", "Found"])
    
    # Get items based on filters
    item_type_filter = None if item_type == "All" else item_type.lower()
    items = db.get_all_items(item_type_filter, 'active')
    
    # Filter by search query
    if search_query:
        search_lower = search_query.lower()
        items = [item for item in items if 
                search_lower in item['title'].lower() or 
                search_lower in item['description'].lower()]
    
    if not items:
        st.info("No items found matching your criteria.")
        return
    
    # Display items in a grid
    cols = st.columns(2)
    for idx, item in enumerate(items):
        with cols[idx % 2]:
            with st.container():
                # Item card styling
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                            padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                            border-left: 4px solid {"#ef4444" if item["item_type"] == "lost" else "#10b981"};'>
                    <h3 style='margin: 0; color: #1e293b;'>{item['item_type'].upper()}: {item['title']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if item['image_url']:
                    st.image(item['image_url'], width=300, use_container_width=True)
                
                st.write(f"**Description:** {item['description']}")
                st.write(f"**Posted by:** {item['username']}")
                st.write(f"**Date:** {item['created_at'][:10]}")
                
                # Message button - only for students, not admins
                if st.session_state.user['role'] == 'student' and st.session_state.user['id'] != item['user_id']:
                    with st.expander("💬 Contact Owner"):
                        message = st.text_area(f"Message about {item['title']}", key=f"msg_{item['id']}")
                        if st.button("Send Message", key=f"send_{item['id']}"):
                            if message:
                                db.create_message(
                                    st.session_state.user['id'],
                                    item['user_id'],
                                    item['id'],
                                    message
                                )
                                st.success("Message sent!")
                
                st.markdown("---")

def show_my_items(db):
    """User's own items"""
    st.header("My Items")
    
    st.markdown("""
    **Status Guide:**
    - 🟢 **Active** - Item is still lost/found and looking for owner/claimer
    - 🟡 **Claimed** - Someone claimed it, but not yet confirmed as resolved
    - ✅ **Resolved** - Item successfully returned to owner (case closed)
    """)
    
    items = db.get_user_items(st.session_state.user['id'])
    
    if not items:
        st.info("You haven't posted any items yet. Click 'Report Item' in the sidebar to add one.")
        return
    
    for item in items:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_emoji = {"active": "🟢", "claimed": "🟡", "resolved": "✅"}
                st.subheader(f"{item['item_type'].title()}: {item['title']}")
                if item['image_url']:
                    st.image(item['image_url'], width=200)
                st.write(f"**Description:** {item['description']}")
                st.write(f"**Status:** {status_emoji.get(item['status'], '')} {item['status'].title()}")
                st.write(f"**Date:** {item['created_at'][:10]}")
            
            with col2:
                with st.form(key=f"edit_{item['id']}"):
                    new_status = st.selectbox(
                        "Update Status",
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

def show_report_item(db, storage):
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
                    st.success(f"✅ Item '{title}' reported successfully!")
                    st.info("Redirecting to My Items...")
                    # Small delay to show success message
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to create item")