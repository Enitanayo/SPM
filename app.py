import streamlit as st
from database import Database
from auth import Auth
from storage import ImageStorage, LocalImageStorage

# Import Views
from views import auth_view, item_view, message_view, admin_view

# Page configuration
st.set_page_config(
    page_title="Campus Lost & Found",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Services
db = Database()
auth = Auth()

# Use local storage if no API key is set in .streamlit/secrets.toml
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

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
        /* Hide Streamlit deploy button and other UI elements */
        /* #MainMenu {visibility: hidden;} */
        footer {visibility: hidden;}
        /* header {visibility: hidden;} */
        .stDeployButton {display: none;}
        button[kind="header"] {display: none;}
        
        /* Main app styling - clean white background */
        .stApp {
            background: #ffffff;
        }
        
        /* Content area */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Style the form container to have purple background */
        div[data-testid="stForm"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }
        
        /* Form labels to be white on purple background */
        div[data-testid="stForm"] label {
            color: white !important;
            font-weight: 500;
        }
        
        /* Form inputs on purple background */
        div[data-testid="stForm"] input {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
        }
        
        div[data-testid="stForm"] input:focus {
            border-color: white !important;
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3) !important;
        }
        
        /* Form buttons on purple card */
        div[data-testid="stForm"] button[kind="primary"] {
            background: white !important;
            color: #667eea !important;
            font-weight: 600;
            width: 100%;
            border: none !important;
        }
        
        div[data-testid="stForm"] button[kind="primary"]:hover {
            background: rgba(255, 255, 255, 0.9) !important;
            transform: translateY(-2px);
        }
        
        /* AGGRESSIVE hiding of all form helper text */
        div[data-testid="stForm"] small,
        div[data-testid="stForm"] .row-widget.stButton small,
        div[data-testid="stForm"] .stMarkdown small,
        .stForm small,
        form small,
        [data-testid="stForm"] p[class*="caption"],
        [data-testid="stFormSubmitContent"] small,
        .element-container small {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        
        /* Hide instruction text from text inputs */
        .stTextInput small {
            display: none !important;
        }
        
        /* Headers */
        h1 {
            color: #1e293b;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        h2 {
            color: #334155;
            font-weight: 600;
            margin-top: 1.5rem;
        }
        
        h3 {
            color: #475569;
            font-weight: 600;
        }
        
        /* Buttons - subtle purple accent */
        .stButton > button {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            background: #5568d3;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        /* Form inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            transition: border-color 0.3s;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Sidebar - clean dark theme */
        section[data-testid="stSidebar"] {
            background: #1e293b;
        }
        
        section[data-testid="stSidebar"] * {
            color: white !important;
        }
        
        /* Tabs - minimal styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8fafc;
            border-radius: 10px;
            padding: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            color: #64748b;
        }
        
        .stTabs [aria-selected="true"] {
            background: #667eea;
            color: white;
        }
        
        /* Cards/Containers */
        div[data-testid="stExpander"] {
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            background: #f8fafc;
        }
        
        /* Metrics - subtle purple */
        div[data-testid="stMetricValue"] {
            color: #667eea;
            font-weight: 700;
        }
        
        /* Info, Success, Error boxes */
        .stAlert {
            border-radius: 10px;
            border-left: 4px solid;
        }
        
        /* File uploader */
        section[data-testid="stFileUploadDropzone"] {
            border-radius: 10px;
            border: 2px dashed #cbd5e1;
            background: #f8fafc;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application controller"""
    init_session_state()
    apply_custom_css()

    # 1. Login Flow
    if st.session_state.user is None:
        auth_view.show_login_page(auth)
        return

    # 2. Main Dashboard Layout
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}!")
    st.sidebar.title("Navigation")
    
    # Define available pages based on role
    pages = ["Browse Items", "My Items", "Report Item", "Messages"]
    if st.session_state.user['role'] == 'admin':
        pages.append("Admin Panel")
    
    # Add key="navigation" so we can change it via code
    selected_page = st.sidebar.radio("Go to", pages, key="navigation")
    
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

    # 3. Page Routing
    if selected_page == "Browse Items":
        item_view.show_browse_items(db)
    elif selected_page == "My Items":
        item_view.show_my_items(db)
    elif selected_page == "Report Item":
        item_view.show_report_item(db, storage)
    elif selected_page == "Messages":
        message_view.show_messages(db)
    elif selected_page == "Admin Panel":
        admin_view.show_admin_panel(db, auth)

if __name__ == "__main__":
    main()