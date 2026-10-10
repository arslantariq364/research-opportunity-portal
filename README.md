# University Research Opportunity Portal

**Assignment:** Assignment No. 1  
**Current Phase:** Phase 2 of 5 (RESTful API & Database Integration)

---

## 1. Project Objective

The **University Research Opportunity Portal** is a web-based full-stack platform designed to connect undergraduate and graduate students with academic research initiatives led by university faculty. It provides faculty members with a centralized interface to post research openings across diverse academic departments and enables students to search, filter, and apply for opportunities aligned with their skills and academic pursuits.

---

## 2. Technology Stack

- **Backend:** Python 3 with [Flask](https://flask.palletsprojects.com/)
- **Database:** [MySQL](https://www.mysql.com/) 8.0+
- **ORM:** [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- **Database Driver:** [PyMySQL](https://pymysql.readthedocs.io/)
- **Frontend Scaffolding:** HTML5, CSS3, [Bootstrap 5](https://getbootstrap.com/), Vanilla JavaScript
- **Testing:** [Pytest](https://docs.pytest.org/) (Unit tests & isolated fixtures)
- **Configuration:** [python-dotenv](https://github.com/theskumar/python-dotenv)
- **Version Control:** Git

---

## 3. Project Directory Structure

```text
research-opportunity-portal/
├── backend/
│   ├── app.py                     # Flask application factory and server entry point
│   ├── check_db.py                # Database connectivity diagnostic utility
│   ├── config.py                  # Configuration loader (.env auto-discovery & DB URI)
│   ├── models.py                  # Flask-SQLAlchemy ResearchOpportunity model
│   ├── requirements.txt           # Python dependencies
│   ├── routes.py                  # RESTful API routes (Blueprint: /api)
│   ├── test_mysql_integration.py  # Live MySQL integration testing script
│   └── validators.py              # Reusable payload validation and business logic
├── frontend/
│   ├── css/
│   │   └── style.css              # Custom portal styling
│   ├── js/
│   │   └── app.js                 # Client-side JavaScript scaffolding
│   └── index.html                 # Bootstrap 5 portal landing page
├── database/
│   └── schema.sql                 # MySQL schema for research_portal & research_opportunities
├── postman/
│   └── README.md                  # Postman collection documentation (Phase 5)
├── tests/
│   ├── __init__.py                # Tests package initializer
│   ├── conftest.py                # Pytest fixtures with in-memory database
│   ├── test_api.py                # Comprehensive REST API test suite (15+ scenarios)
│   └── test_basic.py              # App factory, health check, and schema tests
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules for venvs, credentials, and caches
└── README.md                      # Project documentation
```

---

## 4. Current Development Status

| Feature / Milestone | Status | Description |
|---|---|---|
| **Phase 1: Project & Database Foundation** | **Completed** | Directory structure, MySQL schema, ORM model, config, git setup |
| **Phase 2: Complete REST API (CRUD)** | **Completed** | Full RESTful API with validation, status codes, and test suite |
| **Phase 3: Interactive Frontend UI** | *Pending* | Responsive opportunity list, detail view, creation form |
| **Phase 4: Client-Server Integration** | *Pending* | Asynchronous fetch requests connecting frontend to API |
| **Phase 5: Automated Testing & Postman** | *Pending* | Postman test collection and end-to-end testing |

---

## 5. REST API Architecture & Endpoints

The API is mounted under the `/api` prefix and adheres to RESTful conventions.

### Summary Table of Endpoints

| HTTP Method | Endpoint | Description | Success Code | Error Codes |
|---|---|---|---|---|
| `POST` | `/api/opportunities` | Create a new research opportunity | `201 Created` | `400`, `500` |
| `GET` | `/api/opportunities` | Retrieve all opportunities (Open & Closed) | `200 OK` | `500` |
| `GET` | `/api/opportunities/<id>` | Retrieve a single opportunity by its ID | `200 OK` | `404`, `500` |
| `PUT` | `/api/opportunities/<id>` | Update an existing opportunity (supports partial updates) | `200 OK` | `400`, `404`, `500` |
| `DELETE` | `/api/opportunities/<id>` | Delete an opportunity by its ID | `200 OK` | `404`, `500` |
| `GET` | `/api/health` | Service health status check | `200 OK` | `500` |

---

### Detailed Endpoint Specifications

#### 1. Create Opportunity (`POST /api/opportunities`)
Creates a new research opportunity record. The `id` is generated automatically by MySQL.

- **Request Body (JSON):**
  ```json
  {
      "title": "Autonomous Drone Path Planning",
      "description": "Developing reinforcement learning algorithms for obstacle avoidance in GPS-denied environments.",
      "research_area": "Robotics & AI",
      "faculty_name": "Dr. Usman Tariq",
      "department": "Computer Science",
      "required_skills": "Python, ROS, PyTorch, C++",
      "available_positions": 2,
      "application_deadline": "2026-12-15",
      "status": "Open"
  }
  ```
- **Validation Rules:**
  - All text fields (`title`, `description`, `research_area`, `faculty_name`, `department`, `required_skills`) must be non-empty and non-whitespace strings.
  - `available_positions` must be a strictly positive integer (`> 0`). Booleans (`true`/`false`) are rejected.
  - `application_deadline` must be a valid date in `YYYY-MM-DD` format. Impossible dates (e.g., `2026-02-30`) are rejected.
  - `status` accepts only `"Open"` or `"Closed"`. If omitted, it automatically defaults to `"Open"`.
  - Any unexpected or unsupported fields are rejected with `400 Bad Request`.
- **Response `201 Created`:**
  ```json
  {
      "id": 1,
      "title": "Autonomous Drone Path Planning",
      "description": "Developing reinforcement learning algorithms for obstacle avoidance in GPS-denied environments.",
      "research_area": "Robotics & AI",
      "faculty_name": "Dr. Usman Tariq",
      "department": "Computer Science",
      "required_skills": "Python, ROS, PyTorch, C++",
      "available_positions": 2,
      "application_deadline": "2026-12-15",
      "status": "Open"
  }
  ```

#### 2. Get All Opportunities (`GET /api/opportunities`)
Returns a JSON array of all stored opportunities. If no records exist, returns `[]`.
- **Response `200 OK`:**
  ```json
  [
      {
          "id": 1,
          "title": "Autonomous Drone Path Planning",
          "description": "Developing reinforcement learning algorithms...",
          "research_area": "Robotics & AI",
          "faculty_name": "Dr. Usman Tariq",
          "department": "Computer Science",
          "required_skills": "Python, ROS, PyTorch, C++",
          "available_positions": 2,
          "application_deadline": "2026-12-15",
          "status": "Open"
      }
  ]
  ```

#### 3. Get Opportunity by ID (`GET /api/opportunities/<id>`)
- **Response `200 OK`:** Returns single opportunity JSON object.
- **Response `404 Not Found` (if nonexistent or invalid ID):**
  ```json
  {
      "error": "Research opportunity not found"
  }
  ```

#### 4. Update Opportunity (`PUT /api/opportunities/<id>`)
Updates an existing record. Supports partial updates—only supplied fields are modified.
- **Request Body Example (Partial Update):**
  ```json
  {
      "available_positions": 4,
      "status": "Closed"
  }
  ```
- **Response `200 OK`:** Returns the full updated record JSON.
- **Response `400 Bad Request`:** Returned if submitted fields fail validation or contain unsupported keys.
- **Response `404 Not Found`:** Returned if the record does not exist.

#### 5. Delete Opportunity (`DELETE /api/opportunities/<id>`)
Deletes the specified opportunity.
- **Response `200 OK`:**
  ```json
  {
      "message": "Research opportunity deleted successfully"
  }
  ```
- **Response `404 Not Found`:** Returned if the record does not exist.

---

## 6. Local Setup and Execution

### Step 6.1: Environment and Dependencies

Ensure your virtual environment is active:
```bash
# From research-opportunity-portal/
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Verify your `.env` contains valid credentials:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=portal_user
DB_PASSWORD=your_secure_password
DB_NAME=research_portal
```

### Step 6.2: Verify MySQL Connectivity

Run the database connectivity diagnostic utility:
```bash
python backend/check_db.py
```

Expected output:
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

### Step 6.3: Run Automated Tests

Execute the automated test suite with pytest:
```bash
.venv/bin/pytest -v
```

All 24 unit and API tests will run against an isolated in-memory test database.

### Step 6.4: Run Real MySQL Integration Test

To verify end-to-end persistence against your live MySQL server:
```bash
python backend/test_mysql_integration.py
```

This test creates a temporary test record in MySQL, reads it, modifies it, closes its status, deletes it, and verifies `404 Not Found` upon retrieval.

### Step 6.5: Start the Flask Application Server

Start the development server:
```bash
python backend/app.py
```
Server runs at `http://127.0.0.1:5000`.

---

## 7. Manual API Testing Examples (cURL)

With the server running, you can test the REST API from another terminal window:

### 1. Create a Research Opportunity (POST)
```bash
curl -X POST http://127.0.0.1:5000/api/opportunities \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quantum Error Correction",
    "description": "Researching surface code decoders for fault-tolerant quantum computing architectures.",
    "research_area": "Quantum Computing",
    "faculty_name": "Dr. Sarah Ahmed",
    "department": "Computer Science",
    "required_skills": "Python, Qiskit, Linear Algebra",
    "available_positions": 2,
    "application_deadline": "2026-11-30",
    "status": "Open"
  }'
```

### 2. Retrieve All Opportunities (GET)
```bash
curl -X GET http://127.0.0.1:5000/api/opportunities
```

### 3. Retrieve Single Opportunity by ID (GET)
```bash
curl -X GET http://127.0.0.1:5000/api/opportunities/1
```

### 4. Update an Opportunity (PUT)
```bash
curl -X PUT http://127.0.0.1:5000/api/opportunities/1 \
  -H "Content-Type: application/json" \
  -d '{
    "available_positions": 5,
    "status": "Closed"
  }'
```

### 5. Delete an Opportunity (DELETE)
```bash
curl -X DELETE http://127.0.0.1:5000/api/opportunities/1
```
