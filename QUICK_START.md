# 🚀 QUICK START GUIDE

## 0. Setup Virtual Environment (Khuyến nghị)

```bash
# Tạo venv
python -m venv venv

# Kích hoạt
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài dependencies
pip install -r requirements.txt
```

**Sau này**: Luôn activate venv trước khi chạy bất kỳ lệnh nào.

---

## 1. Chạy với Mock Model (Test ngay)

```bash
# Start server
python main.py

# Server sẽ chạy tại http://localhost:8000
```

Hoặc test trực tiếp:

```bash
python test_core.py
```

---

## 2. Chọn Model Provider (OpenAI/Anthropic/Local)

### Bước 1: Copy file config mẫu

```bash
cp .env.example .env
```

### Bước 2: Edit `.env` để chọn provider

**OPTION 1: OpenAI (GPT-4)**
```bash
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4  # hoặc gpt-3.5-turbo
```

**OPTION 2: Anthropic (Claude)**
```bash
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**OPTION 3: Local Model (LM Studio/Ollama/vLLM)**
```bash
MODEL_PROVIDER=local
LOCAL_MODEL_URL=http://localhost:1234  # LM Studio
LOCAL_MODEL_NAME=mistral-7b

# Ollama: LOCAL_MODEL_URL=http://localhost:11434
# vLLM: LOCAL_MODEL_URL=http://localhost:8080
```

**Lưu ý**: Local models dùng OpenAI-compatible API (`/v1/chat/completions`)

**OPTION 4: Mock (default - no API needed)**
```bash
MODEL_PROVIDER=mock
```

### Bước 3: Restart server

```bash
python main.py
# Log sẽ hiện: "AI Core initialized with provider: openai"
```

---

## 3. Test API với curl

```bash
# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào!"}'

# New session
curl -X POST http://localhost:8000/chat/new-session

# Get history
curl http://localhost:8000/chat/history/{session_id}

# Stats
curl http://localhost:8000/admin/stats
```

---

## 4. Test API với Python

```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Xin chào!"}
)

result = response.json()
print(result["response"])
print(f"Session: {result['session_id']}")
print(f"Persona: {result['metadata']['persona']}")

# Continue conversation
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Code Python cho tôi",
        "session_id": result["session_id"]
    }
)

print(response.json()["response"])
```

---4

## 5. Sử dụng trong code

```python
import asyncio
from app.core import AICore
from app.model import ModelClient

async def main():
    # Mock model
    model = ModelClient(provider="mock")
    
    # Hoặc OpenAI
    # model = ModelClient(
    #     provider="openai",
    #     api_key="sk-...",
    #     model_name="gpt-4"
    # )
    
    ai = AICore(model_client=model)
    
    # Chat
    result = await ai.process("Xin chào!")
    print(result["response"])
    
    # Continue với session
    session_id = result["session_id"]
    result = await ai.process(
        "Giải thích cho tôi về AI",
        session_id=session_id
    )
    print(result["response"])

asyncio.run(main())
```

---

## 5. Tùy chỉnh Personas

Edit `app/config/persona.yaml`:

```yaml
personas:
  my_custom:
    name: "My Custom"
    description: "Mô tả của bạn"
    temperature: 0.7
    tone:
      - "vui vẻ"
      - "sáng tạo"
    patterns:
      - "dùng ví dụ"
      - "giải thích đơn giản"
```

Sau đó persona selector sẽ tự động detect và dùng.

---

## 6. Tùy chỉnh Context Detection

Edit `app/config/rules.yaml`:

```yaml
context_detection:
  my_context:
    keywords:
      - "từ khóa 1"
      - "từ khóa 2"
    confidence_threshold: 0.6
```

---

## 7. Thêm Tool mới

```python
# app/tools/my_tool.py
from app.tools.base import BaseTool, ToolInput, ToolOutput

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Mô tả tool của bạn"
        )
    
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        # Logic của bạn
        return ToolOutput(
            success=True,
            data={"result": "something"},
            error=None
        )

# Đăng ký trong app/api/chat.py
from app.tools.my_tool import MyTool

tool_router = ToolRouter()
tool_router.register(MyTool())
```

---

## 📚 Xem thêm

- [README.md](README.md) - Documentation đầy đủ
- [BUILD_SUMMARY.md](BUILD_SUMMARY.md) - Tổng kết build
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [TODO.md](TODO.md) - Progress tracking

---

**Happy coding! 🎉**
