import streamlit as st

def show_messages(db):
    st.header("💬 Messages")
    
    current_user_id = st.session_state.user['id']
    
    # 1. Fetch all messages
    all_messages = db.get_user_messages(current_user_id)
    
    if not all_messages:
        st.info("No messages yet. Go to 'Browse Items' to start a conversation!")
        return

    # 2. Group messages
    conversations = {}
    
    for msg in all_messages:
        if msg['sender_id'] == current_user_id:
            partner_id = msg['receiver_id']
            partner_name = msg['receiver_username']
        else:
            partner_id = msg['sender_id']
            partner_name = msg['sender_username']
            
        if partner_id not in conversations:
            conversations[partner_id] = {
                'name': partner_name, 
                'msgs': [],
                'last_msg_time': msg['created_at']
            }
        
        conversations[partner_id]['msgs'].append(msg)
        if msg['created_at'] > conversations[partner_id]['last_msg_time']:
            conversations[partner_id]['last_msg_time'] = msg['created_at']

    # 3. Sidebar List
    st.sidebar.markdown("---")
    st.sidebar.subheader("Recent Chats")
    
    sorted_partner_ids = sorted(
        conversations.keys(), 
        key=lambda k: conversations[k]['last_msg_time'], 
        reverse=True
    )
    
    contact_options = {pid: conversations[pid]['name'] for pid in sorted_partner_ids}
    
    selected_partner_id = st.sidebar.radio(
        "Select Conversation:", 
        options=sorted_partner_ids,
        format_func=lambda pid: contact_options[pid]
    )

    # 4. Display Chat Interface
    if selected_partner_id:
        partner_data = conversations[selected_partner_id]
        st.markdown(f"### Chat with **{partner_data['name']}**")
        
        chat_history = sorted(partner_data['msgs'], key=lambda x: x['created_at'])
        
        # Container for chat history
        chat_container = st.container()
        
        with chat_container:
            for msg in chat_history:
                is_me = msg['sender_id'] == current_user_id
                
                # Mark read
                if not is_me and not msg['is_read']:
                    db.mark_message_read(msg['id'])
                
                # --- CSS Logic ---
                if is_me:
                    alignment = "flex-end"
                    bg_color = "#dcf8c6"
                    text_color = "black"
                    border_radius = "15px 15px 0 15px"
                    margin_left = "20%"
                    margin_right = "0"
                else:
                    alignment = "flex-start"
                    bg_color = "#f0f0f0"
                    text_color = "black"
                    border_radius = "15px 15px 15px 0"
                    margin_left = "0"
                    margin_right = "20%"

                # Item Reference HTML (No indentation to prevent code block rendering)
                ref_html = ""
                if msg['item_title']:
                    ref_html = f"""<div style="font-size: 0.8em; color: #555; margin-bottom: 4px; border-left: 2px solid #075e54; padding-left: 5px;">Re: <b>{msg['item_title']}</b></div>"""

                # Render Bubble (No indentation in the HTML string)
                st.markdown(f"""
<div style="display: flex; justify-content: {alignment}; margin-bottom: 10px; padding: 0 10px;">
    <div style="background-color: {bg_color}; color: {text_color}; padding: 10px 15px; border-radius: {border_radius}; max-width: 70%; box-shadow: 0 1px 1px rgba(0,0,0,0.1);">
        {ref_html}
        <div style="margin-bottom: 2px;">{msg['message']}</div>
        <div style="font-size: 0.65em; color: #555; text-align: right; margin-top: 4px;">{msg['created_at'][11:16]}</div>
    </div>
</div>
""", unsafe_allow_html=True)

        # 5. Input Box
        if prompt := st.chat_input(f"Message {partner_data['name']}..."):
            last_item_id = chat_history[-1]['item_id'] if chat_history else None
            
            db.create_message(
                sender_id=current_user_id,
                receiver_id=selected_partner_id,
                item_id=last_item_id, 
                message=prompt
            )
            st.rerun()