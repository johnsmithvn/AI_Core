# AI CORE

Conversational AI với tính cách và nhận thức ngữ cảnh.

## 🎯 Đặc điểm

- **Tự nhiên**: Nói chuyện như người thật, có duyên, biết đùa
- **Trung thực**: Không bịa kiến thức, thừa nhận khi không biết
- **Thông minh**: Tự nhận biết ngữ cảnh để điều chỉnh giọng điệu
- **Mở rộng**: Dễ dàng thêm tools, models, và knowledge

## 🏗️ Kiến trúc

```
User Input
   ↓
Context Analyzer (phân tích ngữ cảnh)
   ↓
Persona Selector (chọn tính cách)
   ↓
Memory Loader (load lịch sử)
   ↓
Prompt Builder (xây prompt)
   ↓
Model Client (gọi LLM)
   ↓
Output Processor (xử lý output)
   ↓
Response
```

## 📦 Cài đặt

```bash
# Clone repo
git clone <repo-url>
cd ai-core

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Chạy

```bash
# Start API server
python main.py

# Server sẽ chạy tại http://localhost:8000
```

## 📡 API Endpoints

### POST /chat
Gửi tin nhắn và nhận phản hồi

```json
{
  "message": "Xin chào!",
  "session_id": "optional-session-id"
}
```

### POST /chat/new-session
Tạo session mới

### GET /chat/history/{session_id}
Lấy lịch sử chat

### DELETE /chat/session/{session_id}
Xóa session

## 🎨 Personas

- **Casual**: Thoải mái, vui vẻ, đùa giỡn
- **Technical**: Nghiêm túc, chính xác, chi tiết
- **Cautious**: Cẩn thận, thừa nhận khi không biết

AI tự động chọn persona dựa trên ngữ cảnh.

## 🛠️ Cấu hình

Chỉnh sửa file trong `app/config/`:
- `persona.yaml` - Cấu hình tính cách
- `rules.yaml` - Quy tắc xử lý
- `system.yaml` - Cấu hình hệ thống

## 🔧 Sử dụng model khác

Mặc định dùng mock model để test. Để dùng model thật:

```python
from app.model import ModelClient
from app.core import AICore

# OpenAI
model = ModelClient(
    provider="openai",
    api_key="your-key",
    model_name="gpt-4"
)

# Anthropic
model = ModelClient(
    provider="anthropic",
    api_key="your-key",
    model_name="claude-3-sonnet"
)

# Local model
model = ModelClient(
    provider="local",
    base_url="http://localhost:8080",
    model_name="llama-3-8b"
)

ai = AICore(model_client=model)
```

## 📚 Thư mục

```
ai-core/
├── app/
│   ├── api/          # FastAPI endpoints
│   ├── core/         # AI Core logic
│   ├── memory/       # Memory management
│   ├── model/        # Model clients
│   ├── tools/        # Tool system
│   └── config/       # Configuration files
├── data/             # Data storage
├── tests/            # Tests
└── main.py           # Entry point
```

## 🧪 Testing

```bash
# Test với mock model
python main.py

# Gửi request test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào!"}'
```

## 📝 License

MIT

## 🤝 Contributing

Pull requests welcome!
