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

## 2. Chạy với OpenAI

### Bước 1: Set API key

Tạo file `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Bước 2: Sửa `app/api/chat.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Thay dòng này:
# model_client = ModelClient(provider="mock")

# Bằng:
model_client = ModelClient(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-4"  # hoặc "gpt-3.5-turbo"
)
```

### Bước 3: Restart server (python-dotenv đã có trong requirements.txt)

```bash
python main.py
```

---

## 3. Chạy với Anthropic (Claude)

### Sửa `app/api/chat.py`:

```python
model_client = ModelClient(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model_name="claude-3-sonnet-20240229"
)
```

---

## 4. Chạy với Local Model (llama.cpp / vLLM)

### Nếu bạn có local model server chạy tại http://localhost:8080:

```python
model_client = ModelClient(
    provider="local",
    base_url="http://localhost:8080",
    model_name="llama-3-8b"
)
```

---

## 5. Test API với curl

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

## 6. Test API với Python

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

---

## 7. Sử dụng trong code

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

## 8. Tùy chỉnh Personas

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

## 9. Tùy chỉnh Context Detection

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

## 10. Thêm Tool mới

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
