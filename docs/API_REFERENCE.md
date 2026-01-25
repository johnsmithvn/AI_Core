# 🔌 API REFERENCE

**Base URL**: `http://localhost:8000` (configurable via `API_PORT` in `.env`)  
**Format**: JSON  
**Version**: 1.1.3  
**Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)

---

## 📡 ENDPOINTS OVERVIEW

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Main chat endpoint |
| POST | `/chat/new-session` | Create new session |
| GET | `/chat/history/{session_id}` | Get conversation history |
| DELETE | `/chat/session/{session_id}` | Delete session |
| POST | `/admin/cleanup` | Cleanup old data |
| GET | `/admin/stats` | Get system statistics |
| GET | `/` | Health check |

---

## 1. POST /chat - Main Chat

**Mô tả**: Gửi tin nhắn và nhận phản hồi từ AI Core với personality tự động

### Request

```json
{
  "message": "Xin chào!",
  "session_id": "optional-uuid"  // Nếu không có, tạo session mới
}
```

**Fields**:
- `message` (string, required): User message
- `session_id` (string, optional): UUID của session. Nếu null → tạo mới

### Response

```json
{
  "response": "Chào bạn! Mình là AI Core, một conversational AI với tính cách...",
  "session_id": "4b8af747-4357-44f3-9473-ebf69a1bf269",
  "metadata": {
    "persona": "casual",
    "context": {
      "context_type": "casual_chat",
      "confidence": 0.85
    },
    "valid": true,
    "warnings": [],
    "model": "google/gemma-3-12b",
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 80,
      "total_tokens": 230
    },
    "timestamp": "2026-01-25T16:30:00Z"
  }
}
```

**Metadata Fields**:
- `persona`: Tính cách được chọn (casual/technical/cautious)
- `context.context_type`: Loại ngữ cảnh (casual_chat/technical_question/knowledge_query)
- `context.confidence`: Độ tin cậy context detection (0.0-1.0)
- `valid`: Output có pass validation không
- `warnings`: Cảnh báo nếu có (empty array nếu ok)
- `model`: Model name được dùng
- `usage`: Token usage stats

### Examples

**curl**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Xin chào!"
  }'
```

**Python**:
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/chat",
        json={"message": "Xin chào!"}
    )
    data = response.json()
    print(f"AI: {data['response']}")
    print(f"Session: {data['session_id']}")
    print(f"Persona: {data['metadata']['persona']}")
```

**JavaScript/TypeScript**:
```typescript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'Xin chào!'})
});

const data = await response.json();
console.log('AI:', data.response);
console.log('Persona:', data.metadata.persona);
```

### Status Codes

- `200` - Success
- `400` - Bad Request (invalid message)
- `500` - Internal Server Error (model error)
- `503` - Service Unavailable (model not loaded)

---

## 2. POST /chat/new-session - Tạo Session Mới

**Mô tả**: Tạo session mới và trả về session ID. Dùng khi muốn bắt đầu conversation mới.

### Request

Empty body hoặc `{}`

### Response

```json
{
  "session_id": "8f7e2a91-3b5c-4d6e-9f0a-1b2c3d4e5f6a",
  "created_at": "2026-01-25T16:30:00Z",
  "message": "New session created"
}
```

### Examples

**curl**:
```bash
curl -X POST http://localhost:8000/chat/new-session
```

**Python**:
```python
response = await client.post("http://localhost:8000/chat/new-session")
session_data = response.json()
session_id = session_data['session_id']
```

### Status Codes

- `200` - Success

---

## 3. GET /chat/history/{session_id} - Lấy Lịch Sử

**Mô tả**: Lấy toàn bộ lịch sử chat của 1 session

### Parameters

- `session_id` (path, required): UUID của session
- `limit` (query, optional): Giới hạn số messages (default: 20)

### Response

```json
{
  "session_id": "4b8af747-4357-44f3-9473-ebf69a1bf269",
  "messages": [
    {
      "role": "user",
      "content": "Xin chào!",
      "timestamp": "2026-01-25T16:30:00Z",
      "persona": null
    },
    {
      "role": "assistant",
      "content": "Chào bạn! Mình là AI Core...",
      "timestamp": "2026-01-25T16:30:05Z",
      "persona": "casual"
    },
    {
      "role": "user",
      "content": "Giải thích async/await cho tôi",
      "timestamp": "2026-01-25T16:31:00Z",
      "persona": null
    },
    {
      "role": "assistant",
      "content": "Async/await là cơ chế...",
      "timestamp": "2026-01-25T16:31:10Z",
      "persona": "technical"
    }
  ],
  "total_messages": 4,
  "context": {
    "last_context_type": "technical_question",
    "last_confidence": 0.92
  }
}
```

### Examples

**curl**:
```bash
# Default (20 messages)
curl http://localhost:8000/chat/history/4b8af747-4357-44f3-9473-ebf69a1bf269

# Custom limit
curl http://localhost:8000/chat/history/4b8af747-4357-44f3-9473-ebf69a1bf269?limit=10
```

