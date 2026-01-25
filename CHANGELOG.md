# CHANGELOG

All notable changes to AI Core will be documented in this file.

## [Unreleased]

## [1.1.2] - 2026-01-25

### Fixed
- **OpenAI API compliance**: `_openai_complete()` giờ tuân thủ 100% OpenAI API docs
  - Thêm `stream: False` explicit parameter
  - Response validation trước khi parse (check choices, message, content)
  - Parse OpenAI error messages correctly từ response JSON
  - Better error handling: HTTPStatusError, TimeoutException với messages rõ ràng
  - Default values cho usage khi API không trả về

- **Local model API improvements**: `_local_complete()` enhanced cho LM Studio/Ollama/vLLM
  - Thêm `stream: False` và proper headers
  - Minimum timeout 60s (local models chậm hơn cloud)
  - ConnectError handling với helpful message "is the server running?"
  - Response validation đầy đủ như OpenAI
  - Specific error messages cho từng error type

### Improved
- Error messages giờ rõ ràng hơn, giúp debug nhanh
- Validate response structure trước khi access fields (tránh KeyError)
- Timeout messages nhắc user check model loaded

## [1.1.1] - 2026-01-25

### Fixed
- Local model endpoint confirmed using `/v1/chat/completions` (OpenAI-compatible)
- Full support for LM Studio, Ollama, vLLM, llama.cpp

### Changed
- Clarified **Hybrid Architecture** in documentation
- AI Core = Framework (core logic) + Model Abstraction (flexible providers)
- Core logic independent: context/persona/prompt/output
- Model layer: abstraction cho nhiều providers

### Documentation
- README.md: Thêm hybrid approach explanation
- QUICK_START.md: LM Studio default port 1234
- .env.example: Specific configs cho LM Studio/Ollama/vLLM
- CODEBASE_ANALYSIS.md: Clarify architecture design

## [1.1.0] - 2026-01-25

### Added
- Environment-based provider selection via `.env` file
- `.env.example` template file with 4 provider options
- `python-dotenv` dependency for environment variables
- Automatic provider selection in `app/api/chat.py`
- Support for MODEL_PROVIDER env var (mock/openai/anthropic/local)
- Structured logging with provider info on startup

### Changed
- Model provider selection now via `.env` instead of code changes
- Updated README.md with `.env` configuration guide
- Updated QUICK_START.md with simplified setup (4 options)
- Updated STRUCTURE.md with `.env.example` reference
- Simplified developer experience - no code changes needed

### Fixed
- QUICK_START.md section numbering (was 1,2,3,6,6,7,8 → now 0-7)
- Documentation consistency across all files

## [1.0.0] - 2026-01-25

### Added
- Initial project structure
- Core AI engine with context awareness
- Persona system (casual, technical, cautious)
- Short-term and long-term memory
- Model client abstraction (OpenAI, Anthropic, local, mock)
- FastAPI REST API
- Configuration system with YAML
- Tool system foundation
- Context analyzer for smart response selection
- Output processor with validation
- Prompt builder with dynamic system prompts

### Core Components
- `app/core/engine.py` - Main AI Core orchestrator
- `app/core/context.py` - Context analysis
- `app/core/persona.py` - Persona selection
- `app/core/prompt.py` - Prompt building
- `app/core/output.py` - Output processing
- `app/memory/` - Memory management
- `app/model/client.py` - LLM client
- `app/api/chat.py` - REST API

### Configuration
- `app/config/persona.yaml` - Persona definitions
- `app/config/rules.yaml` - Core rules and detection
- `app/config/system.yaml` - System settings

### Documentation
- README.md with installation and usage
- TODO.md for tracking progress
- Architecture documentation in code
