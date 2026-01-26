# 📂 AI CORE - PROJECT STRUCTURE

**Version**: 1.1.3  
**Last Updated**: 2026-01-26

---

## 🎯 CẤU TRÚC CHUẨN (PRODUCTION-READY)

```
AI_core/
│
├── 📁 app/                         # Source code chính
│   ├── 📁 api/                     # REST API layer
│   │   ├── __init__.py
│   │   └── chat.py                 # FastAPI endpoints (7 endpoints)
│   │
│   ├── 📁 core/                    # Business logic (NÃO DỰ ÁN)
│   │   ├── __init__.py
│   │   ├── engine.py               # AI Core orchestrator (9-step pipeline)
│   │   ├── context.py              # Context analyzer (3 contexts)
│   │   ├── persona.py              # Persona selector (3 personas)
│   │   ├── prompt.py               # Prompt builder
│   │   ├── output.py               # Output processor & validator
│   │   └── logging.py              # Structured logging (structlog)
│   │
│   ├── 📁 memory/                  # Data persistence
│   │   ├── __init__.py
│   │   ├── schema.py               # Pydantic schemas (Message, Memory, Session)
│   │   ├── short_term.py           # In-memory session storage
│   │   └── long_term.py            # SQLite persistence
│   │
│   ├── 📁 model/                   # LLM abstraction
│   │   ├── __init__.py
│   │   └── client.py               # Multi-provider client (4 providers)
│   │
│   ├── 📁 tools/                   # Tool system
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseTool + example tools
│   │   └── router.py               # Tool routing & execution
│   │
│   └── 📁 config/                  # Configuration files
│       ├── persona.yaml            # 3 personas config
│       ├── rules.yaml              # Core rules + context detection
│       └── system.yaml             # System settings
│
├── 📁 data/                        # Runtime data (gitignored)
│   ├── app.log                     # Application logs
│   └── memory.db                   # SQLite database
│
├── 📁 tests/                       # Test files
│   └── (test files here)
│
├── 📁 md/                          # Reference materials
│   └── (markdown notes)
│
├── 📁 .github/                     # GitHub config
│   └── instructions/
│
├── 📄 main.py                      # Entry point (uvicorn server)
├── 📄 test_core.py                 # Test script (4 test cases)
├── 📄 example_conversation.py      # Demo conversation script
├── 📄 requirements.txt             # Python dependencies (9 packages)
├── 📄 .env.example                 # Environment config template
├── 📄 .gitignore                   # Git ignore rules
│
├── 📖 README.md                    # ⭐ Main documentation
├── 📖 QUICK_START.md               # ⭐ Getting started guide
├── 📖 CODEBASE_ANALYSIS.md         # ⭐ Technical deep dive (1000+ lines)
├── 📖 TODO.md                      # ⭐ Progress tracking
├── 📖 CHANGELOG.md                 # ⭐ Version history
└── 📖 STRUCTURE.md                 # ⭐ This file (project structure)
```

---

## 📊 FILE STATISTICS

### Source Code (app/)
- **Total files**: 19 Python files + 3 YAML files = 22 files
- **Lines**: ~2,000 lines
- **Languages**: Python, YAML

### Documentation
- **Total files**: 7 markdown files
  - Root: 3 files (README.md, QUICK_START.md, CHANGELOG.md)
  - docs/: 4 files (API_REFERENCE.md, CODEBASE_ANALYSIS.md, STRUCTURE.md, TODO.md)
- **Lines**: ~2,500+ lines
- **Purpose**: User guide, technical docs, API reference, tracking

### Configuration
- **YAML files**: 3 files
- **Purpose**: Personas, rules, system settings

---

## 🎯 DOCUMENTATION MAP

| File | Purpose | Audience | Size |
|------|---------|----------|------|
| **README.md** | Main documentation, installation, API | All users | ~150 lines |
| **QUICK_START.md** | Quick start guide, examples | New users | ~200 lines |
| **CODEBASE_ANALYSIS.md** | Architecture, technical deep dive | Developers | ~1000 lines |
| **TODO.md** | Progress tracking, task list | Team | ~140 lines |
| **CHANGELOG.md** | Version history | All users | ~40 lines |
| **STRUCTURE.md** | Project structure guide | All users | This file |

**Quy tắc**: 
- Muốn bắt đầu nhanh → đọc **QUICK_START.md**
- Muốn hiểu system → đọc **README.md**
- Muốn phát triển → đọc **CODEBASE_ANALYSIS.md**
- Muốn track progress → đọc **TODO.md**

