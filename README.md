# AI CORE

**Flexible Conversational AI Framework** với tính cách và nhận thức ngữ cảnh.

> 🎯 **Hybrid Approach**: Framework linh hoạt - dùng external LLMs (OpenAI/Anthropic) hoặc local models (LM Studio/Ollama).

## 🎯 Đặc điểm

- **Tự nhiên**: Nói chuyện như người thật, có duyên, biết đùa
- **Trung thực**: Không bịa kiến thức, thừa nhận khi không biết
- **Thông minh**: Tự nhận biết ngữ cảnh để điều chỉnh giọng điệu
- **Mở rộng**: Dễ dàng thêm tools, models, và knowledge
- **Ổn định**: OpenAI API compliant với robust error handling

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

## 📦 Quick Setup

```bash
# Clone & setup
git clone <repo-url>
cd ai-core

# Install (see QUICK_START.md for details)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run
python main.py  # → http://localhost:8000
```

📘 **[→ Đọc QUICK_START.md](QUICK_START.md)** để biết chi tiết setup với OpenAI/Anthropic/Local models

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

## 🛠️ Configuration

### Model Providers
Mặc định: **Mock** (testing, no API key)  
Production: **OpenAI** | **Anthropic** | **Local**

```bash
# Setup trong 3 bước:
cp .env.example .env
# Edit .env → chọn provider
python main.py
```

📘 **[→ Xem QUICK_START.md](QUICK_START.md)** để config chi tiết với từng provider

### Personas & Rules
Edit config files trong `app/config/`:
- `persona.yaml` - 3 personas (Casual/Technical/Cautious)
- `rules.yaml` - Context detection rules
- `system.yaml` - System settings

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
# Quick test với mock model
python test_core.py  # → 4/4 tests pass

# Test API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào!"}'
```

📘 **[→ Xem QUICK_START.md](QUICK_START.md)** cho examples với Python, custom tools, personas

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **[QUICK_START.md](QUICK_START.md)** | Step-by-step setup guide |
| **[CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md)** | Technical deep dive |
| **[STRUCTURE.md](STRUCTURE.md)** | Project structure |
| **[CHANGELOG.md](CHANGELOG.md)** | Version history |
| **[TODO.md](TODO.md)** | Progress tracking |

---

## 📝 License

MIT

## 🤝 Contributing

Pull requests welcome!