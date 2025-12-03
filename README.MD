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


# PROJECT REPORT

## 1. Project Overview
### 1.1 Group members 
Adebajo Oluwatoni Esther 23/0038  
Adenubi Gbenga Isaiah  23/0281  
Aworekun Convenant Toluwalase 22/0268  
Adeola Enitan-Ayo Oluwaseun 22/0129  
Agomuo wisdom Chiemezie 22/0259  
Igbokwe Marvel 20/2729  


### 1.2 Campus Lost & Found System
### 1.3 Description 
A web platform for reporting, tracking and claiming lost and found items on campus. Users can file reports for missing items, upload photos, search the inventory of found items, and communicate securely with custodians

### 1.4. Requirements Summary



## 2. System Overview Diagram
The Campus Lost and Found system utilizes a Modular Component Architecture to ensure scalability and ease of maintenance.
   - Presentation Layer (Frontend): Built using Streamlit. The UI is decoupled into specific "Views" (in the views/ directory), ensuring that the "Report Item" logic is separate from the "Dashboard" logic.
   - Application Logic: The core business rules are handled by the main controller (app.py), which routes user requests to the appropriate view.
   - Authentication Service: A dedicated auth.py module handles password hashing (SHA-256) and session management.
   - Data Layer: The system uses SQLite (database.py) for structured data and integrates with the ImgBB API (storage.py) for cloud-based image hosting, ensuring the application remains lightweight.


## 3. Project Outcome
The Team successfully delivered a functional Beta Version of the system.   
Successfully Built:
   - Requirement Elicitation & Design (Tasks 2-7): Completed the database schema design and UI/UX wireframing, which were translated into the views/ folder structure.
   - Authentication (Task 9): Implemented secure Login and Registration with role-based access (Student vs. Admin) in auth.py.
   - Catalog & Reporting (Tasks 10-11): Users can successfully upload images of found items and browse the lost item catalog. This logic is fully functional in views/item_view.py.
   - Admin Panel: An administrative dashboard was built (views/admin_view.py) to moderate content.

     **Deferred / Partially Completed**:
        - Messaging Center (Task 12):  
            - Status: Partially Completed.
            - Details: We implemented an asynchronous messaging system where users can leave messages for item owners (visible in views/message_view.py).  
        - Feedback/Ratings (Task 13):  
            - Status: Deferred.
            - Reason: We prioritized the "Image Validation" feature (storage.py) to ensure users could not upload malicious files, which took precedence over the ratings system.

## 4. Individual Contributions
- Adenubi Gbenga - (Project Lead & Backend Architect) I was responsible for the core Database Design (Task 7) and Authentication (Task 9). I wrote the database.py class, ensuring that the users, items, and messages tables were correctly related using Foreign Keys. I also implemented the auth.py module to handle password hashing and session security.  

- Adebajo Oluwatoni - (UI/UX Designer) My primary contribution was UI/UX Wireframes (Task 6). I designed the visual layout of the application. I translated these designs into the modular views/ folder structure, ensuring a consistent look and feel across the "Dashboard" and "Admin Panel."  

- Adeola Oluwaseun - (Frontend Developer - Catalog) I developed the Catalog Module (Task 10). I wrote the code in views/item_view.py that fetches data from the database and renders it in a responsive grid layout. I ensured that the filters for "Lost vs. Found" and "Date" were functional.  

- Igbokwe Marvel - (Frontend Developer - Reporting) I focused on the Report Lost Item (Task 11) functionality. I built the input forms in views/item_view.py and integrated the file uploader. I worked closely with the backend to ensure that images uploaded by users were correctly tagged and stored.  

- Agomuo Wisdom - (QA & Testing) I handled Testing (Task 14). I performed functional testing on the storage.py module, verifying that large images were rejected and valid images were successfully sent to the ImgBB API. I also tested the "Mark as Read" feature in the messaging system.  

- Aworekun Covenant - (Documentation & Use Case Analysis) I managed Use Case Analysis (Task 4). I defined the user journey for "Student Reporting an Item" vs "Admin Deleting an Item," which guided the development of the role-based access control logic in the main() function of app.py.

## 5. Challenges Faced and Addressed
**Image Persistence on Localhost:**
  - Issue: Storing images in a local folder meant they weren't accessible when testing on different machines.
  - Resolution: We implemented storage.py to use the ImgBB API. This offloads storage to the cloud, returning a URL that any user can access, regardless of where the app is hosted.

## 6. Tools and Technologies Used
  - Frontend: Streamlit (Python framework)
  
  - Backend Logic: Python 3.9+
  
  - Database: SQLite3 (Embedded relational database)
  
  - Cloud Storage: ImgBB API (RESTful API for images)

  - Version Control: Git & GitHub

## 7. Testing Summary
We conducted Integration Testing to ensure the modules worked together:

- **Test Case 1 (Registration):** Verified that a new user is added to the SQLite users table with a hashed password. (Result: Pass).
- **Test Case 2 (Image Upload):** Verified that uploading a non-image file (e.g., PDF) triggers the error handler in storage.py. (Result: Pass - Validation logic works).
- **Test Case 3 (Access Control):** Verified that a standard "Student" user cannot see the "Admin Panel" in the sidebar. (Result: Pass).

## 8. Lessons Learned
- The Importance of Managing "Scope Creep" One of the biggest lessons learned was the danger of "Scope Creep"—adding features that were not critical to the Minimum Viable Product (MVP). We spent significant time attempting to build a complex "Real-time Chat System" (Task 12). In hindsight, we should have prioritized perfecting the core "Lost Item Reporting" functions first.

Key Takeaway: In future projects, we will strictly define the MVP early and move "nice-to-have" features (like live chat) to a "Phase 2" backlog to ensure the core deadlines are met.

- Waterfall Planning vs. Agile Execution Our initial Gantt chart followed a rigid Waterfall methodology (completing one phase entirely before starting the next). However, during development, we found that we needed to jump back and forth between "Database Design" and "Frontend Development" as requirements became clearer.

Key Takeaway: A Hybrid approach would have been better. While the high-level schedule (Gantt) is useful for milestones, the day-to-day work requires an Agile approach to adapt to technical hurdles (like the Streamlit stateless issue) without derailing the whole schedule.

- Underestimation of Integration Time The schedule allocated time for building individual modules (Auth, Catalog, Reporting) but underestimated the time required to make them talk to each other. Merging the auth.py logic with the app.py frontend took longer than expected due to session state conflicts.

Key Takeaway: Future schedules should include a dedicated buffer specifically for "System Integration" rather than assuming components will plug-and-play instantly.

- Technical Debt and Architecture We initially started coding everything in a single file (app.py) to move fast. As the code grew to 400+ lines, debugging became nearly impossible, forcing us to stop and refactor the code into separate Views and Models mid-project.

Key Takeaway: Spending more time on "System Architecture" (Task 2) and setting up a modular folder structure before writing the first line of code saves significant time later. "Quick and dirty" coding creates technical debt that must eventually be paid with interest.
- **Separation of Concerns:** We learned the importance of separating UI code (views/) from logic (database.py). This made debugging significantly easier compared to our initial attempt where everything was in one file.
- **Stateless Web Apps:** We gained a deep understanding of how Streamlit handles sessions (st.session_state) and how to persist user data across page reloads.