---

## 🔧 CORE COMPONENTS

### 1. API Layer (app/api/)
- **chat.py**: 7 REST endpoints
- FastAPI + CORS
- Pydantic validation
- Error handling

### 2. Core Logic (app/core/)
- **engine.py**: Main orchestrator (9-step pipeline)
- **context.py**: Context analyzer (casual/technical/cautious)
- **persona.py**: Persona selector (3 personas)
- **prompt.py**: Prompt builder với history
- **output.py**: Output validation
- **logging.py**: Structured logging với request tracing

### 3. Memory (app/memory/)
- **short_term.py**: In-memory sessions
- **long_term.py**: SQLite persistence
- **schema.py**: Data models

### 4. Model (app/model/)
- **client.py**: Multi-provider abstraction
  - Mock (testing)
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  - Local (llama.cpp, vLLM)

### 5. Tools (app/tools/)
- **base.py**: BaseTool + examples
- **router.py**: Tool management

---

## 🚀 QUICK REFERENCE

### Start Server
```bash
python main.py
# → http://localhost:8000
```

### Run Tests
```bash
python test_core.py
# → 4/4 tests should pass
```

### API Endpoints
```
GET  /                          # Health check
POST /chat                      # Main chat
POST /chat/new-session          # Create session
GET  /chat/history/{id}         # Get history
DELETE /chat/session/{id}       # Clear session
POST /admin/cleanup             # Cleanup old data
GET  /admin/stats               # System stats
```

### Key Files to Modify
- **Change model provider**: `.env` (MODEL_PROVIDER)
- **Add new persona**: `app/config/persona.yaml`
- **Add context rules**: `app/config/rules.yaml`
- **Add new tool**: `app/tools/base.py`

---

## 📏 CODE STANDARDS

### File Organization
- `__init__.py` exports public API
- Classes in separate files
- YAML cho configuration
- Docstrings cho tất cả functions

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Constants: `UPPER_CASE`
- Config files: `lowercase.yaml`

---

## 🧹 MAINTENANCE

### Files cần cleanup định kỳ:
- `data/app.log` - Logs (rotate khi > 100MB)
- `data/memory.db` - Database (cleanup old memories)
- `tests/__pycache__/` - Python cache

### Files KHÔNG nên edit trực tiếp:
- `data/` - Auto-generated
- `__pycache__/` - Python cache
- `.pyc` files - Compiled Python

---

## 📦 DEPENDENCIES

```txt
fastapi==0.109.0        # REST API framework
uvicorn==0.27.0         # ASGI server
pydantic==2.5.3         # Data validation
sqlalchemy==2.0.25      # ORM
pyyaml==6.0.1           # YAML parser
structlog==24.1.0       # Structured logging
httpx==0.26.0           # HTTP client
python-multipart==0.0.6 # Form data
python-dotenv==1.0.0    # Environment variables
```

---

## 🎓 LEARNING PATH

### Beginners (Muốn dùng AI Core)
1. README.md - Hiểu tổng quan
2. QUICK_START.md - Chạy thử
3. Thử modify `app/config/persona.yaml`

### Intermediate (Muốn customize)
1. CODEBASE_ANALYSIS.md - Hiểu kiến trúc
2. Đọc `app/core/engine.py` - Pipeline
3. Đọc `app/core/context.py` - Context detection
4. Thử add tool mới trong `app/tools/`

### Advanced (Muốn phát triển core)
1. Đọc toàn bộ `app/core/`
2. Hiểu data flow trong CODEBASE_ANALYSIS.md
3. Đọc `app/memory/` - Persistence
4. Implement RAG trong `engine.py`

---

## 🔒 SECURITY NOTES

- ⚠️ `.env` file chứa API keys - KHÔNG commit
- ⚠️ `data/` folder - gitignored, chứa sensitive data
- ⚠️ Production nên dùng proper secrets management
- ⚠️ CORS set `allow_origins=["*"]` - nên restrict trong production

---

## 📈 FUTURE EXPANSION

Xem [TODO.md](TODO.md) section "SẮP LÀM" cho roadmap.

Core areas:
1. RAG/Vector search
2. More tools (web search, calculator)
3. Unit tests với pytest
4. Metrics + monitoring
5. Docker containerization

---

**Project Status**: ✅ **PRODUCTION READY**  
**Last Build**: 2026-01-26  
**Version**: 1.1.3
