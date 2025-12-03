# 🔍 Campus Lost & Found System

A web-based application to manage lost and found items on campus, featuring user authentication, image hosting, and a messaging system. Built with **Python** and **Streamlit**.

## ⚙️ Installation and Setup

Follow these steps to set up the project environment on your local machine.

### 1\. Prerequisites

Ensure you have **Python 3.9+** installed on your system. You can check this by running:

```bash
python --version
```

### 2\. Clone the Repository

```bash
git clone https://github.com/Enitanayo/SPM.git
cd SPM
```

### 3\. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies to avoid conflicts.

**For Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4\. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

-----

### 5\. Configuration (ImgBB API Key)

This project uses **ImgBB** for cloud image storage. You need to configure your API key securely.

1.  **Get an API Key:**

      * Go to [https://api.imgbb.com/](https://api.imgbb.com/)
      * Login/Signup and click **"Get API Key"**.
      * Copy the key generated.

2.  **Set up Streamlit Secrets:**

      * In the root directory of the project (where `app.py` is), create a new folder named `.streamlit`.
      * Inside that folder, create a file named `secrets.toml`.

    *Folder Structure:*

    ```text
    /SPM
    ├── .streamlit/
    │   └── secrets.toml  <-- Create this file
    ├── app.py
    └── ...
    ```

3.  **Add your Key:**
    Open `secrets.toml` and paste the following line:

    ```toml
    IMGBB_API_KEY = "paste_your_api_key_here"
    ```

> **⚠️ IMPORTANT:** Never commit your `secrets.toml` file to GitHub\! Add `.streamlit/secrets.toml` to your `.gitignore` file to keep your credentials safe.

-----

### 6\. Run the Application

Once everything is set up, launch the application:

```bash
streamlit run app.py
```

The app should open automatically in your browser at `http://localhost:8501`.  

---