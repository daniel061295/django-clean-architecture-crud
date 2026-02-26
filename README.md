# Django Clean Architecture - Plant Store API

This project implements a RESTful API for managing a Plant Store (Items, Categories, Providers, Inventory, and Sales) using **Django Rest Framework (DRF)** and following the principles of **Clean Architecture**.

It demonstrates how to decouple the business logic from the framework (`Django`), ensuring scalability, testability, and maintainability by using **Dependency Injection** and a modular structure.

## 🚀 Features

- **Clean Architecture Layers**:
  - `Domain`: Pure Python entities and repository interfaces.
  - `Application`: Use Cases and DTOs.
  - `Infrastructure`: Data persistence (Django ORM), Mappers, and Repository implementations.
  - `Interface Adapters`: DRF Views, Serializers, and URLs.
- **Modular Design**: The project is organized by business domains (Category, PlantItem, Provider, Inventory, Sale, Tips, History, Plant Health).
- **Dependency Injection**: Decoupled components using `injector` and `django-injector`, with modular DI configuration.
- **Complete CRUD Operations**:
  - Full CRUD for Categories, Plant Items, and Providers.
  - Inventory Movements and Sales management.
- **Dynamic Tips**:
  - Managed plant care tips with a **Random Tip** endpoint.
  - Backend-side state tracking using **Django Cache** to ensure non-consecutive results.
- **AI-Powered Plant Diagnostics**:
  - Plant health analysis integrated with **Google Gemini AI**.
  - Advanced diagnostic logic and history tracking for user interactions.
- **Plant Store History**:
  - Comprehensive audit trail and scan history tracking.
- **RESTful API**: Structured endpoints for all entities.
- **API Documentation**: Automated Swagger/OpenAPI documentation via `drf-spectacular`.
- **Advanced Testing**: Comprehensive test suite using `pytest`.

## 🛠️ Tech Stack

- **Python**: 3.14.2
- **Django**: 6.0.x
- **Django Rest Framework**: 3.15+
- **Google Gemini AI**: For plant health diagnostics.
- **Injector**: Dependency injection library.
- **django-injector**: Django integration for injector.
- **drf-spectacular**: OpenAPI Schema generation.
- **pytest-django**: Testing framework.

## 📂 Project Structure

The project follows a modular structure where each business entity has its own Clean Architecture layers:

```bash
store/
├── category/            # Category domain logic & DI
├── plant_item/          # Plant Item domain logic & DI
├── provider/            # Provider domain logic & DI
├── inventory_movement/  # Inventory management logic & DI
├── sale/                # Sales management logic & DI
├── tips/                # Plant care tips & Random Tip logic
├── history/             # User scan history & audit trails
├── plant_health/        # Plant diagnostic analysis logic
├── management/          # Custom Django-admin commands (Seeding, etc.)
├── di.py                # Main Dependency Injection aggregator
├── models.py            # Shared Django persistence models
└── urls.py              # Application-wide routing
tests/                   # Comprehensive test suite organized by layers
core/                    # Shared Kernel (Cross-cutting concerns)
```

Each module contains:
- `domain/`: Entities, repository interfaces, and domain exceptions.
- `application/`: Use cases and DTOs.
- `infrastructure/`: Repository implementations and Object-Mapping logic.
- `interfaces/`: Views and Serializers.
- `di.py`: Entity-specific dependency injection configuration.

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

### 4. Environment Configuration
Create a `.env` file in the root directory and add the following:
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your-google-gemini-api-key
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 5. Run Server
```bash
python manage.py runserver
```

### 6. Seed Initial Data (Optional)
To populate the database with gardening tips:
```bash
python manage.py seed_tips
```

## 📖 API Documentation

Access the interactive documentation at:

- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

## 🧪 Running Tests

The project uses `pytest` for testing. The configuration in `pytest.ini` ensures proper package discovery by treating the `tests/` directory as a package.

### Standard Tests
```bash
pytest
```

### Specific Test Modules
```bash
pytest tests/domain/
pytest tests/application/
```

## 🛠️ Maintenance & Refactoring

The project uses a modular DI approach. If you add a new entity:
1. Create a `di.py` in the entity's folder.
2. Define a `Module` and its providers.
3. Install the module in `store/di.py` within the `StoreModule.configure` method.
