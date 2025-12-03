import streamlit as st

def show_admin_panel(db, auth):
    st.header("Admin Panel")
    
    # Create tabs for different admin sections
    tab1, tab2, tab3 = st.tabs(["Manage Items", "Manage Admins", "Statistics"])
    
    # --- TAB 1: MANAGE ITEMS ---
    with tab1:
        st.subheader("All Database Items")
        
        # Filter Logic
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            filter_status = st.selectbox("Filter Status", ["All", "active", "claimed", "resolved"])
        
        status_arg = filter_status if filter_status != "All" else None
        
        # Fetch and Filter Items
        if filter_status == "All":
            items = db.get_all_items(status=None)
        else:
            items = db.get_all_items(status=filter_status)
            
        if not items:
            st.info("No items found.")
        
        # Display Items Card View
        for item in items:
            with st.container():
                # Edit Mode Check
                is_editing = st.session_state.get(f"edit_mode_{item['id']}", False)
                
                if is_editing:
                    # --- EDIT FORM ---
                    with st.form(key=f"edit_form_{item['id']}"):
                        st.subheader(f"Editing: {item['title']}")
                        new_title = st.text_input("Title", value=item['title'])
                        new_desc = st.text_area("Description", value=item['description'])
                        new_status = st.selectbox(
                            "Status", 
                            ["active", "claimed", "resolved"],
                            index=["active", "claimed", "resolved"].index(item['status'])
                        )
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.form_submit_button("💾 Save"):
                                success = db.update_item(item['id'], new_title, new_desc, new_status)
                                if success:
                                    st.success("Updated!")
                                    st.session_state[f"edit_mode_{item['id']}"] = False
                                    st.rerun()
                        with c2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_mode_{item['id']}"] = False
                                st.rerun()
                                
                else:
                    # --- READ ONLY VIEW ---
                    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                    
                    with col1:
                        if item['image_url']:
                            st.image(item['image_url'], width=80)
                        else:
                            st.write("📷 No Img")
                            
                    with col2:
                        st.markdown(f"**{item['title']}**")
                        st.caption(f"By: {item['username']} | {item['item_type'].upper()}")
                        
                    with col3:
                        if item['status'] == 'active':
                            st.success(f"● {item['status']}")
                        elif item['status'] == 'resolved':
                            st.info(f"● {item['status']}")
                        else:
                            st.warning(f"● {item['status']}")
                            
                    with col4:
                        if st.button("✏️ Edit", key=f"btn_edit_{item['id']}"):
                            st.session_state[f"edit_mode_{item['id']}"] = True
                            st.rerun()
                        if st.button("🗑️ Del", key=f"btn_del_{item['id']}"):
                            db.delete_item(item['id'])
                            st.rerun()
            st.markdown("---")

    # --- TAB 2: MANAGE ADMINS ---
    with tab2:
        st.subheader("Create New Administrator")
        st.markdown("Use this form to grant **Admin Access** to another user.")
        
        with st.container():
            # Using a form to group inputs
            with st.form("create_admin_form"):
                new_admin_user = st.text_input("New Admin Username")
                new_admin_pass = st.text_input("New Admin Password", type="password")
                new_admin_email = st.text_input("Email (Optional)")
                
                # Hardcode role to 'admin'
                submitted = st.form_submit_button("Create Admin User")
                
                if submitted:
                    if new_admin_user and new_admin_pass:
                        # We reuse the existing register_user function but force the role to 'admin'
                        success, msg = auth.register_user(
                            username=new_admin_user, 
                            password=new_admin_pass, 
                            role='admin', 
                            email=new_admin_email
                        )
                        
                        if success:
                            st.success(f"✅ Admin '{new_admin_user}' created successfully!")
                        else:
                            st.error(f"❌ Error: {msg}")
                    else:
                        st.warning("⚠️ Username and Password are required.")

    # --- TAB 3: STATISTICS ---
    with tab3:
        st.subheader("System Overview")
        
        all_items = db.get_all_items()
        total_items = len(all_items)
        lost_count = len([i for i in all_items if i['item_type'] == 'lost'])
        found_count = len([i for i in all_items if i['item_type'] == 'found'])
        active_count = len([i for i in all_items if i['status'] == 'active'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Items", total_items)
        m2.metric("Lost Items", lost_count)
        m3.metric("Found Items", found_count)
        
        st.markdown("### Status Breakdown")
        s1, s2 = st.columns(2)
        s1.metric("Active Cases", active_count)
        s2.metric("Resolved/Claimed", total_items - active_count)