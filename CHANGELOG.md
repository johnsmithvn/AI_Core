# CHANGELOG

All notable changes to AI Core will be documented in this file.

## [Unreleased]

## [2.1.0] - 2026-02-01

### ⚠️ BREAKING CHANGES - Response Structure (UI cần cập nhật)

#### 1. Metadata field changes
```diff
# Context analysis response
- "confidence": 0.5          # Đã deprecated
+ "signal_strength": 0.5     # Mức độ tín hiệu keyword (KHÔNG phải xác suất)
+ "context_clarity": true    # true = rõ ràng, false = conflict giữa casual/technical
+ "confidence": 0.5          # Vẫn giữ cho backward compatibility
```

#### 2. Full response metadata structure (từ /chat endpoint)
```json
{
  "response": "...",
  "session_id": "xxx",
  "metadata": {
    "persona_used": "Casual + Cautious",
    "tone": "casual",
    "behavior": "cautious",
    "context_type": "casual",
    "needs_knowledge": true,
    "signal_strength": 0.5,      // NEW: Thay thế confidence
    "context_clarity": true,     // NEW: Có conflict không
    "confidence": 0.5,           // DEPRECATED: Giữ cho backward compat
    "length": 150,
    "word_count": 25,
    "estimated_read_time": 1,
    "has_code_blocks": false
  }
}
```

### Added
- **`signal_strength`** - Mức độ tín hiệu keyword (0-1)
  - 0 = không có keyword nào match
  - 0.5 = 1 keyword match
  - 0.67 = 2 keywords match
  - **LƯU Ý**: KHÔNG phải xác suất đúng, chỉ là signal strength
  
- **`context_clarity`** - Có rõ ràng không
  - `true` = chỉ casual HOẶC technical có signal (rõ ràng)
  - `false` = cả 2 đều có signal (conflict) hoặc đều không có

- **Test automation** - 30 test cases
  - `tests/test_conversations.yaml` - 20 core tests
  - `tests/test_edge_cases.yaml` - 10 edge tests với `must_pass` / `allowed_to_fail`
  - `tests/test_automation.py` - Script tự động chạy test

### Changed
- **Score formula** (internal - không ảnh hưởng API response)
  - Cũ: `matches / total_keywords` → list keyword dài = score thấp (bug)
  - Mới: `matches / (matches + 1)` → 1 match luôn = 0.5

### Deprecated
- **`confidence`** trong metadata - Vẫn hoạt động nhưng nên dùng `signal_strength`

### Notes for UI
1. **Nên hiển thị `context_clarity`** khi debug/admin mode
2. **Không nên hiển thị `signal_strength`** cho end-user (dễ hiểu nhầm là "độ chắc chắn")
3. **Backward compatible** - `confidence` vẫn có trong response

---

## [2.0.0] - 2026-02-01

### Added - **Tone + Behavior Architecture** (NEW)
- **Tách biệt Tone và Behavior** thay vì chọn 1 persona cứng
  - `tone`: casual | technical (cách nói - quyết định bởi context_type)
  - `behavior`: normal | cautious (hành vi - quyết định bởi needs_knowledge)
  - 4 combinations: casual+normal, casual+cautious, technical+normal, technical+cautious
  
- **Vui vẻ NHƯNG không bịa** - kết hợp tone casual với behavior cautious
  - Trước: "Tôi không có thông tin cụ thể..." (đúng nhưng khô khan)
  - Sau: "Ôi gu bạn chất đấy! 😄 Nói thật mình không rành, thử hỏi thư viện đi!"

### Changed
- **persona.yaml** - Cấu trúc mới với `tones:` và `behaviors:` sections
- **PersonaSelector** - `select()` build persona động từ tone_config + behavior_config
- **OutputProcessor** - Metadata mới: `tone`, `behavior` thay vì `response_mode`
- **rules.yaml** - Thêm keywords technical, giảm threshold need_knowledge xuống 0.1

### Improved
- Tự nhiên hơn khi AI không biết nhưng vẫn vui vẻ
- Flexible persona system cho future extensions
- Legacy support cho code cũ (personas section vẫn hoạt động)

### Notes
- `temperature` chỉ lấy từ tone (đúng về bản chất - temperature = style)

---

## [1.2.0] - 2026-02-01

### Changed - **Length Management Philosophy** (BREAKING: Behavioral change)
- ❌ **REMOVED hard truncate after generation** (anti-pattern cho local AI)
  - Cắt text sau khi model generate = vô nghĩa (đã tốn tài nguyên)
  - `max_length: null` in `rules.yaml` - không giới hạn
  
- ✅ **NEW: Content description, not control**
  - `output.py` giờ chỉ **mô tả content** qua metadata
  - Added: `word_count`, `estimated_read_time`, `has_code_blocks`
  - Length validation → behavior warnings (không cắt text)
  
- ✅ **NEW: Context-aware length behavior validation**
  - Casual chat dài >3000 chars → warning
  - Cautious + dài + certainty → suspicious
  - Low confidence + very long → warning
  - **Philosophy**: Validate behavior, not truncate output

- ✅ **NEW: AI self-managed response length**
  - Updated `BASE_SYSTEM_PROMPT` với length management guideline
  - AI có thể tóm tắt trước, hỏi user muốn chi tiết không
  - Response >500 từ → chia nhỏ hoặc hỏi user
  - Giống cách người thật nói chuyện

### Fixed - **Semantic Corrections**
- **`context_type` vs `response_mode` separation** (context.py)
  - `context_type`: casual | technical (what user is asking)
  - `response_mode`: casual | technical | cautious (how AI responds)
  - Before: `cautious` was mixed with `need_knowledge` → semantic error
  
- **User message `persona=None`** (engine.py)
  - User messages don't have persona, only assistant messages do
  - Before: `persona=persona["name"]` for user → incorrect schema

### Improved
- **Separation of concerns**: AI Core mô tả, UI quyết định hiển thị
- Better metadata cho frontend: read time, word count, response_mode
- More natural conversation flow
- Cleaner semantic model

## [1.1.3] - 2026-01-25

### Added
- **Dynamic server configuration** via environment variables
  - `API_HOST` - Configure listen address (default: 0.0.0.0)
  - `API_PORT` - Configure port (default: 8000)
  - `API_RELOAD` - Enable auto-reload for development (default: false)
- **Complete API Documentation** - Created `docs/API_REFERENCE.md`
  - 7 endpoints fully documented với examples
  - Request/response schemas
  - curl, Python, JavaScript examples
  - Status codes và error handling
- Improved startup logging với configuration display

### Changed
- `main.py` now reads config from `.env` file
- More flexible deployment (Docker, cloud, local)
- Documentation structure improved

### Fixed
- Hard-coded port 8000 → Now configurable
- Missing API documentation

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