**Python**:
```python
session_id = "4b8af747-4357-44f3-9473-ebf69a1bf269"
response = await client.get(f"http://localhost:8000/chat/history/{session_id}?limit=10")
history = response.json()

for msg in history['messages']:
    print(f"{msg['role']}: {msg['content']}")
```

### Status Codes

- `200` - Success
- `404` - Session not found

---

## 4. DELETE /chat/session/{session_id} - Xóa Session

**Mô tả**: Xóa session và toàn bộ messages trong memory

### Parameters

- `session_id` (path, required): UUID của session

### Response

```json
{
  "status": "deleted",
  "session_id": "4b8af747-4357-44f3-9473-ebf69a1bf269",
  "deleted_messages": 15,
  "message": "Session and 15 messages deleted"
}
```

### Examples

**curl**:
```bash
curl -X DELETE http://localhost:8000/chat/session/4b8af747-4357-44f3-9473-ebf69a1bf269
```

**Python**:
```python
session_id = "4b8af747-4357-44f3-9473-ebf69a1bf269"
response = await client.delete(f"http://localhost:8000/chat/session/{session_id}")
print(response.json())
```

### Status Codes

- `200` - Success
- `404` - Session not found

---

## 5. POST /admin/cleanup - Dọn Dẹp Database

**Mô tả**: Xóa sessions và messages cũ hơn N ngày khỏi long-term memory (SQLite)

### Request

```json
{
  "days": 30  // Optional, default: 30
}
```

### Response

```json
{
  "status": "cleanup_complete",
  "deleted_sessions": 25,
  "deleted_messages": 850,
  "cutoff_date": "2025-12-26T00:00:00Z",
  "database_size_mb_before": 45.2,
  "database_size_mb_after": 15.8
}
```

### Examples

**curl**:
```bash
# Default (30 days)
curl -X POST http://localhost:8000/admin/cleanup

# Custom (7 days)
curl -X POST http://localhost:8000/admin/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

**Python**:
```python
# Cleanup data older than 7 days
response = await client.post(
    "http://localhost:8000/admin/cleanup",
    json={"days": 7}
)
result = response.json()
print(f"Deleted {result['deleted_sessions']} sessions")
print(f"Deleted {result['deleted_messages']} messages")
```

### Status Codes

- `200` - Success
- `400` - Invalid days parameter

---

## 6. GET /admin/stats - Thống Kê Hệ Thống

**Mô tả**: Lấy statistics về sessions, messages, personas usage

### Response

```json
{
  "total_sessions": 120,
  "active_sessions": 45,
  "total_messages": 3200,
  "messages_last_24h": 450,
  "persona_usage": {
    "casual": 1800,
    "technical": 1100,
    "cautious": 300
  },
  "context_distribution": {
    "casual_chat": 1600,
    "technical_question": 1200,
    "knowledge_query": 400
  },
  "avg_messages_per_session": 26.67,
  "avg_session_duration_minutes": 45.5,
  "database_size_mb": 18.7,
  "model_provider": "local",
  "model_name": "google/gemma-3-12b",
  "uptime_seconds": 3600,
  "timestamp": "2026-01-25T16:30:00Z"
}
```

### Examples

**curl**:
```bash
curl http://localhost:8000/admin/stats
```

**Python**:
```python
response = await client.get("http://localhost:8000/admin/stats")
stats = response.json()

print(f"Total sessions: {stats['total_sessions']}")
print(f"Active sessions: {stats['active_sessions']}")
print(f"Most used persona: {max(stats['persona_usage'], key=stats['persona_usage'].get)}")
```

### Status Codes

- `200` - Success

---

## 7. GET / - Health Check

**Mô tả**: Kiểm tra server có chạy không

### Response

```json
{
  "status": "ok",
  "service": "AI Core API",
  "version": "1.1.3",
  "model_provider": "local",
  "timestamp": "2026-01-25T16:30:00Z"
}
```

### Examples

**curl**:
```bash
curl http://localhost:8000/
```

**Python**:
```python
response = await client.get("http://localhost:8000/")
if response.json()['status'] == 'ok':
    print("Server is running!")
```

### Status Codes

- `200` - Server is healthy

---

## 🔐 AUTHENTICATION

**Hiện tại**: Không có authentication (local development)  
**Production**: Khuyến nghị thêm:
- API Key authentication
- OAuth2
- Rate limiting
- IP whitelisting

---

## 📊 STATUS CODES

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request (invalid input) |
| `404` | Not Found (session/resource not found) |
| `500` | Internal Server Error |
| `503` | Service Unavailable (model not loaded/connection failed) |

---

## ⚠️ ERROR RESPONSES

All errors follow this format:

```json
{
  "detail": "Error message here",
  "status_code": 400,
  "timestamp": "2026-01-25T16:30:00Z"
}
```

**Common Errors**:

1. **Invalid message**:
```json
{
  "detail": "Message is required and cannot be empty",
  "status_code": 400
}
```

2. **Session not found**:
```json
{
  "detail": "Session 4b8af747-4357-44f3-9473-ebf69a1bf269 not found",
  "status_code": 404
}
```

3. **Model not loaded**:
```json
{
  "detail": "Local model timeout after 60s - model may not be loaded",
  "status_code": 503
}
```

4. **Connection error**:
```json
{
  "detail": "Cannot connect to http://127.0.0.1:1234 - is the server running?",
  "status_code": 503
}
```

---

## 🧪 TESTING

### Interactive API Docs (Swagger)

```
http://localhost:8000/docs
```

- Tự động generate từ FastAPI
- Test endpoints trực tiếp trong browser
- Xem request/response schemas
- Copy curl commands

### Postman Collection

Import base URL: `http://localhost:8000`

