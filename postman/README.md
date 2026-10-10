# Postman API Test Suite — University Research Opportunity Portal

This directory contains the official Postman Collection (v2.1 format) for automated and manual REST API verification of the University Research Opportunity Portal (Phase 4).

## Collection File
- **File**: `Research_Opportunity_Portal.postman_collection.json`
- **Specification**: Postman Collection Format v2.1.0
- **Base URL**: `http://127.0.0.1:5000` (configurable via `baseUrl` collection variable)

---

## Required Request Workflow (10 Sequential Requests)

The collection is designed to run sequentially from top to bottom. It creates its own isolated records, captures generated IDs dynamically, and cleans up after itself:

| # | Request Name | Method | Path | Expected Status | Purpose |
|---|--------------|--------|------|-----------------|---------|
| **01** | Create Opportunity 1 | `POST` | `/api/opportunities` | `201 Created` | Creates test record in Computer Science; stores auto-generated ID into `{{opportunity_id}}` variable. |
| **02** | Create Opportunity 2 | `POST` | `/api/opportunities` | `201 Created` | Creates test record in Electrical Engineering (Robotics). |
| **03** | Create Opportunity 3 | `POST` | `/api/opportunities` | `201 Created` | Creates test record in Biomedical Engineering (Bioinformatics). |
| **04** | Retrieve All Opportunities | `GET` | `/api/opportunities` | `200 OK` | Retrieves all opportunities and verifies the newly created records are present. |
| **05** | Retrieve Opportunity by ID | `GET` | `/api/opportunities/{{opportunity_id}}` | `200 OK` | Retrieves specific opportunity matching the captured ID. |
| **06** | Update Opportunity | `PUT` | `/api/opportunities/{{opportunity_id}}` | `200 OK` | Updates title, available positions, and description. |
| **07** | Close Opportunity | `PUT` | `/api/opportunities/{{opportunity_id}}` | `200 OK` | Updates status to `Closed`. |
| **08** | Delete Opportunity | `DELETE` | `/api/opportunities/{{opportunity_id}}` | `200 OK` | Deletes the captured test record. |
| **09** | Retrieve Deleted Opportunity | `GET` | `/api/opportunities/{{opportunity_id}}` | `404 Not Found` | Verifies the deleted opportunity returns HTTP 404 error response. |
| **10** | Invalid Data Request | `POST` | `/api/opportunities` | `400 Bad Request` | Submits missing and invalid fields; verifies 400 rejection and validation error messages. |

---

## Dynamic Variable & ID Handling
- **`baseUrl`**: Initial value set to `http://127.0.0.1:5000`. You can change this if your Flask server runs on a different port or host.
- **`opportunity_id`**: Dynamically set by Request 01 (`pm.collectionVariables.set("opportunity_id", jsonData.id)`). Downstream requests (05, 06, 07, 08, 09) use `{{opportunity_id}}` automatically without hardcoding record IDs.

---

## How to Import and Run in Postman

### Step 1: Start the Backend Server
Ensure the Flask backend is running:
```bash
source .venv/bin/activate
python backend/app.py
```
The server will start on `http://127.0.0.1:5000`.

### Step 2: Import into Postman
1. Open the Postman desktop application or Postman Web.
2. In the top left navigation bar, click the **Import** button.
3. Drag and drop the file `postman/Research_Opportunity_Portal.postman_collection.json` or click **files** to browse and select it.
4. Click **Import**. The collection **Research Opportunity Portal** will now appear under your Collections sidebar.

### Step 3: Run the Entire Collection
1. Click the collection name **Research Opportunity Portal** in the sidebar.
2. Click the **Run** button (or click **...** and choose **Run collection**).
3. Ensure all 10 requests are selected in order.
4. Click **Run Research Opportunity Portal**.
5. All test assertions will execute sequentially, displaying green checkmarks for all status codes, JSON schemas, field validations, status transitions, and error handling.
