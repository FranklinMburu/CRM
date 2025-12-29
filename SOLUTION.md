# Audit Logging Feature — Solution

## 1. Feature Choice & Rationale

I implemented an **Audit Logging** feature to enhance accountability, traceability, and trust within the MiniCRM system.

CRMs manage sensitive customer and business data. In real-world production systems, it is critical to know **who changed what, when, and why**. Audit logs are a foundational feature for:

* Security & compliance
* Debugging and incident investigation
* Team accountability
* Operational transparency

Rather than adding surface-level CRUD functionality, I chose a feature that reflects **how mature systems are actually built**.

---

## 2. Product & Security Design Decision (Why Read-Only)

Audit logs are intentionally implemented as **read-only** resources.

Allowing audit records to be edited or deleted would undermine their purpose as a source of truth. In production systems, audit logs must be immutable to maintain integrity and reliability.

Key design decisions:

* Audit logs are **created automatically by the backend**
* No public API endpoints exist for creating, updating, or deleting audit records
* Only authenticated users can view audit logs

This is a deliberate security and product decision, not a limitation.

---

## 3. Backend Implementation (Django REST Framework)

### New Model

A new `AuditLog` model was introduced with the following fields:

* `user` — User who performed the action
* `action` — CREATE / UPDATE / DELETE
* `entity_type` — Affected model (Lead, Contact, Reminder, etc.)
* `entity_id` — ID of the affected record
* `timestamp` — When the action occurred
* `ip_address` — Source IP (if available)

### Integration with Existing Models

Audit logs are automatically generated when core CRM entities are modified:

* Leads
* Contacts
* Reminders

This ensures full integration with existing domain models as required by the assessment.

### API Endpoints

* `GET /api/audit-logs/` — List audit logs (authenticated users only)

Creation of audit logs happens internally via backend logic and is not exposed as a public endpoint.



## 4. Frontend Implementation (Vue 3 + Vuetify)

### Audit Logs View

A dedicated **Audit Logs** page was added to the frontend:

* Read-only table view using Vuetify
* Search functionality across user, action, entity, and IP
* Color-coded action indicators (Create / Update / Delete)
* Human-readable timestamps
* Loading and empty states handled

### Navigation

The Audit Logs page is accessible via the main sidebar navigation and protected by existing authentication guards.

The frontend strictly follows established project patterns and styling conventions.

---

## 5. Testing Strategy

To ensure correctness and reliability, backend tests focus on **business logic and security**, which are the most critical aspects of this feature.

### Test Coverage

The following tests are implemented:

1. Audit log is created when a Lead is created
2. Audit log is created when a Lead is updated
3. Audit log is created when a Lead is deleted
4. Unauthenticated users cannot access audit logs
5. Authenticated users can successfully retrieve audit logs

This approach validates integration with existing models, access control, and core feature behavior.

---

## 6. Trade-offs & Decisions

### What Was Intentionally Not Implemented

* Manual creation of audit logs
* Editing or deleting audit records

These were excluded to preserve audit integrity and reflect real-world best practices.

---

## 7. Database Migrations

* A new migration was added for the `AuditLog` model
* Migrations run successfully on a fresh database
* No existing data is affected

---

## 8. Setup & Testing Instructions

```bash
python manage.py migrate
python manage.py test
npm install
npm run dev
```

---

## 9. Future Improvements

Potential enhancements include:

* Server-side filtering by user, entity, or date range
* Exporting audit logs (CSV / PDF)
* Retention policies and archival
* Role-based visibility (e.g., admin-only access)

---

## Final Notes

This feature was designed to balance scope, security, and real-world relevance. It integrates deeply with existing models, adheres to established patterns, and demonstrates both technical execution and product-level decision making.


Testing
How to Run the Tests

All backend tests for the Audit Logs feature are located in:

backend/tasks/tests.py

To run the tests locally:

# Activate virtual environment (if applicable)
source venv/bin/activate


# Run audit log tests only
python manage.py test tasks


# Or run the full backend test suite
python manage.py test

The test runner will:

Create a temporary test database

Apply all migrations (including audit log migrations)

Execute the test suite in isolation

Destroy the database after completion

Expected result:

Ran 5 tests in X.XXXs
OK
What the Tests Cover

The Audit Logs feature is validated by 5 backend tests, covering all required behaviors:

CREATE action logging

Verifies that creating a model instance generates an audit log entry

Confirms action type (CREATE), entity type, entity ID, user, and captured new_values

UPDATE action logging

Verifies that updating an existing model generates an audit log entry

Confirms action type (UPDATE)

Validates both old_values and new_values reflect the field change

DELETE action logging

Verifies that deleting a model generates an audit log entry

Confirms action type (DELETE)

Ensures old_values are preserved and new_values is empty

Unauthenticated access protection

Verifies that unauthenticated requests to /api/audit-logs/ return 401 Unauthorized

Authenticated access

Verifies that authenticated users can retrieve audit logs

Confirms response structure, pagination, and required fields

Test Characteristics

Tests use Django TestCase and DRF APITestCase

No mocking is used; tests validate real signal execution

Each test is isolated and deterministic

Tests can run in any order with consistent results

Audit context is explicitly set and cleared within tests