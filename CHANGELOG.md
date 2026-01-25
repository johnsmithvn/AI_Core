# CHANGELOG

All notable changes to AI Core will be documented in this file.

## [Unreleased]

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
