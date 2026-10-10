# University Research Opportunity Portal

**Assignment:** Assignment No. 1  
**Current Phase:** Phase 1 of 5 (Project Structure, Database Design & Configuration)

---

## 1. Project Objective

The **University Research Opportunity Portal** is a web-based full-stack platform designed to bridge the gap between undergraduate/graduate students and university faculty. It enables faculty members to post research vacancies across academic departments, while allowing students to discover, filter, and apply for open research positions matching their skill sets.

---

## 2. Technology Stack

- **Backend:** Python 3 with [Flask](https://flask.palletsprojects.com/)
- **Database:** [MySQL](https://www.mysql.com/) (Version 8.0+)
- **ORM:** [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- **Database Driver:** [PyMySQL](https://pymysql.readthedocs.io/)
- **Frontend:** HTML5, CSS3, [Bootstrap 5](https://getbootstrap.com/), Vanilla JavaScript
- **Testing:** [Pytest](https://docs.pytest.org/) and [Postman](https://www.postman.com/)
- **Version Control:** Git

---

## 3. Project Directory Structure

```text
research-opportunity-portal/
├── backend/
│   ├── app.py                # Application factory and Flask entry point
│   ├── config.py             # Configuration loader (MySQL URI & environment variables)
│   ├── models.py             # Flask-SQLAlchemy ResearchOpportunity model
│   ├── routes.py             # API routes & Blueprint definitions
│   ├── validators.py         # Request validation logic
│   ├── check_db.py           # Database connectivity diagnostic script
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Main web portal interface (Bootstrap 5)
│   ├── css/
│   │   └── style.css         # Custom portal styles
│   └── js/
│       └── app.js            # Frontend JavaScript logic
├── database/
│   └── schema.sql            # MySQL database & table initialization script
├── postman/
│   └── README.md             # Postman API test collection documentation
├── tests/
│   ├── __init__.py           # Tests package initializer
│   ├── conftest.py           # Pytest test fixtures and configuration
│   └── test_basic.py         # App factory, health check, and model verification tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore patterns for venvs, credentials, and caches
└── README.md                 # Project documentation
```

---

## 4. Current Development Status

| Feature / Component | Status | Details |
|---|---|---|
| **Project Directory Structure** | **Completed** | Full modular architecture established |
| **Relational Schema (MySQL)** | **Completed** | `research_opportunities` table with strict constraints |
| **SQLAlchemy ORM Mapping** | **Completed** | `ResearchOpportunity` model aligned with SQL schema |
| **Environment Configuration** | **Completed** | Flexible `.env` loading from root or backend directory |
| **Git Version Control** | **Completed** | Initialized repository with comprehensive `.gitignore` |
| **Automated Unit Tests** | **Completed** | Pytest test suite for app creation and schema mapping |
| **RESTful CRUD Endpoints** | *Pending* | Scheduled for Phase 2 |
| **Interactive Frontend UI** | *Pending* | Scheduled for Phase 3 |
| **Client-Server Integration** | *Pending* | Scheduled for Phase 4 |
| **End-to-End & Postman Testing** | *Pending* | Scheduled for Phase 5 |

---

## 5. Local Setup & Database Instructions

### Step 5.1: Create a Dedicated Local MySQL User & Database

To ensure security, do not use the MySQL root user in application configuration. Create a dedicated database user with privileges restricted to the `research_portal` database.

Log into your local MySQL server as administrator:
```bash
sudo mysql
```

Execute the following SQL statements (replace `'your_secure_password'` with your preferred password):

```sql
-- 1. Create the database
CREATE DATABASE IF NOT EXISTS research_portal
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Create dedicated user
CREATE USER IF NOT EXISTS 'portal_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- 3. Grant privileges on the application database
GRANT ALL PRIVILEGES ON research_portal.* TO 'portal_user'@'localhost';

-- 4. Flush privileges to apply changes
FLUSH PRIVILEGES;

-- 5. Exit MySQL prompt
EXIT;
```

---

### Step 5.2: Initialize the Database Schema

Import the schema definition from the project root:

```bash
mysql -u portal_user -p research_portal < database/schema.sql
```
*(Enter the password you assigned to `portal_user` when prompted).*

---

### Step 5.3: Set Up Python Virtual Environment & Dependencies

From the `research-opportunity-portal/` directory:

```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install required packages
pip install -r backend/requirements.txt
```

---

### Step 5.4: Configure Environment Variables

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

Open `.env` in your text editor and update `DB_PASSWORD` (and other parameters if customized):

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=portal_user
DB_PASSWORD=your_secure_password
DB_NAME=research_portal

FLASK_APP=backend/app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=replace-with-a-random-secret-key-in-production
```

---

### Step 5.5: Verify Database Connectivity

Run the included verification diagnostic script:

```bash
python backend/check_db.py
```

Expected output on successful connection:
```text
============================================================
University Research Opportunity Portal - Database Connectivity Check
============================================================
Host:     localhost
Port:     3306
User:     portal_user
Database: research_portal
------------------------------------------------------------
[SUCCESS] Connected to MySQL successfully! Version: 8.0.x
[SUCCESS] Table 'research_opportunities' exists in database.
============================================================
```

---

### Step 5.6: Run the Backend Server

Start the Flask development server:

```bash
python backend/app.py
```

The application will run at:
- Root info endpoint: `http://127.0.0.1:5000/`
- API Health check: `http://127.0.0.1:5000/api/health`

---

### Step 5.7: Run Automated Tests

Execute the unit test suite with pytest:

```bash
pytest
```
