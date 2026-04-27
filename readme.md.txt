# 🛡 Insurance Lead Management System

A fully modular, production-ready **Insurance Lead Management System** built in Python
using 7 design patterns, exposed as a **FastAPI REST API** with a **React dashboard**.

## 🏗 Design Patterns Used
| Pattern | Where |
|---|---|
| **Facade** | `LeadManagementFacade` — single entry point |
| **Repository** | `LeadRepository`, `AgentRepository` |
| **Factory** | `LeadFactory` — AUTO, HEALTH, LIFE, HOME leads |
| **Builder** | `LeadBuilder` — fluent method chaining |
| **Strategy** | `BasicScoringStrategy`, `PremiumScoringStrategy`, `RiskBasedScoringStrategy` |
| **Observer** | `EventBus`, `EmailNotifier`, `SMSNotifier`, `AuditLogger` |
| **Singleton** | `DatabaseConnection`, `AppConfig`, `EventBus` |

## 🚀 Quick Start

### With Docker (recommended)
```bash
git clone https://github.com/YOUR_USERNAME/insurance-lead-system.git
cd insurance-lead-system
mkdir -p data
docker compose up --build
```

Open:
- **Dashboard** → http://localhost:3000
- **API docs** → http://localhost:8000/docs

### Without Docker
```bash
pip install -r requirements.txt
uvicorn api.app:app --reload
```

## 📁 Project Structure
├── facade/           # LeadManagementFacade (entry point)
├── api/              # FastAPI routers + Pydantic schemas
├── services/         # Business logic
├── repositories/     # Data access layer
├── models/           # Domain models
├── strategies/       # Scoring strategies
├── observers/        # EventBus + notifiers
├── factories/        # Lead factory
├── builders/         # Lead builder
├── frontend/         # React dashboard
└── tests/            # pytest test suite

## 🧪 Run Tests
```bash
```
pytest tests/ -v

## further change in read me checkout2