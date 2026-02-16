# Django Clean Architecture - Plant Store API

This project implements a RESTful API for managing Plant Items using **Django Rest Framework (DRF)** and following the principles of **Clean Architecture**.

It demonstrates how to decouple the business logic from the framework (`Django`), ensuring scalability, testability, and maintainability.

## 🚀 Features

- **Clean Architecture Layers**:
  - `Domain` (Pure Python, no Django dependencies)
  - `Application` (Use Cases, DTOs)
  - `Infrastructure` (Django ORM, Mappers)
  - `Interfaces` (DRF Views, Serializers)
- **Shared Core**: Shared infrastructure components and global exception handling.
- **RESTful API**: Complete CRUD for `PlantItem`.
- **API Documentation**: Automated Swagger/OpenAPI documentation via `drf-spectacular`.
- **Linting**: Pre-configured `pylint-django` for code quality.

## 🛠️ Tech Stack

- **Python**: 3.12+
- **Django**: 5.x / 6.x
- **Django Rest Framework**: 3.x
- **drf-spectacular**: OpenAPI Schema generation
- **Pylint**: Code analysis

## 📂 Project Structure

```bash
store/
├── domain/           # Enterprise Business Rules (Entities, Exceptions, Repository Interfaces)
├── application/      # Application Business Rules (Use Cases, DTOs)
├── infrastructure/   # Frameworks & Drivers (Models, Mappers, Repository Implementations)
├── interfaces/       # Interface Adapters (Views, Serializers, URLs)
└── tests/            # Unit and Integration Tests
core/                 # Shared Kernel (Abstract Models, Global Handlers)
```

## ⚡ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/daniel061295/django-clean-architecture-crud.git
cd django-clean-architecture-crud
```

### 2. Set up Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run Server
```bash
python manage.py runserver
```

## 📖 API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

## 🧪 Running Tests
```bash
python manage.py test store
```