**Pre-request script** (optional):
```javascript
// Auto-generate session_id
if (!pm.environment.get("session_id")) {
    pm.environment.set("session_id", pm.variables.replaceIn('{{$randomUUID}}'));
}
```

### Python Test Client

```python
import asyncio
import httpx

async def test_full_conversation():
    async with httpx.AsyncClient() as client:
        # Create new session
        session_resp = await client.post("http://localhost:8000/chat/new-session")
        session_id = session_resp.json()['session_id']
        
        # Chat
        messages = [
            "Xin chào!",
            "Giải thích async/await trong Python",
            "Bạn có biết sách 'Clean Code' không?"
        ]
        
        for msg in messages:
            response = await client.post(
                "http://localhost:8000/chat",
                json={"message": msg, "session_id": session_id}
            )
            data = response.json()
            print(f"\nUser: {msg}")
            print(f"AI ({data['metadata']['persona']}): {data['response']}")
        
        # Get history
        history = await client.get(f"http://localhost:8000/chat/history/{session_id}")
        print(f"\n\nTotal messages: {history.json()['total_messages']}")
        
        # Delete session
        await client.delete(f"http://localhost:8000/chat/session/{session_id}")
        print("Session cleaned up")

asyncio.run(test_full_conversation())
```

---

## 🔧 CONFIGURATION

### Server Configuration (`.env`)

```bash
# Server settings
API_HOST=0.0.0.0      # 0.0.0.0 = all interfaces, 127.0.0.1 = localhost only
API_PORT=8000          # Custom port
API_RELOAD=true        # Auto-reload on code change

# Model provider
MODEL_PROVIDER=local   # mock | openai | anthropic | local
LOCAL_MODEL_URL=http://127.0.0.1:1234  # LM Studio
LOCAL_MODEL_NAME=google/gemma-3-12b
```

### Run with custom config

```bash
# Custom port
API_PORT=9000 python main.py

# Production mode (no reload)
API_RELOAD=false python main.py

# Localhost only
API_HOST=127.0.0.1 python main.py
```

---

## 📝 NOTES

### Session Management
- Sessions auto-created nếu không truyền `session_id`
- Sessions persist trong short-term memory (in-memory, 1 hour)
- Messages persist trong long-term memory (SQLite, vĩnh viễn)
- Cleanup old data với `/admin/cleanup`

### Context Detection
- AI tự động analyze ngữ cảnh (casual/technical/cautious)
- Confidence score 0.0-1.0
- Context thay đổi dynamic trong conversation

### Persona Selection
- 3 personas: casual, technical, cautious
- Auto-selected based on context
- Temperature: casual (0.8), technical (0.3), cautious (0.5)

### Rate Limiting
- **Chưa implement** - cần thêm cho production
- Khuyến nghị: 60 requests/minute per IP

### Model Support
- **Mock**: Testing, no API needed
- **OpenAI**: GPT-3.5, GPT-4 (cloud)
- **Anthropic**: Claude (cloud)
- **Local**: LM Studio, Ollama, vLLM, llama.cpp (local)

---

## 🔗 RELATED DOCS

- [README.md](../README.md) - Project overview
- [QUICK_START.md](../QUICK_START.md) - Setup guide
- [CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md) - Technical deep dive
- [STRUCTURE.md](STRUCTURE.md) - Project structure
- [TODO.md](TODO.md) - Progress tracking
- [CHANGELOG.md](../CHANGELOG.md) - Version history

---

## 🆘 TROUBLESHOOTING

### "Connection refused" error

```bash
# Check if server is running
curl http://localhost:8000/

# Check logs
tail -f data/app.log
```

### "Model not loaded" error (Local)

1. Check LM Studio is running
2. Load model in LM Studio UI
3. Verify URL in `.env`: `LOCAL_MODEL_URL=http://127.0.0.1:1234`

### "Session not found" error

- Session ID invalid hoặc đã bị delete
- Create new session với `/chat/new-session`

### Slow responses

- Local models chậm hơn cloud (30-60s)
- Check model size (smaller = faster)
- Check GPU/CPU usage

---

**Version**: 1.1.3  
**Last Updated**: 2026-01-25  
**Maintained by**: AI Core Team
