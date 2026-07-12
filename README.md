# AssetFlow — Enterprise Asset & Resource Management System

A full-stack ERP platform for organisations to track physical assets, allocate
them to employees/departments, book shared resources, manage maintenance
workflows, and run periodic audit cycles.

**Stack:** Django + DRF + MySQL · React (Vite) + Tailwind CSS · JWT auth

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| MySQL | 8.0+ |

---

## Backend setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt

# Copy env and fill in your values
cp ../.env.example ../.env

# Create the MySQL database
mysql -u root -p -e "CREATE DATABASE assetflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
python manage.py migrate

# Create a superuser (will be the initial Admin)
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

API is available at `http://localhost:8000/api/v1/`

---

## Frontend setup

```bash
cd frontend

npm install

# Copy env for Vite
cp ../.env.example .env.local
# Set VITE_API_BASE_URL=http://localhost:8000/api/v1

npm run dev
```

App is available at `http://localhost:5173/`

---

## Project structure

```
AssetFlow/
├── backend/          Django project (assetflow/) + 9 domain apps
├── frontend/         React (Vite) app
├── docs/             ASSETFLOW_SPEC.md, THEME.md
├── .env.example      Template — copy to .env and fill values
└── README.md
```

See `docs/ASSETFLOW_SPEC.md` for full module specifications and business rules.
See `docs/THEME.md` for the design-system tokens and component guidelines.

---

## Roles

| Role | Permissions |
|------|-------------|
| Admin | Org setup, role promotion, org-wide analytics |
| Asset Manager | Register/allocate assets, approve workflows |
| Department Head | Department-scoped views, book resources |
| Employee | Own allocations, book resources, raise requests |

> Signup always creates an **Employee** account. Roles are assigned by an Admin only.

---

## Build phases

| Phase | Modules |
|-------|---------|
| 1 — Foundation | Auth/RBAC, org setup, asset registry, dashboard shell |
| 2 — Core workflows | Allocation & transfer, resource booking, maintenance |
| 3 — Polish | Audit cycles, reports, notifications, overdue jobs |
