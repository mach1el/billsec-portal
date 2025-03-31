# 📞 Django CDR Reporting Service

A **Django-based Call Detail Record (CDR) Reporting Service** that:
- Filters CDRs by **date range & project**.
- Displays a **full CDR report** with all columns.
- **Exports data to CSV**.
- Visualizes **SIP reason distribution** using a **pie chart**.
- Runs inside **Docker** with **PostgreSQL** support.

---

# 📑 Table of Contents

- [📞 Django CDR Reporting Service](#-django-cdr-reporting-service)
- [📑 Table of Contents](#-table-of-contents)
  - [🚀 Features](#-features)
  - [🗂 Database Design](#-database-design)
    - [1️⃣ Main Django Database](#1️⃣-main-django-database)
    - [2️⃣ CDR Data Warehouse (`central_data`)](#2️⃣-cdr-data-warehouse-central_data)
    - [🛠️ Go-based CDR Import Service](#️-go-based-cdr-import-service)
  - [⚙️ Installation](#️-installation)
    - [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
    - [2️⃣ Set Up Virtual Environment (Optional)](#2️⃣-set-up-virtual-environment-optional)
    - [3️⃣ Install Dependencies](#3️⃣-install-dependencies)
    - [4️⃣ Run Migrations](#4️⃣-run-migrations)
    - [5️⃣ Create a Superuser](#5️⃣-create-a-superuser)
    - [6️⃣ Run Development Server](#6️⃣-run-development-server)
  - [🐳 Docker Deployment](#-docker-deployment)
    - [1️⃣ Build Docker Image](#1️⃣-build-docker-image)
    - [2️⃣ Run Docker Container](#2️⃣-run-docker-container)
    - [3️⃣ Using Docker Compose](#3️⃣-using-docker-compose)
  - [🔧 Configuration](#-configuration)
    - [1️⃣ Database Setup](#1️⃣-database-setup)
    - [2️⃣ Modify Settings](#2️⃣-modify-settings)
  - [📊 CDR Report Filtering](#-cdr-report-filtering)
  - [🎨 Technologies Used](#-technologies-used)
  - [📜 API Endpoints](#-api-endpoints)
  - [🛠 Development \& Contribution](#-development--contribution)
  - [🔥 Future Enhancements](#-future-enhancements)
  - [📞 Support](#-support)

---

## 🚀 Features
- 📊 **Full CDR Reporting** with all fields.
- 🔍 **Filter by Date & Project Schema**.
- 📂 **Export to CSV**.
- 🐳 **Runs in Docker with PostgreSQL**.

---

## 🗂 Database Design

### 1️⃣ Main Django Database
- Stores:
  - User auth & admin accounts
  - Project schema connection info
  - UI configuration
  - Filtered queries

### 2️⃣ CDR Data Warehouse (`central_data`)
- Stores CDR data per project.
- Each project gets its own **table** under the same schema:
  - Table name = project `schema` field
- Populated by a separate **Go service** at the end of each day.

### 🛠️ Go-based CDR Import Service
- Polls all registered project databases.
- Aggregates daily CDR records.
- Imports the data into `central_data` under a table named after the project schema.
- Django UI queries from these tables on demand.

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/django-cdr-service.git
cd django-cdr-service
```

### 2️⃣ Set Up Virtual Environment (Optional)

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Migrations

```bash
python manage.py migrate
```

### 5️⃣ Create a Superuser

```bash
python manage.py createsuperuser
```

### 6️⃣ Run Development Server

```bash
python manage.py runserver
```

Then, visit http://localhost:8000.

## 🐳 Docker Deployment

### 1️⃣ Build Docker Image

```bash
docker build -t django-cdr .
```

### 2️⃣ Run Docker Container

```bash
docker run -p 8000:8000 django-cdr
```

### 3️⃣ Using Docker Compose

```bash
docker-compose up -d --build
```

## 🔧 Configuration

### 1️⃣ Database Setup

* Uses PostgreSQL (default) or MySQL.
* Set variables in .env or docker-compose.yml.

Example `.env` file:

```env
# Main database
DB_NAME=billsec_portal
DB_USER=billsec_portal
DB_PASSWORD=billsec_portal
DB_HOST=localhost
DB_PORT=5432

# Data Central for store cdr
DC_DB_NAME=data_central
DC_DB_USER=data_central
DC_DB_PASSWORD=data_central
DC_DB_HOST=localhost
DC_DB_PORT=2345
```

### 2️⃣ Modify Settings

Edit settings.py:

```python
DATABASES = {
  'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}
```

## 📊 CDR Report Filtering

The report supports:

- Date Range Selection (From & To).
- Project Schema Selection.
- Full Table Display (All Fields).
- CSV Export.

## 🎨 Technologies Used
- Django (Python)
- PostgreSQL (Database)
- Gunicorn (Production WSGI Server)
- Docker & Docker Compose (Containerization)

## 📜 API Endpoints

| Method | Endpoint         | Description         |
|--------|------------------|---------------------|
| GET    | /cdr            | View full CDR report |
| POST   | /cdr/export     | Export report as CSV |
| GET    | /projects       | Manage Projects      |
| GET    | /billing        | View Fare Report     |

## 🛠 Development & Contribution

1. Fork & Clone the Repo.
2. Set up a virtual environment.
3. Submit a Pull Request with improvements.

## 🔥 Future Enhancements

- 📥 CDR Data Import (SFTP, API).
- 📊 Advanced Analytics & Charts.
- 🔄 Live CDR Updates.

## 📞 Support
For issues, create a GitHub issue or contact `michaeldang.general@example.com`.

🚀 Enjoy your fully Dockerized Django CDR Reporting Service! 🎉