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

# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Cài dependencies (trong venv)
pip install -r requirements.txt
```

**Lưu ý**: Luôn activate venv trước khi chạy:
```bash
venv\Scripts\activate  # Windows
python main.py
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

## 🔧 Chọn Model Provider

Mặc định dùng **mock model** để test. Để dùng model thật, chỉnh sửa file `.env`:

### Bước 1: Copy file config mẫu
```bash
cp .env.example .env
```

### Bước 2: Chọn provider trong `.env`

**Option 1: OpenAI (GPT-4)**
```bash
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4  # hoặc gpt-3.5-turbo
```

**Option 2: Anthropic (Claude)**
```bash
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**Option 3: Local Model (llama.cpp/vLLM/Ollama)**
```bash
MODEL_PROVIDER=local
LOCAL_MODEL_URL=http://localhost:8080
LOCAL_MODEL_NAME=llama-3-8b
```

**Option 4: Mock (default)**
```bash
MODEL_PROVIDER=mock
```

### Bước 3: Restart server
```bash
python main.py
# Log sẽ hiện: "AI Core initialized with provider: openai"
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
